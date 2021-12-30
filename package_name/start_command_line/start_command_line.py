""" Command line utility for repository """
import fire
from repo_utils import get_repository_path
import os
import importlib

package_name = __file__.replace(get_repository_path(), '').split(os.sep)[1]
mod = importlib.import_module(package_name)

def start_command_line():
    """
    Command-line interface for the repository.
    Specify the definition to execute and then any arguments.
    e.g. "define <name>".
    The Fire library converts the specified function or object into a command-line utility.
    """
    global mod
    fire.Fire(mod)
