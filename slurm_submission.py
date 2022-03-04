from batch_submission import AbstractBatchSubmission, do_multiple_subprocess_attempts

class SlurmSubmission(AbstractBatchSubmission):
    def get_job_queue(self):
        long_info = do_multiple_subprocess_attempts(["squeue", "-u", os.getenv("USER")])
        long_info = long_info.decode("utf-8")
        long_info = long_info.rstrip("\n")
        lines = long_info.split("\n")
        if len(lines) < 2: return {}
        lines = lines[1:] #remove the header line
        lines = [l.strip() for l in lines]
        job_ids = {int(l.split(" ")[0]) for l in lines}
        return job_ids

    def _submit(self):
        submission_command = ["sbatch"]
        submission_command.append("--mem {}".format(self.memory))
        submission_command.append("--time {}".format(self.time))
        submission_command.append("--output {}".format(self.output))
        submission_command.append("--error {}".format(self.error))
        submission_command.append(self.script)

        long_info = do_multiple_subprocess_attempts(submission_command)
        long_info = long_info.decode("utf-8")
        long_info = long_info.rstrip("\n")
        long_info = long_info.strip(" ")
        job_id = int(long_info.split(" ")[-1])
        return jobid

AbstractBatchSubmission.register(SlurmSubmission)
