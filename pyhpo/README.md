# PyHPO
A Python library to work with, analyze, filter and inspect the Human Phenotype Ontology

It allows working on individual terms ``HPOTerm``, a set of terms ``HPOSet`` and the full ``Ontology``.

Internally the ontology is represented as a branched linked list, every term contains pointers to its parent and child terms. This allows fast tree traversal functioanlity.

The library is helpful for discovery of novel gene-disease associations and GWAS data analysis studies. At the same time, it can be used for oragnize clinical information of patients in research or diagnostic settings.

It provides an interface to create ``Pandas Dataframe`` from its data, allowing integration in already existing data anlysis tools.

## HPOTerm
An individual ``HPOTerm`` contains all info about itself as well as pointers to its parents and its children. You can access its information-content, calculate similarity scores to other terms, find the shortest or longes connection between two terms. List all associated genes or diseases, etc.

## HPOSet
An ``HPOSet`` can be used to represent e.g. a patient's clinical information. It allows some basic filtering and comparisons to other ``HPOSet``s.

## Ontology
The ``Ontology`` represents all HPO terms and their connections and associations. It also contains pointers to associated genes and disease.


# Installation / Setup
This is not yet defined. I'm planning on adding PyHPO to PyPy, so you can install it via pip. For now, you need to install it manually. The easiest way to do so is:

```bash
git clone https://github.com/anergictcell/pyhpo.git

ln -s pyhpo <PYTHON-LIB-PATH>
```

