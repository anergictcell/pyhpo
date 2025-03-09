Annotations
===========

The ``Annotations`` module contains the gene and disease associations of HPOTerms.

.. code::

    from pyhpo import Ontology
    from pyhpo.annotations import Omim, Orpha

    Ontology()

    # All genes and diseases can be accessed through the Ontology

    for gene in Ontology.genes:
        print(gene.name)
        # >> "EZH2"
        # ...

    for orpha in Ontology.orpha_diseases:
        print(orpha.id)
        # >> 231401
        # ...


    # or accessed directly from the `Orpha`, `Omim`, `Gene` class

    orpha_disease = Orpha.get(77260)
    omim_disease = Omim.get(230900)


    # Annotations can be converted to `HPOSet`

    orpha_set = orpha_disease.hpo_set()
    omim_set = omim_disease.hpo_set()

    similarity = orpha_set.similarity(omim_set)
    print(similarity)
    # >> 0.6620065792484546


.. class:: GeneSingleton

    An instance of a gene, associated to several :class:`pyhpo.term.HPOTern`.

    .. note::

        Since version 4.0 genes do not contain references to HPOTerms transitively, i.e. only directly
        associated HPOTerms are linked to the gene.

    .. attribute:: id

        :Return Type: ``int``

        :Returns: The HGNC ID of the gene

    .. attribute:: name

        :Return Type: ``str``

        :Returns: The HUGO gene synbol of the gene

    .. attribute:: symbol

        :Return Type: ``str``

        :Returns: The HUGO gene synbol of the gene (alias of :attr:`GeneSingleton.name`)

    .. attribute:: hpo

        :Return Type: ``set(int)``

        :Returns: The HPO-IDs of all associated :class:`pyhpo.term.HPOTerm` s

    .. autofunction:: pyhpo.annotations.Annotation.toJSON

    .. autofunction:: pyhpo.annotations.Annotation.hpo_set


.. class:: Gene

    ``Gene`` holds all :class:`GeneSingleton` instances and ensures they are not duplicated.
    It does not need to be instantiated, as it is already created as a singleton during the
    setup of the Ontology.

    .. autofunction:: pyhpo.annotations.Gene.get
    .. autofunction:: pyhpo.annotations.Gene.__call__


.. class:: OmimDisease

    An instance of an Omim disease, associated to several :class:`pyhpo.term.HPOTerm`.

    .. attribute:: id

        :Return Type: ``int``

        :Returns: The Omim ID

    .. attribute:: name

        :Return Type: ``str``

        :Returns: The Omim disease name

    .. attribute:: hpo

        :Return Type: ``set(int)``

        :Returns: The HPO-ID of all associated :class:`HPOTerm` s

    .. autofunction:: pyhpo.annotations.Annotation.toJSON

    .. autofunction:: pyhpo.annotations.Annotation.hpo_set


.. class:: Omim

    ``Omim`` holds all :class:`OmimDisease` instances and ensures they are not duplicated.
    It does not need to be instantiated, as it is already created as a singleton during the
    setup of the Ontology.

   .. autofunction:: pyhpo.annotations.DiseaseDict.get

        :Return type: :class:`OmimDisease`

   .. autofunction:: pyhpo.annotations.DiseaseDict.__call__


.. class:: OrphaDisease

    An instance of an Orpha disease, associated to several :class:`pyhpo.term.HPOTerm`.

    .. attribute:: id

        :Return Type: ``int``

        :Returns: The Orpha ID

    .. attribute:: name

        :Return Type: ``str``

        :Returns: The Orpha disease name

    .. attribute:: hpo

        :Return Type: ``set(int)``

        :Returns: The HPO-ID of all associated :class:`HPOTerm` s

    .. autofunction:: pyhpo.annotations.Annotation.toJSON

    .. autofunction:: pyhpo.annotations.Annotation.hpo_set


.. class:: Orpha

    ``Orpha`` holds all :class:`OrphaDisease` instances and ensures they are not duplicated.
    It does not need to be instantiated, as it is already created as a singleton during the
    setup of the Ontology.

    .. autofunction:: pyhpo.annotations.DiseaseDict.get

        :Return type: :class:`OrphaDisease`

   .. autofunction:: pyhpo.annotations.DiseaseDict.__call__


.. class:: DecipherDisease

    An instance of an Decipher disease, associated to several :class:`pyhpo.term.HPOTerm`.

   .. attribute:: id

        :Return Type: ``int``

      :Returns: The Decipher ID

    .. attribute:: name

        :Return Type: ``str``

        :Returns: The Decipher disease name

    .. attribute:: hpo

        :Return Type: ``set(int)``

        :Returns: The HPO-ID of all associated :class:`HPOTerm` s

    .. autofunction:: pyhpo.annotations.Annotation.toJSON

    .. autofunction:: pyhpo.annotations.Annotation.hpo_set


.. class:: Decipher

    ``Decipher`` holds all :class:`DecipherDisease` instances and ensures they are not duplicated.

    .. autofunction:: pyhpo.annotations.DiseaseDict.get

        :Return type: :class:`DecipherDisease`

   .. autofunction:: pyhpo.annotations.DiseaseDict.__call__
