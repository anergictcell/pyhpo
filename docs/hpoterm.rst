HPOTerm
====================
``HPOTerm`` instances contain all relevant information about a single HPO term. They are part of an ``Ontology`` and contain links to parental and offspring ``HPOTerm`` s.


``HPOTerm``
********************
.. autoclass:: pyhpo.term.HPOTerm
   :no-private-members:
   :no-special-members:


parent_of
----------
.. automethod:: pyhpo.term.HPOTerm.parent_of

child_of
----------
.. automethod:: pyhpo.term.HPOTerm.child_of

parent_ids
----------
.. automethod:: pyhpo.term.HPOTerm.parent_ids

common_ancestors
----------------
.. automethod:: pyhpo.term.HPOTerm.common_ancestors

count_parents
----------------
.. automethod:: pyhpo.term.HPOTerm.count_parents

longest_path_to_root
------------------------
.. automethod:: pyhpo.term.HPOTerm.longest_path_to_root

shortest_path_to_root
------------------------
.. automethod:: pyhpo.term.HPOTerm.shortest_path_to_root

shortest_path_to_parent
------------------------
.. automethod:: pyhpo.term.HPOTerm.shortest_path_to_parent

longest_path_to_bottom
------------------------
.. automethod:: pyhpo.term.HPOTerm.longest_path_to_bottom

path_to_other
------------------------
.. automethod:: pyhpo.term.HPOTerm.path_to_other

similarity_score
------------------------
.. automethod:: pyhpo.term.HPOTerm.similarity_score

toJSON
------------------------
.. automethod:: pyhpo.term.HPOTerm.toJSON
