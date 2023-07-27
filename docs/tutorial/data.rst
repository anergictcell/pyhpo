Masterdata
----------

**PyHPO** ships with a full version of the HP ontology, including gene and disease associations. I try to keep this data up to date, but will frequently fall behind on the release schedule.

To build the ontology, the following 3 files are needed from the HPO masterdata:

* ``http://purl.obolibrary.org/obo/hp.obo``
* ``http://purl.obolibrary.org/obo/hp/hpoa/phenotype_to_genes.txt``
* ``http://purl.obolibrary.org/obo/hp/hpoa/phenotype.hpoa``


Updating to the most recent version
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To update to the most recent version of the masterdata, you can use the following Python script:

.. code:: python

    from pyhpo.update_data import download_data

    download_data()


Manually updating the masterdata
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

By default, the HPO masterdata is stored along the installed library. You *could* manually update the files in there, but that is not recommended.
Instead, you can download the HPO masterdata into a local folder and specify that folder during instantiation of the Ontology:

.. code:: python

    from pyhpo import Ontology

    _ = Ontology("/path/to/folder/with/masterdata/")



