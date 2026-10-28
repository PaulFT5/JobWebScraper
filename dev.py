import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).parent


def stop(proc):
    if proc.poll() is None:  # still running
        # /T kills the whole process tree, since npm and uvicorn --reload start child processes
        subprocess.run(["taskkill", "/PID", str(proc.pid), "/T", "/F"], capture_output=True)


def main():
    backend = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "backend.api.main:app",
         "--reload", "--host", "127.0.0.1", "--port", "8000"],
        cwd=ROOT,
    )
    frontend = subprocess.Popen(
        ["npm.cmd", "run", "dev"],
        cwd=ROOT / "frontend",
    )

    try:
        # keep running until Ctrl+C, or until either server exits
        while backend.poll() is None and frontend.poll() is None:
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        stop(backend)
        stop(frontend)


if __name__ == "__main__":
    main()