Annotations
===========

The ``Annotations`` section contains various metadata annotations for HPO terms.

``GeneSingleton`` class
***********************
.. autoclass:: pyhpo.annotations.GeneSingleton
   :no-private-members:
   :no-special-members:

toJSON
------
.. automethod:: pyhpo.annotations.GeneSingleton.toJSON


``GeneDict`` class
******************
.. autoclass:: pyhpo.annotations.GeneDict
   :no-private-members:
   :no-special-members:


``DiseaseSingleton`` class
**************************
.. autoclass:: pyhpo.annotations.DiseaseSingleton
   :no-private-members:
   :no-special-members:

toJSON
------
.. automethod:: pyhpo.annotations.DiseaseSingleton.toJSON

``DiseaseDict`` class
*********************
.. autoclass:: pyhpo.annotations.DiseaseDict
   :no-private-members:
   :no-special-members:

Omim
****
Instance of :class:`pyhpo.annotations.DiseaseDict` to handle Omim diseases. Ensures that diseases are not duplicated through use of Singletons.

Orpha
*****
Instance of :class:`pyhpo.annotations.DiseaseDict` to handle Orphanet diseases. Ensures that diseases are not duplicated through use of Singletons.

Decipher
********
Instance of :class:`pyhpo.annotations.DiseaseDict` to handle Decipher diseases. Ensures that diseases are not duplicated through use of Singletons.

``HPO_Gene`` class
******************
.. autoclass:: pyhpo.annotations.HPO_Gene
   :no-private-members:
   :no-special-members:


Methods
*******

parse_pheno_file
----------------
.. autofunction:: pyhpo.annotations.parse_pheno_file

remove_outcommented_rows
------------------------
.. autofunction:: pyhpo.annotations.remove_outcommented_rows
