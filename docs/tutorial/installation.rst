Installation
============

PIP / PyPI
----------

.. include:: ../../README.rst
    :start-after: Getting started
                  ===============
    :end-before: Usage example
                 =============

From source
-----------

You can also install **PyHPO** from source by cloning the git repository:

.. code:: bash

    git clone https://github.com/Centogene/pyhpo.git


I recommend to use a virtual environment to use **PyHPO**:

.. code:: bash

    cd pyhpo
    virtualenv venv
    source ./venv/bin/activate


Install dependencies:

.. code:: bash

    pip install -r requirements.txt



Development / Contributing
--------------------------

If you want to contribute to **PyHPO** development, first install from source (see above),
then install all dev dependencies:

.. code:: bash

    pip install -r requirements_dev.txt

Make sure to install ``mypy`` and linter, such as ``flake8`` or ``ruff``.
