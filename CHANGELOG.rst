Changelog
=========

3.2.0
-----
Update Pydantic dependency to 2.0

Data update to 2023-06-17

3.1.5
-----
Data update to 2023-04-05

Minor fix in parsing to account for new JAX HPO data format

3.0
---
Refactored huge parts of the code, enabling more strict mypy type checking
and class validation via Pydantic. This makes development much easier, but has
a few, minor impacts on the library's API.

Obviously, 3.0.0 also includes a data update to 2021-10-10.

Breaking API changes:
^^^^^^^^^^^^^^^^^^^^^

Python version
""""""""""""""
Due to use of f-strings, PyHPO requires Python >= 3.6


``Ontology.omim_excluded_diseases``
"""""""""""""""""""""""""""""""""""
removed


``Ontology.orpha_excluded_diseases``
"""""""""""""""""""""""""""""""""""
removed


``Ontology.decipher_excluded_diseases``
"""""""""""""""""""""""""""""""""""
removed


``HPOTerm.children`` and ``HPOTerm.parents``
""""""""""""""""""""""""""""""""""""""""""""
``HPOTerm.children`` and ``HPOTerm.parents`` now are ``set(HPOTerm)`` instead of ``list(HPOTerm)``. This makes more sense logically, but breks code that slices the result. I believe this to be low impact, since there is no good reason to slice a list of children or parents. In an ideal case one wants to iterate through them or check for existence or length. This behaviour is still possible:

This code will still work

.. code-block:: python

    for child in term.children:
        # do something with the child-term
        child.similarity(term)

    if term_x in term.children:
        # Hooray

    if len(term.children):
        # Hooray


``HPOTerm.hierarchy``
"""""""""""""""""""""
``HPOTerm.hierarchy`` now is a property and not a method anymore.


``HPOTerm._index``
"""""""""""""""""""""
``HPOTerm._index`` now is a public attribute ``HPOTerm.index``.


``HPOTerm.id_from_string``
""""""""""""""""""""""""""
``HPOTerm.id_from_string`` is moved to ``pyhpo.parser.generics.id_from_string``.


``HPOTerm.parse_synonym``
"""""""""""""""""""""""""
``HPOTerm.parse_synonym`` is moved to a semi-private function in the OBO parser.


``Ontology[index]`` / ``Ontology.__getitem__``
""""""""""""""""""""""""""""""""""""""""""""""
Direct access of ``HPOTerms`` from the Ontology raises ``KeyError`` instead
of returning ``None`` if no term is present for the index.


``HPOTerm.genes``, ``HPOTerms.omim_diseases``, ``HPOTerm.orpha_diseases``, ``HPOTerm.decipher_diseases``
""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
Updating gene or diease annotations should be done only via

* ``pyhpo.parser.genes.add_gene_to_term``
* ``pyhpo.parser.diseases.add_decipher_to_term``
* ``pyhpo.parser.diseases.add_negative_decipher_to_term``
* ``pyhpo.parser.diseases.add_omim_to_term``
* ``pyhpo.parser.diseases.add_negative_omim_to_term``
* ``pyhpo.parser.diseases.add_orpha_to_term``
* ``pyhpo.parser.diseases.add_negative_orpha_to_term``

.. note::

    Updating ``HPOTerm.genes``, ``HPOTerm.omim_diseases`` etc directly will not update the parent and child terms properly.

.. code-block:: python

    # DON'T DO THIS
    term.genes.update(new_gene)

    # Do this instead
    from pyhpo.parser.genes import add_gene_to_term
    add_gene_to_term(new_gene, term)


``HPOTerm.similarity``
"""""""""""""""""""""""""
``HPOTerm.similarity`` no longer defines the default options. They are now defined in
``pyhpo.similarity.base._Similarity``. Defaults now to:

* method: ``graphic``
* kind: ``omim``


``HPOTerm.shortest_path_to_parent``
"""""""""""""""""""""""""""""""""""
``HPOTerm.shortest_path_to_parent`` raises a RuntimeError if the ``other``
term is not a parent of ``self`` instead of returning ``(inf, None)``.


``HPOTerm.__repr__``
""""""""""""""""""""
Changed repr to be more readable and more pythonic.


``HPOTerm.print_hierarchy``
"""""""""""""""""""""""""""
``HPOTerm.print_hierarchy`` has been removed and is not part of the public
API anymore


``Disease.hpo``, ``Gene.hpo``
"""""""""""""""
There are no setter and wrapper methods around this anymore. These attributes
should not be set by clients and should only be modified by the library itself.


``Ontology()``
""""""""""""""
Initiating the ontology with custom data changed to specify the path to
the data folder


``Gene``
""""""""
Retired old list-based initializiation. Use keyword arguments instead

.. code-block:: python

    # DON'T DO THIS
    mygene = Gene([None, None, 1, 'EZH2'])

    # Do this instead
    mygene = Gene(hgncid=1, symbol='EZH2')


``Omim``, ``Decipher``, ``Orpha``
"""""""""""""""""""""""""""""""""
Retired old list-based initializiation. Use keyword arguments instead

