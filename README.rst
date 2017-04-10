======
pdbook
======
*pdbook* is a Django app to display radiotherapy planning data in a nice
accessible tabular form, with an optional interpolation widget.

Screenshots
-----------

Quick Start
-----------
1. Add *pdbook* to your ``INSTALLED_APPS`` setting:

.. code-block:: python

    INSTALLED_APPS = [
        ...
        'pdbook',
    ]

2. Include the *pdbook* URL configuration in your project's ``urls.py``:

.. code-block:: python

    url(r'^pdb/' include(pdbook.urls')),

3. Run ``python manage.py migrate`` to create the *pdbook* models in the database.
4. Start the development server and visit http://127.0.0.1:8000/admin/ to add your *Machine*, *Beam* and *Data* (you'll need the Admin app enabled).
5. Visit http://127.0.0.1:8000/pdb/ to view the planning data.

Dependencies
------------
* `django <https://www.djangoproject.com>`_
* `numpy <https://www.numpy.org>`_
* `floatThead <https://github.com/mkoryak/floatThead>`_ (included)
* `Tablesaw <https://github.com/filamentgroup/tablesaw>`_ (included)
