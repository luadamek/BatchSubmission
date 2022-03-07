import unittest
from batch_submission.slurm_submission import SlurmSubmission
import os
import time



class TestSlurmBatchSubmissionOutsideContainer(unittest.TestCase):

    payload = ["print(\"Hello World\")"]
    payload.append("print(\"__FINISHED__\")")
    with open("test.py", "w") as f:
        for p in payload:
            f.write(p + "\n")

    jobname = "testing"
    commands = ["python test.py"]
    error = "testing_error.err"
    output = "testing_output.out"
    memory = "1000M"
    time = "00:00:02"
    job_directory = "testing_directory"
    job = SlurmSubmission(jobname, job_directory, commands, time, memory, output, error, in_container=False)


    payload_failure = ["assert False\n", "Hello World\n"]
    payload.append("print(\"__FINISHED__\")")
    with open("test.py", "w") as f:
        for p in payload:
            f.write(p + "\n")

    jobname_failure = "testing_failure"
    commands_failure = ["python test.py"]
    error_failure = "testing_failure_error.err"
    output_failure = "testing_failuer_output.out"
    memory_failure = "1000M"
    time_failure = "00:00:02"
    job_directory_failure = "testing_directory"
    job_failure = SlurmSubmission(jobname_failure, job_directory_failure, commands_failure, time_failure, memory_failure, output_failure, error_failure, in_container=False)
    def test_submission_batch(self):
        job.submit()
        self.assertEqual(job.script, job.outside_of_container_script)
        self.asserTrue(job.running())
        while job.running():
            time.sleep(15)
        self.assertFalse(job.running())
        self.assertTrue(job.finished)
        self.assertTrue(job.check_finished())
        self.assertFalse(job.check_failed())

        with open(os.path.join(job_directory, output), "r") as f:
            lines = f.readlines()

        self.assertIn("Hello World\n", lines)
        self.assertIn("__FINISHED__\n", lines)

    def test_submission_batch_failure(self):
        job_failure.submit()
        self.assertEqual(job_failure, job_failure.outside_of_container_script)
        self.asserTrue(job_failure.running())
        while job.running():
            time.sleep(15)
        self.assertFalse(job_failure.running())
        self.assertFalse(job_failure.finished)
        self.assertFalse(job_failure.check_finished())
        self.assertTrue(job_failure.check_failed())

        with open(os.path.join(job_directory_failure, output_failure), "r") as f:
            lines = f.readlines()

        self.assertNotIn("Hello World\n", lines)
        self.assertNotIn("__FINISHED__\n", lines)


class TestSlurmBatchSubmissionInsideContainer(unittest.TestCase):
    payload = ["print(\"Hello World\")"]
    payload.append("print(\"__FINISHED__\")")
    with open("test.py", "w") as f:
        for p in payload:
            f.write(p + "\n")

    jobname = "testing"
    commands = ["python test.py"]
    error = "testing_error.err"
    output = "testing_output.out"
    memory = "1000M"
    time = "00:00:02"
    job_directory = "testing_directory"
    job = SlurmSubmission(jobname, job_directory, commands, time, memory, output, error, in_container=True)


    payload_failure = ["assert False\n", "Hello World\n"]
    payload.append("print(\"__FINISHED__\")")
    with open("test.py", "w") as f:
        for p in payload:
            f.write(p + "\n")

    jobname_failure = "testing_failure"
    commands_failure = ["python test.py"]
    error_failure = "testing_failure_error.err"
    output_failure = "testing_failuer_output.out"
    memory_failure = "1000M"
    time_failure = "00:00:02"
    job_directory_failure = "testing_directory"
    job_failure = SlurmSubmission(jobname_failure, job_directory_failure, commands_failure, time_failure, memory_failure, output_failure, error_failure, in_container=True)

    def test_submission_batch(self):
        job.submit()
        self.asserTrue(job.running())
        while job.running():
            time.sleep(15)
        self.assertFalse(job.running())
        self.assertTrue(job.finished)
        self.assertTrue(job.check_finished())
        self.assertFalse(job.check_failed())
        self.assertNotEqual(job.script, job.outside_of_container_script)

        with open(os.path.join(job_directory, output), "r") as f:
            lines = f.readlines()

        self.assertIn("Hello World\n", lines)
        self.assertIn("__FINISHED__\n", lines)

    def test_submission_batch_failure(self):
        job_failure.submit()
        self.asserTrue(job_failure.running())
        while job.running():
            time.sleep(15)
        self.assertFalse(job_failure.running())
        self.assertFalse(job_failure.finished)
        self.assertFalse(job_failure.check_finished())
        self.assertTrue(job_failure.check_failed())
        self.assertNotEqual(job_failure.script, job_failure.outside_of_container_script)

        with open(os.path.join(job_directory_failure, output_failure), "r") as f:
            lines = f.readlines()

        self.assertNotIn("Hello World\n", lines)
        self.assertIn("__FINISHED__\n", lines)
