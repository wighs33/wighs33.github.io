"""Compatibility entry point: always build the curated 100-class atlas."""
import runpy
from pathlib import Path
runpy.run_path(str(Path(__file__).with_name("build-core-class-map.py")), run_name="__main__")
