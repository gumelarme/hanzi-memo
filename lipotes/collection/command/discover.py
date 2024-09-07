import glob
import os
from pathlib import Path

from lipotes.collection.parser import resolve_resource_dir


def discover(pattern: str, resource_dir=None) -> list[str]:
    resource_dir = resolve_resource_dir(resource_dir)
    files = glob.glob(os.path.join(resource_dir, pattern))
    return [str(Path(x).name) for x in files]
