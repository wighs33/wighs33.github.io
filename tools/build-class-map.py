"""Build the complete game-header class tree and member documentation."""
import runpy
from pathlib import Path
runpy.run_path(str(Path(__file__).with_name("build-class-tree.py")), run_name="__main__")
