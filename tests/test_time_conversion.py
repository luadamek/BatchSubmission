import unittest
from batch_submission.batch_submission_factory import *

class TestSlurmBatchSubmission(unittest.TestCase):
    def test_check_if_condor_time(self):
        self.assertFalse(check_if_condor_time(None))
        self.assertTrue(check_if_condor_time("workday"))
        self.assertTrue(check_if_condor_time("espresso"))
        self.assertFalse(check_if_condor_time("notatime"))

    def test_check_if_condor_time(self):
        self.assertTrue(check_if_slurm_time("00:00:01"))
        self.assertFalse(check_if_slurm_time("00:000:02"))
        self.assertTrue(check_if_slurm_time("99:99:99"))
        self.assertTrue(check_if_slurm_time("10:10:00"))
        self.assertFalse(check_if_slurm_time("workday"))
        self.assertFalse(check_if_slurm_time("microcentury"))

    def test_get_raw_time_from_slurm_time(self):
        self.assertEqual(get_raw_time_from_slurm_time("00:00:00"), [0,0,0])
        self.assertEqual(get_raw_time_from_slurm_time("00:20:00"), [0,20,0])
        self.assertEqual(get_raw_time_from_slurm_time("05:20:00"), [5,20,0])
        self.assertEqual(get_raw_time_from_slurm_time("00:00:05"), [0, 0, 5])
        self.assertEqual(get_raw_time_from_slurm_time("notatime"), None)

    def test_greater_than_equal(self):
        self.assertTrue(greater_than_equal([0,20,0], [0,0,0]))
        self.assertFalse(greater_than_equal([0,20,0], [0,40,0]))
        self.assertTrue(greater_than_equal([0,20,0], [0,0,60]))
        self.assertTrue(greater_than_equal([1,20,0], [0,60,60]))

    def test_time_translation_slurm_to_condor(self):
        self.assertEqual(time_translation_slurm_to_condor("00:00:20"), "espresso")
        self.assertEqual(time_translation_slurm_to_condor("00:00:40"), "microcentury")
        self.assertEqual(time_translation_slurm_to_condor("00:02:00"), "longlunch")
        self.assertEqual(time_translation_slurm_to_condor("00:03:00"), "workday")
        self.assertEqual(time_translation_slurm_to_condor("00:08:00"), "workday")
        self.assertEqual(time_translation_slurm_to_condor("00:10:45"), "tomorrow")
        self.assertEqual(time_translation_slurm_to_condor("01:00:00"), "tomorrow")
        self.assertEqual(time_translation_slurm_to_condor("02:00:00"), "testmatch")
        self.assertEqual(time_translation_slurm_to_condor("10:00:00"), "nextweek")

    def time_time_translation_condor_to_slurm(self):
        self.assertEqual("workday", "00:08:00")
        self.assertEqual("nextweek", "07:00:00")


if __name__ == "__main__":
    unittest.main()
