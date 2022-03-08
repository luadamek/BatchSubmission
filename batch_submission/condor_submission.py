from batch_submission.batch_submission import AbstractBatchSubmission, do_multiple_subprocess_attempts
import os

def get_jobid_from_submission(long_info):
    """
    Parameters
    ----------
        The byte-string returned by submitting a job to the slurm system

    Returns
    -------
        int
            The jobid of the submission.
    """
    raise ValuError("Not yet implemented")
    return job_id


def parse_queue_output(long_info):
    """
    Parameters
    ----------
        The byte-string returned by querying the slurm system for the currently running jobs.

    Returns
    -------
        set of int
            The jobids of the currenty submitted and running jobs on the slurm batch system.
    """
    raise ValuError("Not yet implemented")
    return job_ids

class CondorSubmission(AbstractBatchSubmission):
    def get_job_queue(self):
        """
        Get the queue of jobs currently submitted to the batch system by the user

        Parameters
        ----------

        Returns
        -------
            set of {int}
                A set of jobids for all jobs currently running
        """
        long_info = do_multiple_subprocess_attempts(["squeue", "-u", os.getenv("USER")])
        job_ids = parse_queue_output(long_info)
        return job_ids

    def _submit(self):
        """
        Submit the job to the batch system, and return the jobid for book keeping.

        Parameters
        ----------

        Returns
        -------
            int
                The jobid of the submission.
        """
        raise ValuError("Not yet implemented")
        return jobid

    def get_submission_command(self):
        """
        Create the shell command to submit this job.

        Parameters
        ----------

        Returns
        -------
            list of str
                The submission command
        """
        raise ValuError("Not yet implemented")
        return submission_command

AbstractBatchSubmission.register(CondorSubmission)
