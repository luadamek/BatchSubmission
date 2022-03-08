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
    long_info = long_info.decode("utf-8")
    long_info = long_info.rstrip("\n")
    long_info = long_info.strip(" ")
    job_id = int(long_info.split(" ")[-1])
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
    long_info = long_info.decode("utf-8")
    long_info = long_info.rstrip("\n")
    lines = long_info.split("\n")
    if len(lines) < 2: return {}
    lines = lines[1:] #remove the header line
    lines = [l.strip() for l in lines]
    job_ids = {int(l.split(" ")[0]) for l in lines}
    return job_ids

class SlurmSubmission(AbstractBatchSubmission):
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
        submission_command = self.get_submission_command()
        long_info = do_multiple_subprocess_attempts(submission_command)
        jobid = get_jobid_from_submission(long_info)
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
        submission_command = ["sbatch"]
        submission_command.append("--mem={}".format(self.memory))
        submission_command.append("--time={}".format(self.time))
        submission_command.append("--output={}".format(self.output))
        submission_command.append("--error={}".format(self.error))
        submission_command.append(self.script)

        return submission_command

AbstractBatchSubmission.register(SlurmSubmission)
