"""
Development hack to make the path of the library
available to the examples, usefil while developing
Note: Import this before maple
"""

import sys
from pathlib import Path

path_root = Path(__file__).parents[1]
sys.path.append(str(path_root) + "/src")
