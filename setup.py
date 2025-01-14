#!/usr/bin/env python

import glob
import os
import sys
from shutil import rmtree

from setuptools import Command, find_packages, setup
from setuptools.command.test import test as TestCommand


def read(fname):
    """
    Read the contents of a file.

    Parameters
    ----------
    fname : str
        Path to file.

    Returns
    -------
    str
        File contents.
    """
    with open(os.path.join(os.path.dirname(__file__), fname)) as f:
        return f.read()


install_requires = read("requirements.txt").splitlines()

# Dynamically determine extra dependencies
extras_require = {}
extra_req_files = glob.glob("requirements-*.txt")
for extra_req_file in extra_req_files:
    name = os.path.splitext(extra_req_file)[0].replace("requirements-", "", 1)
    extras_require[name] = read(extra_req_file).splitlines()

# If there are any extras, add a catch-all case that includes everything.
# This assumes that entries in extras_require are lists (not single strings),
# and that there are no duplicated packages across the extras.
if extras_require:
    extras_require["all"] = sorted({x for v in extras_require.values() for x in v})


# Import meta data from __meta__.py
#
# We use exec for this because __meta__.py runs its __init__.py first,
# __init__.py may assume the requirements are already present, but this code
# is being run during the `python setup.py install` step, before requirements
# are installed.
# https://packaging.python.org/guides/single-sourcing-package-version/
meta = {}
exec(read("package_name/__meta__.py"), meta)


# Import the README and use it as the long-description.
# If your readme path is different, add it here.
possible_readme_names = ["README.md", "README.rst", "README.txt", "README"]

# Handle turning a README file into long_description
long_description = meta["description"]
readme_fname = ""
for fname in possible_readme_names:
    try:
        long_description = read(fname)
    except IOError:
        # doesn't exist
        continue
    else:
        # exists
        readme_fname = fname
        break

# Infer the content type of the README file from its extension.
# If the contents of your README do not match its extension, manually assign
# long_description_content_type to the appropriate value.
readme_ext = os.path.splitext(readme_fname)[1]
if readme_ext.lower() == ".rst":
    long_description_content_type = "text/x-rst"
elif readme_ext.lower() == ".md":
    long_description_content_type = "text/markdown"
else:
    long_description_content_type = "text/plain"


class PyTest(TestCommand):
    """Support setup.py test."""

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import pytest

        pytest.main(self.test_args)


class UploadCommand(Command):
    """Support setup.py upload."""

    description = "Build and publish the package."
    user_options = []

    @staticmethod
    def status(s):
        """Print things in bold."""
        print("\033[1m{0}\033[0m".format(s))

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        try:
            self.status("Removing previous builds...")
            here = os.path.abspath(os.path.dirname(__file__))
            rmtree(here, "dist")
        except OSError:
            pass

        self.status("Building Source and Wheel (universal) distribution...")
        os.system("{0} setup.py sdist bdist_wheel --universal".format(sys.executable))

        self.status("Uploading the package to PyPI via Twine...")
        os.system("twine upload dist/*")

        self.status("Pushing git tags...")
        os.system("git tag v{0}".format(meta["__version__"]))
        os.system("git push --tags")

        sys.exit()

# START repo_utils addition
import importlib
import subprocess
# sys already imported

def imp(package):
    """ Import module by name """
    try:
      mod = importlib.import_module(package)
      return mod
    except (ImportError, KeyError):
      return None

def install(package): # credit to https://stackoverflow.com/questions/12332975/installing-python-module-within-code
    subprocess.call([sys.executable, "-m", "pip", "install", package])

def impstall(package):
    """ Try to import name of package. If import fails, install, then import.
    """
    mod = imp(package)
    if mod is None:
      install(package)
      mod = imp(package)
    return mod

impstall('rc-repo-utils')
from repo_utils import enable_installing_dependencies, get_repository_path
# Add init file for every definition. This is necessary when installing for production,
#   and not necessary when installing in development mode with -e (pip install -e .).
init_filepaths = enable_installing_dependencies(get_repository_path(), meta["path"])
# END repo_utils addition

setup(
    # Essential details on the package and its dependencies
    name=meta["name"],
    version=meta["version"],
    packages=find_packages(exclude=["tests", "*.tests", "*.tests.*", "tests.*"]),
    package_dir={meta["name"]: os.path.join(".", meta["path"])},
    # START repo_utils addition
    entry_points={
        "console_scripts": [f"{meta['path']}={meta['path']}:start_command_line"],
    },
    scripts=["install.py"],
    # END repo_utils addition
    # If any package contains *.txt or *.rst files, include them:
    # package_data={"": ["*.txt", "*.rst"],}
    python_requires=">=3.6",
    install_requires=install_requires,
    extras_require=extras_require,
    # Metadata to display on PyPI
    author=meta["author"],
    author_email=meta["author_email"],
    description=meta["description"],
    long_description=long_description,
    long_description_content_type=long_description_content_type,
    license=meta["license"],
    url=meta["url"],
    classifiers=[
        # Trove classifiers
        # Full list: https://pypi.python.org/pypi?%3Aaction=list_classifiers
        "Natural Language :: English",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    # Could also include keywords, download_url, project_urls, etc.
    # Custom commands
    cmdclass={
        "test": PyTest,
        "upload": UploadCommand,
    },
)

# START repo_utils addition
# Remove init files created by calling enable_installing_dependencies before setup.
for filepath in init_filepaths:
    if os.path.exists(filepath):
        os.remove(filepath)
# END repo_utils addition
