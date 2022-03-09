from batch_submission.slurm_submission import SlurmSubmission
from batch_submission.condor_submission import CondorSubmission
from batch_submission.batch_submission import AbstractBatchSubmission
from utils import check_for_command

BATCH_SYSTEM = None

TIME_TRANSLATION_CONDOR_TO_SLURM=\
{\
"espresso"    :"00:00:20",
"microcentury":"00:01:00",
"longlunch"   :"00:02:00",
"workday"     :"00:08:00",
"tomorrow"    :"01:00:00",
"testmatch"   :"03:00:00",
"nextweek"    :"07:00:00",
}

ORDERED_CONDOR_TIMES = [\
        "espresso",\
        "microcentury",\
        "longlunch",\
        "workday",\
        "tomorrow",\
        "testmatch",\
        "nextweek",\
        ]

def check_if_condor_time(time):
    """ Check if the string time is a valid condor time, as listed in the keys of TIME_TRANSLATION_CONDOR_TO_SLURM."""
    return time in TIME_TRANSLATION_CONDOR_TO_SLURM

def check_if_slurm_time(time):
    """ Check if th etime is a valid slurm time. I.e. three integers separated by colons, in the form XX:XX:XX."""
    split = time.split(":")
    if not len(split) == 3: return False
    if not all(len(el) == 2 for el in split): return False
    raw_time = []
    for el in split:
        try: int(el)
        except Exception as e:
            return False
    return True

def get_raw_time_from_slurm_time(time):
    """Return a list of three integers representing the day, hour and minutes of the slurm submission time string of the form XX:XX:XX."""
    if not check_if_slurm_time(time): return None
    raw_time = [int(el) for el in time.split(":")]
    return raw_time

def greater_than_equal(time1, time2):
    """Return True of time1 is longer than time 2. time1 and time2 are integer lists of times, E.g. [days, minutes, seconds]"""
    for el1, el2 in zip(time1, time2):
        if el1 > el2: return True
        elif el1 < el2: return False
        else: continue
    return True

def time_translation_slurm_to_condor(time):
    """Return the shortest possible condor time that is longer than the input parameter time (a slurm time string of the form XX:XX:XX"""
    raw_time = get_raw_time_from_slurm_time(time)
    if raw_time is None: return None

    for condor_time in ORDERED_CONDOR_TIMES:
        condor_raw_time = get_raw_time_from_slurm_time(TIME_TRANSLATION_CONDOR_TO_SLURM[condor_time])
        if greater_than_equal(condor_raw_time, raw_time):
            return condor_time

    return condor_time

def time_translation_condor_to_slurm(time):
    """Translate a condor time string (e.g. workday) to a slurm time string of the form XX:XX:XX"""
    if not check_if_condor_time(time):
        raise ValueError("{} is not a valid queue for condor")
    return TIME_TRANSLATION_CONDOR_TO_SLURM[time]

class BatchSubmissionFactory:
    """
    A factory for the creation of an object of a class that inherits from AbstractBachSubmission.
    All arguments (args and kwargs) will be forwarded to the creation of the AbstractBatchSubmission object.

    Attributes
    ----------
        args
            tuple
                Arguments to be passed to the construction of an instance of an AbstractBatchSubmission derived class.

        kwargs
            dict
                Keyworkd arguments to be passed to the construction of an instance of an AbstractBatchSubmission derived class.

        supported
            set of str
                The names of the batch submission systems that this factory supports.

    Methods
    -------
        translate_parameters
            Convert the arguments to the necessary batch submission system.

    """

    def __init__(self, *args, **kwargs):
        self.args = list(args)
        self.kwargs = kwargs
        self.supported = {"slurm", "condor"}

    def translate_parameters(self, kind):
        """
        Translate the parameters to the appropriate batch submission engine.
        For example, if the time is "00:00:20", but the submission system is condor,
        then convert this argument to "espresso".

        Arguments
        ---------
            kind
                string
                    Name of batch submission system. Must be in self.supported.
        """
        all_argnames = AbstractBatchSubmission.__init__.__code__.co_varnames # the parameters of the __init__ of the abstract base submission class.
        argnames = all_argnames[1:len(self.args) + 1]
        kw_argnames = all_argnames[len(self.args) + 1:]

        if kind == "slurm":

            #translate the time parameters
            time_index = argnames.index("time")
            if check_if_condor_time(self.args[time_index]):
                self.args[time_index] = time_translation_condor_to_slurm(self.args[time_index])

            if not check_if_slurm_time(self.args[time_index]):
                raise ValueError("{} is not avalid time for SLURM".format(self.args[time_index]))

            #translate the memory parameters
            #TBD


        elif kind == "condor":

            #translate the time parameters
            time_index = argnames.index("time")
            if check_if_slurm_time(self.args[time_index]):
                self.args[time_index] = time_translation_slurm_to_condor(self.args[time_index])

            if not check_if_condor_time(self.args[time_index]):
                raise ValueError("{} is not avalid time for SLURM".format(self.args[time_index]))

            #translate the memory parameters
            #TBD


    def get_batch_job(self):
        """
        Return an instance of a class with the interface defined in AbstractBatchSubmission.
        This function should find out if condor, slurm or another batch submission software is available,
        and return an object that will submit jobs to it.

        Arguments
        ---------

        Returns
        -------
            An instance of a class that follows the AbstractBatchSubmission interface.
        """

        global BATCH_SYSTEM
        condor_q = ["which", "condor_q"]
        slurm_q = ["which", "squeue"]

        if BATCH_SYSTEM == "condor" or (BATCH_SYSTEM is None and check_for_command(condor_q)):
            if BATCH_SYSTEM is None: print("Found condor installed. Using condor.")
            BATCH_SYSTEM = "condor"
            self.translate_parameters("condor")
            return CondorSubmission(*self.args, **self.kwargs)

        if BATCH_SYSTEM == "slurm" or (BATCH_SYSTEM is None and check_for_command(slurm_q)):
            if BATCH_SYSTEM is None: print("Found slurm installed. Using slurm.")
            BATCH_SYSTEM = "slurm"
            self.translate_parameters("slurm")
            return SlurmSubmission(*self.args, **self.kwargs)

        else:
            raise ValueError("None of the supported batch submission systems, condor or slurm,  were found")
