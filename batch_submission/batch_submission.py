from abc import ABC, abstractmethod 
import os
import random

import subprocess


#sometimes the slurm batch system fails when queried often, so provide a protection by trying to query it multiple times
def do_multiple_subprocess_attempts(command):
    """
    Execute the the terminal command. If it fails, try it up to ten times. Occasionally, the slurm system will fail, if queried often.
    Multiple attmepts account for these failures.

    Parameters
    ----------
        command : list of str
            The command to be executed, where each element is separated by a space. E.G. ls directory would be represented by ["ls", "directory"].

    Returns
    -------
        str
            The output as printed on the terminal screen after the command was executed.

    """
    for i in range(0, 10):
        try:
           result = subprocess.check_output(command)
        except Exception as e:
           if i != 9: continue
           else: raise(e)
        break
    return result

class BatchSubmissionSet:
    """
    A class to aggregate objects of type AbstractBatchSubmission, and check their collective status. This class checks for failed jobs
    and handles their resubmission.

    Attributes
    ----------
        jobs : list of AbstractBatchSubmission
            The set of AbstractBatchSubmissions to monitor for completion and submission.

    Methods
    -------
        check_completion
            Return True if all jobs are not running and finished.
        submit
            Submit all jobs to the batch system.
        get_failed_jobs
            Return the list of failed jobs.
        resubmit_jobs
            Resubmit all failed jobs.
        test_job_locally
            Run a job locally.
    """

    def __init__(self, jobs):
        """
        Initialize a BatchSubmissionSet.

        Attributes
        ----------
            jobs : list of AbstractBatchSubmission
                The set of AbstractBatchSubmissions to monitor for completion and submission.

        Returns
        -------
            None

        Raises
        ------
            TypeError if not all of elements of jobs are of type AbstractBatchSubmission
        """


        for el in jobs:
            if not type(el) == AbstractBatchSubmission:
                raise TypeError("All elements of jobs must be of type AbstractBatchSubmission")

        self.jobs = jobs

    def check_completion(self):
        """
        Return True if all jobs are not running and finished
        """
        if len(jobs) == 0: return True

        first_job = jobs[0]
        queue = first_job.get_job_queue()

        for job in self.jobs:

            running = job.check_running(job_queue = queue)
            if running:
                return False

            finished = job.check_finished()
            if not finishd:
                return False

        return True

    def submit(self):
        """
        Submit all jobs to the batch system
        """
        first_job = jobs[0]
        queue = first_job.get_job_queue()

        for job in self.jobs:
            running = job.check_running(job_queue = queue)
            if running:
                continue

            job.submit()

    def get_failed_jobs(self):
        """
        Return the list of failed jobs
        """
        first_job = jobs[0]
        queue = first_job.get_job_queue()

        failed_jobs = []

        for job in self.jobs:
            if job.check_failed(job_queue = queue):
                failed_jobs.append(job)

        return jobs

    def resubmit_jobs(self):
        """
        Resubmit all failed jobs.
        """
        failed_jobs = self.get_failed_jobs()
        for job in failed_jobs:
            job.submit()

    def test_job_locally(self):
        """
        Run a random job locally.
        """
        if len(self.jobs) == 0: return

        random_job_index = random.randint(0,len(self.jobs) - 1)
        self.jobs[random_job_index].run_local()

def create_container_script(script):
    """
    Given a shell script, create a new script that will run inside of a sinulgarity container on ComputeCanada
    """
    new_script_name = script.rstrip(".sh") + "_container.sh"
    os.system("batchScript \"source {}\" -O {}".format(script, new_script_name))
    return new_script_name


