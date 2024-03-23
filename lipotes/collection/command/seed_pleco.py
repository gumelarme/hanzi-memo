import glob
import os
from pathlib import Path

from tqdm import tqdm

from resources.collections.pleco import parse_pleco

from .action import resolve_resource_dir, seed_collection


async def seed_pleco(files: str):
    files = list(map(str.strip, files.split(",")))
    try:
        for file in files:
            validate_pleco_file(file)
    except Exception as e:
        print(f"Error: {e}")
        print_available_pleco_files()
        return

    shown_file = files[0]
    if len(files) > 1:
        shown_file = f"{files[0]}-{files[-1]}"

    desc = f"Seeding pleco {shown_file}"
    with tqdm(total=len(files), desc=desc) as progress_bar:
        for file in files:
            collections = parse_pleco(file)
            for coll_name, words in collections.items():
                await seed_collection(
                    coll_name, list(words), ["zh_sc", "zh_tc", "pinyin"]
                )
            progress_bar.update(1)


def validate_pleco_file(file: str, resource_dir=None) -> None:
    resource_dir = resolve_resource_dir(resource_dir)
    filename = os.path.join(resource_dir, file)
    if not os.path.isfile(filename):
        raise Exception(f"File {filename!r} did not exist")


def print_available_pleco_files(resource_dir=None) -> None:
    resource_dir = resolve_resource_dir(resource_dir)
    pleco_files = glob.glob(os.path.join(resource_dir, "*.xml"))
    pleco_files = [f"  - {Path(x).name}" for x in pleco_files]
    print("Available pleco files: ")
    print("\n".join(pleco_files))
