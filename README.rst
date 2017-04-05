===
pdb
===
pdb is a Django app to create and display radiotherapy planning data in nice
accessible tabular form, with an optional interpolation widget.

Quick Start
-----------
1. Add "pdb" to your INSTALLED_APPS setting::

    INSTALLED_APPS = [
        ...
        'pdb',
    ]

2. Include the pdbook URLconf in your project urls.py::

    url(r'^pdb/' include(pdb.urls')),
    
3. Run `python manage.py migrate` to create the pdb models.

4. Start the development server and visit http://127.0.0.1:8000/admin/ to create a
    pdb (you'll need the Admin app enabled).
    
5. Visit http://127.0.0.1:8000/pdb/ to view the planning data tables.
