import unittest
from batch_submission.slurm_submission import SlurmSubmission, get_jobid_from_submission, parse_queue_output
import os
import time

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

payload_failure = ["print(\"Hello World\")", "assert False"]
payload_failure.append("print(\"__FINISHED__\")")
with open("test_fail.py", "w") as f:
    for p in payload_failure:
       f.write(p + "\n")

jobname_failure = "testing_failure"
commands_failure = ["python test_fail.py"]
error_failure = "testing_failure_error.err"
output_failure = "testing_failuer_output.out"
memory_failure = "1000M"
time_failure = "00:00:02"
job_directory_failure = "testing_directory"
job_failure = SlurmSubmission(jobname_failure, job_directory_failure, commands_failure, time_failure, memory_failure, output_failure, error_failure, in_container=False)

long_info_submission = b'Submitted batch job 58508066\n\n'

long_info_queue = b'JOBID     USER              ACCOUNT           NAME  ST  TIME_LEFT NODES CPUS TRES_PER_N MIN_MEM NODELIST (REASON) \n58508061  ladamek      def-psavard_cpu        test.sh  PD       1:00     1    1        N/A   1000M  (Priority) \n58508062  ladamek      def-psavard_cpu        test.sh  PD       1:00     1    1        N/A   1000M  (Priority) \n58508063  ladamek      def-psavard_cpu        test.sh  PD       1:00     1    1        N/A   1000M  (Priority) \n58508064  ladamek      def-psavard_cpu        test.sh  PD       1:00     1    1        N/A   1000M  (Priority) \n58508065  ladamek      def-psavard_cpu        test.sh  PD       1:00     1    1        N/A   1000M  (Priority) \n58508066  ladamek      def-psavard_cpu        test.sh  PD       1:00     1    1        N/A   1000M  (Priority) \n\n'

class TestSlurmBatchSubmission(unittest.TestCase):
    def test_submission_local(self):
        job.run_local()
        with open(os.path.join(job_directory, output), "r") as f:
             lines = f.readlines()
        self.assertIn("Hello World\n", lines)
        self.assertIn("__FINISHED__\n", lines)
        self.assertTrue(job.finished)
        self.assertFalse(job.check_failed())
        self.assertTrue(job.submitted)

    def test_failed_submission_local(self):
        job_failure.run_local()
        with open(os.path.join(job_directory_failure, output_failure), "r") as f:
             lines = f.readlines()
        self.assertIn("Hello World\n", lines)
        self.assertNotIn("__FINISHED__\n", lines)
        self.assertFalse(job_failure.finished)
        self.assertTrue(job_failure.check_failed())
        self.assertTrue(job_failure.submitted)

    def test_jobid(self):
        self.assertEqual(get_jobid_from_submission(long_info_submission), 58508066)

    def test_queue(self):
        self.assertEqual(parse_queue_output(long_info_queue), {i for i in range(58508061, 58508066 + 1)})


if __name__ == '__main__':
     unittest.main()

