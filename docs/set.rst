HPOSet
====================
``HPOSet`` instances contains a set of HPO terms. This class is useful to represent a patient's clinical information.

It provides analytical helper functions to narrow down the actual provided clinical information.


``HPOSet`` class
*****************
.. autoclass:: pyhpo.set.HPOSet
   :no-private-members:
   :no-special-members:

child_nodes
--------------------
.. automethod:: pyhpo.set.HPOSet.child_nodes

remove_modifier
--------------------
.. automethod:: pyhpo.set.HPOSet.remove_modifier

replace_obsolete
--------------------
.. automethod:: pyhpo.set.HPOSet.replace_obsolete

all_genes
--------------------
.. automethod:: pyhpo.set.HPOSet.all_genes

omim_diseases
--------------------
.. automethod:: pyhpo.set.HPOSet.omim_diseases

information_content
--------------------
.. automethod:: pyhpo.set.HPOSet.information_content

variance
--------------------
.. automethod:: pyhpo.set.HPOSet.variance

combinations
--------------------
.. automethod:: pyhpo.set.HPOSet.combinations

combinations_one_way
--------------------
.. automethod:: pyhpo.set.HPOSet.combinations_one_way

similarity
--------------------
.. automethod:: pyhpo.set.HPOSet.similarity

toJSON
--------------------
.. automethod:: pyhpo.set.HPOSet.toJSON

serialize
--------------------
.. automethod:: pyhpo.set.HPOSet.serialize


``BasicHPOSet`` class
*********************
.. autoclass:: pyhpo.set.BasicHPOSet
   :no-private-members:
   :no-special-members:


Class methods
************************

from_queries
--------------------
.. automethod:: pyhpo.set.HPOSet.from_queries

from_serialized
--------------------
.. automethod:: pyhpo.set.HPOSet.from_serialized
