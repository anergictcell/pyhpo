Changelog
=========

2.7
---
- Added type annotation to all methods
- ``Ontology.get_hpo_object`` now behaves as documented and raises an error if the term is not found instead of silently returning None

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