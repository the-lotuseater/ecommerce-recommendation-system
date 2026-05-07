import os
import subprocess
import sys

def start_backend():
    try:
        process = subprocess.Popen(
            [sys.executable, "-m", "backend.server"]
        )
        return process
    except Exception as e:
        print(f"Error starting backend: {e}")
        raise e

def start_frontend():
    try:
        subprocess.run(
            ["npm", "run", "dev"],
            cwd=os.path.join(os.path.dirname(__file__), "frontend"),
            check=True,
            shell=True
        )
    except subprocess.CalledProcessError as e:
        print(f"Error starting frontend: {e}")
        raise e


if __name__ == "__main__":
    backend = start_backend()
    start_frontend()
    backend.wait()
