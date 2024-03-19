from dataclasses import dataclass
from typing import Generic, TypeVar

T = TypeVar("T")


@dataclass
class D(Generic[T]):
    data: T


def d(data):
    return D(data=data)
