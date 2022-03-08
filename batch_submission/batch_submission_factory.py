from batch_submission.slurm_submission import SlurmSubmission
from batch_submission.condor_submission import CondorSubmission
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

class BatchSubmissionFactory:
    """
    A factory for the creation of an AbstractBachSubmission object.
    All arguments (args and kwargs) will be forwarded to the creation of a AbstractBatchSubmission object.
    """

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        supported = {"slurm", "condor"}

    #def translate_parameters(self, args, kwargs, kind):
    #    assert kind in supported
    #    argnames = inspect.getfullargspec(AbstractBatchSubmission.__init__).args

    def get_batch_job(self):
        global BATCH_SYSTEM
        condor_q = ["which", "condor_q"]
        slurm_q = ["which", "squeue"]

        if BATCH_SYSTEM == "condor" or (BATCH_SYSTEM is None and check_for_command(condor_q)):
            if BATCH_SYSTEM is None: print("Found condor installed. Using condor.")
            BATCH_SYSTEM = "condor"
            #self.args, self.kwargs = translate_parameters(self, self.args, self.kwargs, kind = "slurm")
            return CondorSubmission(*self.args, **self.kwargs)

        if BATCH_SYSTEM == "slurm" or (BATCH_SYSTEM is None and check_for_command(slurm_q)):
            if BATCH_SYSTEM is None: print("Found slurm installed. Using slurm.")
            BATCH_SYSTEM = "slurm"
            #self.args, self.kwargs = translate_parameters(self, self.args, self.kwargs, kind = "condor")
            return SlurmSubmission(*self.args, **self.kwargs)

        else:
            raise ValueError("None of the supported batch submission systems, condor or slurm,  were found")
