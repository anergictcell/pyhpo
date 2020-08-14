Handling master data
====================
The ``PyHPO`` package relies on several master data files provided by the HPO Consortium.
The package always includes those files in the ``data`` subfolder. Even though I try to update ``PyHPO`` with every HPO data update, I might be behind sometimes and can't guarantee long-term support. 

Here you will find the easiest procedures to update the data yourself.

``PyHPO`` requires three data files

* ``HPO_ONTOLOGY``: This is the ``obo`` file describing the HPO Ontology. Let's all hope that the file format will never change. This file is mandatory
* ``HPO_GENE``: This is a custom file provided by the HPO consortium that contains links between HPO-Terms and genes. 
* ``HPO_PHENO``: This is a custom file provided by the HPO consortium that contains links between HPO-Terms and diseases.

``HPO_GENE`` and ``HPO_PHENO`` files are not mandatory per-se. The ontology itself will work without them, but the HPO Terms will not be annotated. That means, you won't be able to calculate the information content, similarity and some other features.


``Auto update``
********************
You can try to auto-update the data from the HPO Jenkins servers and OBO-Library via the built-in script
``update_data.py``.


.. code:: python
    
    from pyhpo.update_data import download_data
    download_data()


Error handling
---------------
If the URLs of the files change, you will need to modify the URLS dict in the ``update_data``  module.

.. code:: python
    
    from pyhpo.update_data import download_data
    download_data.URLS['HPO_ONTOLOGY'] = 'https://custom-url.com'
    download_data()


Sometimes, the HPO-Disease associations file is improperly generated and the header start with ``#``. During Annotation parsing, ``PyHPO`` removes all outcomment rows.
So you might have to manually change the file from::

    #description: HPO annotations for rare diseases [7801: OMIM; 47: DECIPHER; 3958 ORPHANET]
    #date: 2020-08-11
    #tracker: https://github.com/obophenotype/human-phenotype-ontology
    #HPO-version: http://purl.obolibrary.org/obo/hp.obo/hp/releases/2020-08-11/hp.obo.owl
    #DatabaseID      DiseaseName     Qualifier       HPO_ID  Reference       Evidence        Onset   Frequency       Sex     Modifier        Aspect  Biocuration

to::

    #description: HPO annotations for rare diseases [7801: OMIM; 47: DECIPHER; 3958 ORPHANET]
    #date: 2020-08-11
    #tracker: https://github.com/obophenotype/human-phenotype-ontology
    #HPO-version: http://purl.obolibrary.org/obo/hp.obo/hp/releases/2020-08-11/hp.obo.owl
    DatabaseID      DiseaseName     Qualifier       HPO_ID  Reference       Evidence        Onset   Frequency       Sex     Modifier        Aspect  Biocuration


``Manual update``
********************
Of course you can manually download the files and replace them in the ``data`` subfolder. However, this is not recommended, as it might cause issues and is not easy to undo.

Instead, you can download the files and store them somewhere in your home folder. Upon initilizing the :class:`pyhpo.ontology.OntologyClass`, you can specify the path to the files.

.. code:: python

    from pyhpo.ontology import Ontology

    _ = Ontology(data_folder='/path/to/master/data')

