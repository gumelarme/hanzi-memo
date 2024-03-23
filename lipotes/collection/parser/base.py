import os
from dataclasses import dataclass


@dataclass(frozen=True)
class ZHWord:
    zh_sc: str | None
    zh_tc: str | None
    pinyin: str | None = None

    def __post_init__(self):
        # setattr here to avoid frozen=True raising error
        if self.zh_sc == "":
            object.__setattr__(self, "zh_sc", None)

        if self.zh_tc == "":
            object.__setattr__(self, "zh_tc", None)

        if not any([self.zh_sc, self.zh_tc]):
            raise Exception("At least one of `zh_sc` or `zh_tc` must be present")


def resolve_resource_dir(resource_dir: str = None) -> str:
    if resource_dir is None:
        resource_dir = os.path.join(os.getcwd(), "resources/collections/data/source")

    return resource_dir
