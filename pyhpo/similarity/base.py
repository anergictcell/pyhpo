from typing import Dict, List, Optional, Type

from pydantic import BaseModel

import pyhpo


class _Similarity(BaseModel):
    dispatch: Dict[str, 'SimilarityBase'] = {}
    kind: str = 'omim'
    method: str = 'graphic'

    def __call__(
        self,
        term1: 'pyhpo.HPOTerm',
        term2: 'pyhpo.HPOTerm',
        kind: Optional[str] = '',
        method: Optional[str] = ''
    ) -> float:
        kind = kind or self.kind
        method = method or self.method
        try:
            similarity = self.dispatch[method]
        except KeyError as err:
            raise RuntimeError(
                f'Unknown method {method} to calculate similarity'
            ) from err

        dependencies: List[float] = [
            self(term1, term2, kind, dep) for dep in similarity.dependencies
        ]

        return similarity(term1, term2, kind, dependencies)

    def register(
        self,
        name: str,
        similarity_class: Type['SimilarityBase']
    ) -> None:
        self.dispatch[name] = similarity_class()


class SimilarityBase(BaseModel):
    """
    Base class to use for custom similarity calculations.

    Custom implementation must inherit from
    :class:`pyhpo.similarity.base.SimilarityBase` and provide a
    ``__call__`` method with the same signature as
    :func:`pyhpo.similarity.base.SimilarityBase.__call__`

    You can also provide a list of ``dependencies`` of other
    similarity methods that should be called beforehand. Results
    of these calls will be passed as ``dependencies`` parameter to
    the ``__call__`` method.
    """
    dependencies: List[str] = []

    def __call__(
        self,
        term1: 'pyhpo.HPOTerm',
        term2: 'pyhpo.HPOTerm',
        kind: str,
        dependencies: List[float]
    ) -> float:
        """
        This method does the actual calculation of the similarity.
        This method must be provided in all custom similarity classes

        Parameters
        ----------
        term1:
            One of the two terms to compare
        term2:
            The other of the two terms to compare
        kind:
            This can be an extra parameter, ususally ``omim`` or ``gene``
            to specify which annotations to consider for similarity
        depdencies:
            A list of other calculation-results that should be calculated
            beforehand. This is not needed at all, but helpful if your
            implementation builds on an already existing similarity
            calculation.
        """
        raise NotImplementedError(
            'A similarity class requires a __call__ function'
        )


SimScore = _Similarity()
