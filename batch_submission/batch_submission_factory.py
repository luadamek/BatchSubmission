from batch_submission.slurm_submission import SlurmSubmission
from batch_submission.condor_submission import CondorSubmission
from batch_submission.batch_submission import AbstractBatchSubmission
import subprocess

def check_for_command(command):
    """
    Check if the command can be successfully executed.

    Parameters
    ----------
        list of str
            List of string representing the command to be executed. E.g. ["ls", "-al"] is equivalent to "ls -al".

    Returns
    -------
        bool
            True if the command was successfully executed.
    """
    for i in range(0, 3):
        try:
            output = subprocess.check_output(command)
            return True
        except Exception as e:
            if i == 2:
                print("comand \"{}\" failed".format(" ".join(command)))
                print(e)
    return False

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
        "longlunch",\
        "tomorrow",\
        "testmatch",\
        "nextweek",\
        ]

def check_if_condor_time(time):
    return time in TIME_TRANSLATION_CONDOR_TO_SLURM

def check_if_slurm_time(time):
    split = time.split(":")
    if not len(split) == 3: return False
    raw_time = []
    for el in split:
        try: int(el)
        except Exception as e:
            return False
    return True

def get_raw_time_from_slurm_time(time):
    if not check_if_slurm_time(time): return None
    raw_time = [int(el) for el in time.split(":")]
    return raw_time

def greater_than(time1, time2):
    for el1, el2 in zip(time1, time2):
        if el1 < el2: return False
    return True

def time_translation_slurm_to_condor(time):
    raw_time = get_raw_time_from_slurm_time(time)
    if raw_time is None: return None

    for condor_time in ORDERED_CONDOR_TIMES:
        condor_raw_time = get_raw_time_from_slurm_time(TIME_TRANSLATION_CONDOR_TO_SLURM[condor_time])
        if greater_than(condor_raw_time, raw_time):
            return condor_time

    return condor_time

def time_translation_condor_to_slurm(time):
    if not check_if_condor_time(time):
        raise ValueError("{} is not a valid queue for condor")
    return TIME_TRANSLATION_CONDOR_TO_SLURM[time]

class BatchSubmissionFactory:
    """
    A factory for the creation of an AbstractBachSubmission object.
    All arguments (args and kwargs) will be forwarded to the creation of a AbstractBatchSubmission object.
    """

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        supported = {"slurm", "condor"}

    def translate_parameters(self, kind):
        all_argnames = AbstractBatchSubmission.__init__.__code__.co_varnames
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
            
            if not check_if_slurm_time(self.args[time_index]):
                raise ValueError("{} is not avalid time for SLURM".format(self.args[time_index]))

            #translate the memory parameters
            #TBD


    def get_batch_job(self):
        global BATCH_SYSTEM
        condor_q = ["which", "condor_q"]
        slurm_q = ["which", "squeue"]

        if BATCH_SYSTEM == "condor" or (BATCH_SYSTEM is None and check_for_command(condor_q)):
            if BATCH_SYSTEM is None: print("Found condor installed. Using condor.")
            BATCH_SYSTEM = "condor"
            self.translate_parameters("slurm")
            return CondorSubmission(*self.args, **self.kwargs)

        if BATCH_SYSTEM == "slurm" or (BATCH_SYSTEM is None and check_for_command(slurm_q)):
            if BATCH_SYSTEM is None: print("Found slurm installed. Using slurm.")
            BATCH_SYSTEM = "slurm"
            self.translate_parameters("condor")
            return SlurmSubmission(*self.args, **self.kwargs)

        else:
            raise ValueError("None of the supported batch submission systems, condor or slurm,  were found")
