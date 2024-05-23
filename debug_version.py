# debug_version.py
import setuptools_scm

version = setuptools_scm.get_version()
print(f"Extracted version: {version}")
