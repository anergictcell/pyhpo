from pyhpo.similarity.base import SimScore
from pyhpo.similarity.defaults import register_defaults


register_defaults(SimScore)


__all__ = (
    'SimScore',
)
