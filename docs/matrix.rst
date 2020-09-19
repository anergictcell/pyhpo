Matrix
======

To reduce overhead and external dependencies, ``PyHPO`` uses an internal data matrix, ``pyhpo.Matrix``. It is used for row- and columnwise comparisons of HPOSets.

``Matrix`` should not be used for other purposes, as it does not contain much error handling and expects conform clients.


``Matrix`` class
*****************
.. autoclass:: pyhpo.matrix.Matrix
   :no-private-members:
   :no-special-members:

