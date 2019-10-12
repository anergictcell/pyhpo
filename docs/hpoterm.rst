HPOTerm
====================
``HPOTerm`` instances contain all relevant information about a single HPO term. They are part of an ``Ontology`` and contain links to parental and offspring ``HPOTerm`` s.


``HPOTerm``
********************
.. autoclass:: pyhpo.term.HPOTerm
   :no-private-members:
   :no-special-members:

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

hierarchy
----------------
.. automethod:: pyhpo.term.HPOTerm.hierarchy

print_hierarchy
----------------
.. automethod:: pyhpo.term.HPOTerm.print_hierarchy

similarity_score
------------------------
.. automethod:: pyhpo.term.HPOTerm.similarity_score

Class methods
************************

id_from_string
------------------------
.. automethod:: pyhpo.term.HPOTerm.id_from_string

parse_synonym
------------------------
.. automethod:: pyhpo.term.HPOTerm.parse_synonym

