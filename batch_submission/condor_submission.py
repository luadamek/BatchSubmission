from batch_submission.batch_submission import AbstractBatchSubmission, do_multiple_subprocess_attempts
import os


def get_jobid_from_submission(submission):
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


def parse_queue_output(jobqueue):
    """
    Parameters
    ----------
        list of ClassAd
            the list of ClassAds returned by htcondor.Schedd().query().

    Returns
    -------
        set of int
            The jobids of the currenty submitted and running jobs on the slurm batch system.
    """
    import htcondor
    job_ids = set()
    for el in jobqueue:
        job_status = el["JobStatus"]
        running = (job_status == htcondor.JobStatus.RUNNING) or (job_status == htcondor.JobStatus.IDLE)
        if running:
            job_ids.add(el["ClusterId"])

    return job_ids

schedd = None
def get_schedd():
    """
    Only import the scheduler for htcondor if it is available. Avoids problems when it is not
    """
    global schedd
    if schedd is None:
        import htcondor
        schedd = htcondor.Schedd()
    return schedd

class CondorSubmission(AbstractBatchSubmission):
    def get_job_queue(self):
        """
        Get the queue of jobs currently running to the batch system by the user

        Parameters
        ----------

        Returns
        -------
            set of {int}
                A set of jobids for all jobs currently running
        """
        long_info = get_schedd().query(constraint="OWNER == \"{}\"".format(os.getenv("USER")), projection=["ClusterId", "JobStatus"])
        job_ids =  parse_queue_output(long_info)
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
        import htcondor
        logfile = self.output.replace(".out", ".log")

        for fname in [logfile, self.output, self.error]:
            with open(fname, "w") as f:
                pass
            os.system("chmod 777 {}".format(fname))

        os.system("chmod 777 {}".format(self.job_directory))
        
        submission = htcondor.Submit({\
            "Universe": "vanilla",\
            "Executable": self.script,\
            "request_memory": self.memory,\
            "request_cpus": 1,\
            "Error": self.error,\
            "Output": self.output,\
            "Log": logfile,\
            "should_transfer_files": "NO",\
            "+JobFlavour": self.time,
        })

        sub_file = self.output.replace(".out", ".sub")
        with open(sub_file, "w") as f:
            f.write(str(submission))
            f.write("\nqueue")

        long_info = do_multiple_subprocess_attempts(["condor_submit", sub_file])
        os.system("rm {}".format(sub_file))
        #get_schedd().submit(submission) has permission issues. I don't know why...

        info = long_info.decode("utf-8")
        info = info.strip("\n")
        info = info.strip(" ")
        info = info.strip("\n")
        info = info.split(" ")[-1]
        info = info.strip(".")
        jobid = int(info)
        return jobid


AbstractBatchSubmission.register(CondorSubmission)
