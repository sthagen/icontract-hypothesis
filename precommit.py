#!/usr/bin/env python3
"""Run precommit checks on the repository."""
import argparse
import os
import pathlib
import subprocess
import sys


def main() -> int:
    """"Execute entry_point routine."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--overwrite",
        help="Overwrites the unformatted source files with the well-formatted code in place. "
        "If not set, an exception is raised if any of the files do not conform to the style guide.",
        action="store_true",
    )

    args = parser.parse_args()

    overwrite = bool(args.overwrite)

    repo_root = pathlib.Path(__file__).parent

    print("Black'ing...")
    # fmt: off
    black_targets = [
        "icontract_hypothesis",
        "tests", "precommit.py", "setup.py",
        "benchmarks", "benchmark.py",
        "check_help_in_readme.py",
        "--exclude", "tests/pyicontract_hypothesis/samples",
    ]
    # fmt: on

    if overwrite:
        subprocess.check_call(["black"] + black_targets, cwd=str(repo_root))
    else:
        subprocess.check_call(["black", "--check"] + black_targets, cwd=str(repo_root))

    print("Mypy'ing...")
    mypy_targets = ["icontract_hypothesis", "tests"]
    subprocess.check_call(["mypy", "--strict"] + mypy_targets, cwd=str(repo_root))

    print("Pylint'ing...")
    pylint_targets = ["icontract_hypothesis"]
    subprocess.check_call(
        ["pylint", "--rcfile=pylint.rc"] + pylint_targets, cwd=str(repo_root)
    )

    print("Pydocstyle'ing...")
    subprocess.check_call(["pydocstyle", "icontract_hypothesis"], cwd=str(repo_root))

    print("Testing...")
    env = os.environ.copy()
    env["ICONTRACT_SLOW"] = "true"

    subprocess.check_call(
        [
            "coverage",
            "run",
            "--source",
            "icontract_hypothesis",
            "-m",
            "unittest",
            "discover",
        ],
        cwd=str(repo_root),
        env=env,
    )

    subprocess.check_call(["coverage", "report"])

    print("Doctesting...")
    subprocess.check_call([sys.executable, "-m", "doctest", "README.rst"])
    for pth in (repo_root / "icontract_hypothesis").glob("**/*.py"):
        subprocess.check_call([sys.executable, "-m", "doctest", str(pth)])

    print("Checking the restructured text of the readme...")
    subprocess.check_call(
        [sys.executable, "setup.py", "check", "--restructuredtext", "--strict"]
    )

    print("Checking the help in the readme...")
    subprocess.check_call([sys.executable, "check_help_in_readme.py"])

    return 0


if __name__ == "__main__":
    sys.exit(main())
