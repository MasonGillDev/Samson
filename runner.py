import subprocess
import sys


command_string = "error"


result = subprocess.run(["./runner.sh"],input=command_string,capture_output=True, text=True)


print(result.stdout)