class AbstractBatchSubmission(ABC):
    """
    An abstract base class that handles the submission and bookkeeping of a batch job.
    This class represents a single job to the run on a batch system.
    This should be exteneded to support submission to either Slurm or Condor.

    Attributes
    ----------
        jobname : str
            The name of this job. Used to identify this job and name it's shell script.
        job_directory : str
            The directory of where to save the error file, output file and shell scripts. If this directory doesn't exist, it will be created.
        commands : list of str
            The sequence of unix commands to be executed, in order to run the job
        time : str
            The amount of time that the job needs to run. For slurm, this might be "00:40:00", or
            for condor this could be "workday".
        memory : str
            The amount of memoery that the job needs to run. This could be 40000M (4GB) on slurm, for example.
        output : str
            The name of the output file for logging of the completion of the job. This file will be checked for job completion.
        error : str
            The name of the error file from the job submission.
        finished_token : str (optional)
            The string that indicates the completion of the job. This should be printed on one line of self.output to indicate completion.
        in_container : bool
            If true, the funtion function container_script_function will be used to generate a new script, where that the commands are run in inside of
            a container. The container_script_function is expected to return a str representing the path of the new script.
        container_script_function : function
            A function that generates a script to run the commands inside of a conatiner.
        finished : bool
            True if this job has finished running. False otherwise.
        outside_of_container_script : str
            The path of the script to run this job locally inside of the singularity container. This is useful for testing the job.
            This path is identical to self.script unless in_container is true. 

    Methods
    -------
        check_failed
            A method to check that the job has failed to execute
        check_finished
            A method to check that the job has finished executing
        get_job_queue
            An abstract method to retrieve the jobqueue as a set of jobids. Needs to be implemented by any inherited classes.
            This method is abstract because it depends on the kind of batch submission system, i.e. Slurm vs Condor.
        check_running
            A method to confirm if the job is currently running
        _submit
            An abstract method to submit the job to the batch system and return the jobid for bookkeeping.
            This method is abstract because it depends on the kind of batch submission system, i.e. Slurm vs Condor.
        submit
            A method that submits the job to the batch system. This method calls _submit, but also resets the status of this jod. This means
            that self.finished is set to False, self.running is set to true and self.jobid is updated based on the ID returned by _submit.
        run_local
            Run the job locally.
    """

    def __init__(self, jobname, job_directory, commands, time, memory, output, error, finished_token="__FINISHED__", in_container=False, container_script_function = create_container_script):
        self.commands = commands
        self.jobname = jobname
        self.job_directory = job_directory
        self.time = time
        self.memory = memory
        self.finished_token = finished_token
        self.in_container = in_container
        self.container_script_function = container_script_function

        self.output = os.path.join(job_directory, output)
        if ".out" != self.output[-4:]:
            self.output += ".out"

        self.error = os.path.join(job_directory, error)
        if ".err" != self.error[-4:]:
            self.errput += ".err"

        self.script = os.path.join(job_directory, jobname + ".sh")
        self.outside_of_container_script = self.script
        self.finished = False
        self.submitted = False
        self.jobid = None

        self._create_submission_script()

    def _create_submission_script(self):
        """
        Create the scripts necessary to run this job. Create a script by writing self.commands to a file name self.jobname in job_directory.
        If the job will be run inside of a container, create the script for that by calling self.container_script_function.
        """

        if not os.path.exists(self.job_directory):
            os.makedirs(self.job_directory)
        with open(self.script, "w") as f:
            f.write("#!/bin/sh\n")
            for c in self.commands:
                f.write(c + "\n")

        # working inside of a container, and therefore, create a script to run jobs inside of the conatiner.
        if self.in_container:
            self.script = self.container_script_function(self.script)

    def check_failed(self, job_queue = None):
        """
        Check if a job has failed. To return true, the job must be: submitted to the batch system, not currently running and not finished.
        Otherwise, return False.

        Parameters
        ----------
            job_queue : set of {int} (optional)
                A set, where the values are all of the jobs currently running on the batch system. If this is not provided, the 
                method self.get_job_queue() will be called instead.

        Returns
        -------
             None
        """
        return self.submitted and (not self.check_running(job_queue = job_queue)) and (not self.check_finished())


    def check_finished(self):
        """
        Check if a job has finished executing. This function returns true if the output file exists and
        self.finished_token is written on any line of self.output. The function returns false otherwise.
        """
        if self.finished: return True

        output_file_exists = os.path.exists(self.output)
        if not output_file_exists: return False #the output file was not made

        #look for the finished token in the output_file
        with open(self.output, "r") as f:
            lines = f.readlines()
            for el in lines:
                if self.finished_token == el.strip("\n"):
                    self.finished = True
                    return True

        return False

    @abstractmethod
    def get_job_queue(self):
        """
        Return a set of jobIDs, representing all of the jobs currently running. The values don't matter; a set is used for 
        an O(1) lookup time, compared to O(N) for a list.


        Parameters
        ----------

        Returns
        -------
            set {int}
                A set of integers of the job ids of all currently running jobs
        """
        pass

    def check_running(self, job_queue=None):
        """
        Return True of the job is running, and false otherwise. If the job is doesn't have a jobid (jobid is None), return False. If it does exist,
        return whether the jobid is in the job_queue.

        Parameters
        ----------
            job_queue : set of {int} (optional)
                A set, where the calues are all of the jobs currently running on the batch system. If this is not provided, the
                method self.get_job_queue() will be called instead.

        Returns
        -------
            int
                The jobid of the submission.
        """
        if self.jobid is None: return False

        if job_queue is None:
            job_queue = self.get_job_queue()

        return self.jobid in job_queue

    @abstractmethod
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
        pass

    def clear_output_files(self):
        while os.path.exists(self.output):
            os.system("rm {}".format(self.output))

        while os.path.exists(self.error):
            os.system("rm {}".format(self.error))

    def submit(self):
        """
        Submit the job to the batch system, and return the jobid for book keeping
        """
        self.finished = False
        self.submitted = True
        self.clear_output_files()
        self.jobid = self._submit()

    def run_local(self, in_container = False):
        """
        Run the job locally.

        Parameters
        ----------
            in_container : bool
                If True, the job will source the self.outside_of_container_script script. If false, self.script will be sourced,
                which should start a container and execute the job inside of it.

        Returns
        -------
            None

        """
        self.submitted = True
        self.finished = False
        if not in_container: os.system("source {} &> {}".format(self.outside_of_container_script, self.output))
        else: os.system("source {}".format(self.script))
        self.check_finished()
