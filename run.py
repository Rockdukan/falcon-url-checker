import os
import subprocess
import sys


def main() -> None:
    bind = os.environ.get("BIND", "127.0.0.1:8000")
    timeout = os.environ.get("TIMEOUT", "120")

    code = subprocess.run(
        [
            sys.executable,
            "-m",
            "gunicorn",
            "--bind",
            bind,
            "--timeout",
            timeout,
            "wsgi:app",
        ],
        check=False,
    ).returncode

    raise SystemExit(code)


if __name__ == "__main__":
    main()