.. code-block:: python

    # DON'T DO THIS
    my_disease = Omim([None, 1, 'Gaucher'])

    # Do this instead
    my_disease = Omim(diseaseid=1, name='Gaucher')


Changes in behaviour
^^^^^^^^^^^^^^^^^^^^

Annotations
"""""""""""
Disease and Gene annotations are not completely bidirectional anymore.
HPOTerms do still inherit their annotation to their parent terms. But diseases and genes do not get these inheritances assigned reciprocally. 

For example, consider ``COHEN SYNDROME (OMIM-ID: 216550)``. 

Cohen syndrom is linked to ``HP:0002943 | Thoracic scoliosis`` in the HPO-Annotations file, but not to ``HP:0002650 | Scoliosis``. Since Scoliosis is a parent of Thoracic scoliosis, both HPOTerms are annotated with Cohen disease. However, Cohen disease is only annotated with the Thoracic scoliosis HPOterm.

.. code-block:: python

    cohen = Omim.get(216550)
    scoliosis = Ontology[2650]
    thoracic_scoliosis = Ontology[2943]

    thoracic_scoliosis.child_of(scoliosis)
    # >> True

    cohen in scoliosis.omim_diseases
    # >> True

    cohen in thoracic_scoliosis.omim_diseases
    # >> True

    thoracic_scoliosis.index in cohen.hpo
    # >> True

    scoliosis.index in cohen.hpo
    # >> False


Term search in Ontology
"""""""""""""""""""""""
Searching via ``Ontology.search`` or ``Ontology.synonym_search`` is now case insensitive.


2.7
---
- Added type annotation to all methods
- ``Ontology.get_hpo_object`` now behaves as documented and raises an error if the term is not found instead of silently returning None
- 2.7.3 Fixes a bug in ``EnrichmentModel.enrichment`` method.

2.6
---
- Refactored Gene and Disease annotations
- Added proper hashing methods to ``HPOTerm``, ``Disease`` and ``Gene``
- Bugfix for similarity score when one set does not contain any HPOTerm
- 2.6.1: Re-add (Gene/Omim).get method for single gene/disease fetching. Needed in pyhpoapi

2.5
---
- Added combination methods for HPOset similarities
- Added Matrix module for row/column based operations
- Data update to ``hp/releases/2020-10-12``
    - HPO: 15530 ==> 15656
    - Genes: 4366 ==> 4484
    - OMIM: 7801 ==> 7860
    - Negative OMIM: 652 ==> 660
    - ORPHANET: 3956 ==> 3989
    - Negative ORPHANET: 255 ==> 259
    - DECIPHER: 47 ==> 47
    - Negative DECIPHER: 0 ==> 0

2.4
---
- Data update to ``hp/releases/2020-08-11``
    - HPO: 15332 ==> 15530
    - Genes: 4317 ==> 4366
    - OMIM: 7675 ==> 7801
    - Negative OMIM: 638 ==> 652
    - ORPHANET: 3889 ==> 3956
    - Negative ORPHANET: 240 ==> 255
    - DECIPHER: 47 ==> 47
    - Negative DECIPHER: 0 ==> 0

2.3
---
- Added GraphIC similarity measure

2.2
---
- Added Orphanet diseases to Annotation
- Added Decipher diseases to Annotation

2.1
---
- Reworked BasicHPOSet
- Added omim_diseases to HPOSet
- Added distance method to similarity measurement
- Added equal measurement to HPOSet similarity

2.0
---
- Refactored Ontology to act as a singleton
  - Able to remove some weird dependencies when creating HPOSets
  - Refactored some unit tests to only temporarily mock methods
- Performance improvements through using more cached objects
- Making HPOSet an actual set
- Adding BasicHPOSet
- Handling obsolete terms

1.4
---
- Added serialization to HPO Term and HPO Set
- Option to remove modifier from HPO Set
- Changed Omim and Gene to be Singletons

1.3
---
- Data update
    - HPO: 14961 ==> 15332
    - Genes: 4312 ==> 4317
    - OMIM: 7623 ==> 7675
    - Negative OMIM: 634 ==> 638

1.2
---
- Data update
    - HPO: 14832 ==> 14961
    - Genes: 4293 ==> 4312
    - OMIM: 7758 ==> 7623
    - Negative OMIM: 631 ==> 634
- Switched to new annotation files from HPO Team (``phenotype.hpoa``)

1.1.2
-----
- Only data update

1.1.1
-----
- No code changes
- Removed daemon and client scripts since they are not yet part of the package and aren't working.
- Restructured some metadata for packaging and documentation

1.1
---
- Adding annotation automatically to the Ontology by default.
   - This should not break backwards compatibility, since all annotation data is stored in the repo itself and thus always present

1.0.1
-----
- Include data (HPO-Ontology and Annotation) directly in the repo
- Data updates:
   - HPO: hp/releases/2019-09-06
      - Added HPO terms: 14647 ==> 14831
   - Genes: Added genes 4073 ==> 4231
   - OMIM: Added diseases 7665 ==> 7677
   - OMIM excluded: Added excluded diseases 614 ==> 623

1.0
---
- First stable release