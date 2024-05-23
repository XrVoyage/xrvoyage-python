import subprocess

def get_semver():
    try:
        # Run git describe to get the tag information
        result = subprocess.run(['git', 'describe', '--tags'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        describe_output = result.stdout.decode().strip()

        # Extract the parts of the git describe output
        parts = describe_output.split('-')
        first = parts[0]
        first = first.split('v')[1] if 'v' in first else first
        second = parts[1] if len(parts) > 1 else ''
        div = '.' if second else ''

        # Construct the semantic version
        semver = f"{first}{div}{second}"
        return semver
    except subprocess.CalledProcessError as e:
        print(f"Error running git describe: {e.stderr.decode().strip()}")
        return None

if __name__ == "__main__":
    semver = get_semver()
    if semver:
        print(semver)
