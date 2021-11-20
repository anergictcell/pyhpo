Similarity
==========

The ``similarity`` submodule allows to create custom Similarity calculations
for comparison of single terms or term-sets.

It provides a simple interface to register custom Similarity handler, so
that they can be called directly on an :class:`pyhpo.term.HPOTerm` or an
:class:`pyhpo.set.HPOSet`.

SimilarityBase
**************
.. autoclass:: pyhpo.similarity.base.SimilarityBase

__call__
--------
.. automethod:: pyhpo.similarity.base.SimilarityBase.__call__


Examples
********

.. code:: python

    from pyhpo.similarity.base import SimScore, SimilarityBase
    from pyhpo import Ontology

    class CustomSimscore(SimilarityBase):
        # For demo purposes, we will just check for equality

        def __call__(
            self,
            term1: 'pyhpo.HPOTerm',
            term2: 'pyhpo.HPOTerm',
            kind: str,
            dependencies: List[float]
        ) -> float:
            if term1 == term2:
                return 1
            else:
                return 0

    SimScore.register('custom_method', CustomSimscore)

    _ = Ontology()
    
    term1 = Ontology.get_hpo_object('Scoliosis')
    term2 = Ontology.get_hpo_object('Thoracic scoliosis')

    sim_score = term1.similarity_score(
        other=term2,
        kind='omim',  # actually doesn't matter in this example
        method='custom_method'
    )

    assert sim_score == 0

    # Now comparing the same term to each other
    sim_score = term1.similarity_score(
        other=term1,
        kind='omim',  # actually doesn't matter in this example
        method='custom_method'
    )

    assert sim_score == 1