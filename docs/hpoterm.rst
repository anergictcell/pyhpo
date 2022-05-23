HPOTerm
====================
``HPOTerm`` instances contain all relevant information about a single HPO term. They are part of an ``Ontology`` and contain links to parental and offspring ``HPOTerm`` s.


``HPOTerm``
********************
.. autoclass:: pyhpo.term.HPOTerm
   :no-private-members:
   :no-special-members:

Attributes
----------
   .. autoattribute:: pyhpo.term.HPOTerm.id
   .. autoattribute:: pyhpo.term.HPOTerm.name
   .. autoattribute:: pyhpo.term.HPOTerm.information_content
   .. autoattribute:: pyhpo.term.HPOTerm.comment
   .. autoattribute:: pyhpo.term.HPOTerm.definition
   .. autoattribute:: pyhpo.term.HPOTerm.synonym
   .. autoattribute:: pyhpo.term.HPOTerm.parents
   .. autoattribute:: pyhpo.term.HPOTerm.children
   .. autoattribute:: pyhpo.term.HPOTerm.genes
   .. autoattribute:: pyhpo.term.HPOTerm.omim_diseases
   .. autoattribute:: pyhpo.term.HPOTerm.orpha_diseases
   .. autoattribute:: pyhpo.term.HPOTerm.decipher_diseases

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


``InformationContent``
**********************
.. autoclass:: pyhpo.term.InformationContent
   :no-private-members:
   :no-special-members:

Default attributes
------------------
   .. autoattribute:: pyhpo.term.InformationContent.gene
   .. autoattribute:: pyhpo.term.InformationContent.omim
   .. autoattribute:: pyhpo.term.InformationContent.orpha
   .. autoattribute:: pyhpo.term.InformationContent.decipher


set_custom
----------
.. automethod:: pyhpo.term.InformationContent.set_custom
