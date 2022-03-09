import unittest
from pybatchsub.batch_submission_factory import BatchSubmissionFactory
from pybatchsub.batch_submission import BatchSubmissionSet
import os
import time

dir = os.getenv("PWD")

jobs = []
for i in range(0, 5):
    payload = ["print(\"Hello World {}\")".format(i)]
    payload.append("print(\"__FINISHED__\")")
    executable_name = "test_{}.py".format(i)
    with open(executable_name, "w") as f:
        for p in payload:
            f.write(p + "\n")

    jobname = "testing_{}".format(i)
    commands = ["cd {}".format(dir), "python {}".format(executable_name)]
    error = "testing_error_{}.err".format(i)
    output = "testing_output_{}.out".format(i)
    memory = "50M"
    time = "00:00:04"
    job_directory = "testing_batch_directory_{}".format(i)
    batch_factory = BatchSubmissionFactory(jobname, job_directory, commands, time, memory, output, error, in_container=True)
    job = batch_factory.get_batch_job()
    jobs.append(job)
jobset = BatchSubmissionSet(jobs)

jobs = []
for i in range(0, 5):
    payload = ["print(\"Hello World {}\")".format(i)]
    if i == 4:
        payload.append("assert False")
    payload.append("print(\"__FINISHED__\")")
    executable_name = "test_{}_onefail.py".format(i)
    with open(executable_name, "w") as f:
        for p in payload:
            f.write(p + "\n")

    jobname = "testing_{}".format(i)
    commands = ["cd {}".format(dir), "python {}".format(executable_name)]
    error = "testing_error_{}.err".format(i)
    output = "testing_output_{}.out".format(i)
    memory = "50M"
    time = "00:00:04"
    job_directory = "testing_batch_directory_failure_{}".format(i)
    batch_factory = BatchSubmissionFactory(jobname, job_directory, commands, time, memory, output, error, in_container=True)
    job = batch_factory.get_batch_job()
    jobs.append(job)
jobset_onefail = BatchSubmissionSet(jobs)

import time

class TestSlurmBatchSubmissionInsideContainer(unittest.TestCase):
    def test_submission_batch(self):
       jobset.submit()
       self.assertTrue(jobset.check_running())
       while jobset.check_running():
           time.sleep(5)
       self.assertFalse(jobset.check_running())
       self.assertTrue(jobset.check_finished())
       self.assertEqual(jobset.get_failed_jobs(), [])

       for i in range(0, 5):
           jobdir = "testing_batch_directory_{}".format(i)
           output = "testing_output_{}.out".format(i)
           with open(os.path.join(jobdir, output), "r") as f:
               lines = f.readlines()

           self.assertIn("Hello World {}\n".format(i), lines)
           self.assertIn("__FINISHED__\n", lines)

    def test_submission_batch_failure(self):
       jobset_onefail.submit()
       self.assertTrue(jobset_onefail.check_running())
       while jobset_onefail.check_running():
           time.sleep(5)
       self.assertFalse(jobset_onefail.check_running())
       self.assertFalse(jobset_onefail.check_finished())
       self.assertEqual(len(jobset_onefail.get_failed_jobs()), 1)

       jobset_onefail.resubmit()
       self.assertTrue(jobset_onefail.check_running())
       self.assertFalse(jobset_onefail.check_finished())
       while jobset_onefail.check_running():
           time.sleep(5)
       self.assertFalse(jobset_onefail.check_running())
       self.assertFalse(jobset_onefail.check_finished())

       for i in range(0, 5):
           jobdir = "testing_batch_directory_failure_{}".format(i)
           output = "testing_output_{}.out".format(i)
           with open(os.path.join(jobdir, output), "r") as f:
               lines = f.readlines()

           self.assertIn("Hello World {}\n".format(i), lines)
           if i != 4: self.assertIn("__FINISHED__\n", lines)
           else: self.assertNotIn("__FINISHED__\n", lines)



if __name__ == "__main__":
    unittest.main()
