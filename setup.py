import setuptools
import pyhpo

with open("README.rst", "r") as fh:
    long_description = fh.read()

PACKAGES = (
    'pyhpo',
)

CLASSIFIERS = [
    'Development Status :: 4 - Beta',
    'Intended Audience :: Developers',
    'Intended Audience :: Healthcare Industry',
    'Intended Audience :: Science/Research',
    'License :: OSI Approved :: MIT License',
    'Operating System :: OS Independent',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: Implementation :: CPython',
    'Programming Language :: Python :: Implementation :: PyPy',
    'Topic :: Scientific/Engineering :: Bio-Informatics',
    'Topic :: Scientific/Engineering :: Medical Science Apps.',
    'Topic :: Software Development :: Libraries :: Python Modules',
]


setuptools.setup(
    name='pyhpo',
    version=pyhpo.__version__,
    author=pyhpo.__author__,
    author_email="jonas.marcello@esbme.com",
    description="A Python package to work with the HPO Ontology",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    url="https://github.com/anergictcell/pyhpo",
    packages=PACKAGES,
    classifiers=CLASSIFIERS,
    python_requires='>=3.6',
    include_package_data=True,
    extras_require={
        'pandas': ['pandas'],
        'scipy': ['scipy'],
        'all': ['pandas', 'scipy']
    }
)
