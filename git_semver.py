import subprocess

def get_git_semver():
    describe_command = ["git", "describe", "--tags"]
    result = subprocess.run(describe_command, stdout=subprocess.PIPE, text=True)
    describe_output = result.stdout.strip()

    if "-" in describe_output:
        first, second, _ = describe_output.split("-")
        first = first.lstrip("v")
        semver = f"{first}.{second}"
    else:
        first = describe_output.lstrip("v")
        semver = f"{first}.0"

    print(semver)

if __name__ == "__main__":
    get_git_semver()
