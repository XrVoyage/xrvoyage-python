import tarfile
import json
import os

# Get the tarball filename
tarball = next(file for file in os.listdir('dist') if file.endswith('.tar.gz'))

# Open the tarball
with tarfile.open(f'dist/{tarball}', 'r:gz') as tar:
    # Extract the PKG-INFO file
    pkg_info = tar.extractfile(f'{tarball[:-7]}/PKG-INFO')
    pkg_info_content = pkg_info.read().decode('utf-8')

    # Find the version line
    for line in pkg_info_content.split('\n'):
        if line.startswith('Version:'):
            version = line.split(' ')[1]
            print(f'Package version: {version}')
            break
