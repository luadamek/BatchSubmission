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
