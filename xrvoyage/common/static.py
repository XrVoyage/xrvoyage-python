import subprocess

def execute_command(command):
    """Executes a shell command and returns the output."""
    try:
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        return None

def get_git_version():
    """Gets the current git version using `git describe --tags`."""
    return execute_command(['git', 'describe', '--tags'])

def get_git_branch():
    """Gets the current git branch with an asterisk."""
    branches = execute_command(['git', 'branch'])
    if branches:
        for branch in branches.split('\n'):
            if branch.startswith('*'):
                return branch[2:].strip()
    return None

def discover_version():
    """Discovers the version from git if possible."""
    version = get_git_version()
    branch = get_git_branch()
    if version and branch:
        return f"{version} [{branch}]"
    return "0.0.0"

try:
    # During build this is generated
    from .._version import version as __version__
except ImportError:
    # During development this is discovered
    __version__ = discover_version()

def get_version():
    return __version__

def print_version():
    print(__version__)
