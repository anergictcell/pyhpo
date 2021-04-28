from typing import Dict, List, Optional, Type

import pyhpo


class _Similarity:
    dispatch: Dict['str', 'SimilarityBase'] = {}
    kind = 'omim'
    method = 'graphic'

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


class SimilarityBase:
    dependencies: List[str] = []

    def __call__(
        self,
        term1: 'pyhpo.HPOTerm',
        term2: 'pyhpo.HPOTerm',
        kind: str,
        dependencies: List[float]
    ) -> float:
        raise NotImplementedError(
            'A similarity class requires a __call__ function'
        )


SimScore = _Similarity()
