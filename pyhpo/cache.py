import functools
import sys
from typing import Callable

if sys.version_info.major < 3:
    raise RuntimeError('PyHPO runs only on Python >= 3.6')

if sys.version_info.major == 3 and sys.version_info.minor < 6:
    raise RuntimeError('PyHPO runs only on Python >= 3.6')


def cached_property_backport(func):  # type: ignore

    @property
    @functools.lru_cache
    def inner_function(*args, **kwargs):  # type: ignore
        return func(*args, **kwargs)

    return inner_function


if sys.version_info.minor >= 8:
    cached_property: Callable = functools.cached_property
else:
    cached_property = cached_property_backport
