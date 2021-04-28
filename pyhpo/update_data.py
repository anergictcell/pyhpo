import os
import urllib.request
import logging
from typing import Optional

from pyhpo.parser.obo import FILENAME as hpo_file
from pyhpo.parser.genes import FILENAME as gene_file
from pyhpo.parser.diseases import FILENAME as pheno_file


"""
Downloads the required data for HPO Ontology and the annotations
"""
logger = logging.getLogger(__name__)


URLS = {
    'HPO_ONTOLOGY': 'http://purl.obolibrary.org/obo/hp.obo',
    'HPO_GENE': 'http://purl.obolibrary.org/obo/hp/hpoa/phenotype_to_genes.txt',  # noqa: E501
    'HPO_PHENO': 'http://purl.obolibrary.org/obo/hp/hpoa/phenotype.hpoa'
}

FILENAMES = {
    'HPO_ONTOLOGY': hpo_file,
    'HPO_GENE': gene_file,
    'HPO_PHENO': pheno_file
}


def make_backup(filename: str) -> None:
    logger.debug('Backup not yet implemented')


def download_data(data_dir: Optional[str] = None) -> None:
    if data_dir is None:
        data_dir = os.path.realpath(os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            'data'
        ))
    else:
        data_dir = os.path.realpath(data_dir)

    logger.debug('Downloading data to %s', data_dir)

    for url in URLS:
        logger.debug('Downloading %s', url)
        filename = os.path.join(data_dir, FILENAMES[url])
        if os.path.exists(filename):
            logger.warning('%s exists already. Backing up old data', filename)
            make_backup(filename)
        urllib.request.urlretrieve(
            URLS[url],
            filename
        )
