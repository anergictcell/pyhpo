# -*- coding: utf-8 -*-

"""PyHPO: A library for handling the Human Phenotype Ontology"""

from pyhpo.term import HPOTerm
from pyhpo.ontology import Ontology, OntologyClass
from pyhpo.set import HPOSet
from pyhpo.annotations import Annotation, GeneSingleton, DiseaseSingleton
from pyhpo.annotations import OmimDisease, OrphaDisease, DecipherDisease
from pyhpo import config

# The following info will be used by setup.py and sphinx documentation
__author__ = 'Jonas Marcello'
__version__ = '3.2.2'

__all__ = (
    'Annotation',
    'HPOTerm',
    'HPOSet',
    'Ontology',
    'OntologyClass',
    'GeneSingleton',
    'DiseaseSingleton',
    'OmimDisease',
    'OrphaDisease',
    'DecipherDisease',
    'config'
)
