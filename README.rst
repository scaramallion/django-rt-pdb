======
pdbook
======
pdbook is a Django app to create and display radiotherapy planning data in nice
accessible tabular form, with an optional interpolation widget.

Quick Start
-----------
1. Add `pdbook` to your INSTALLED_APPS setting:
```python
    INSTALLED_APPS = [
        ...
        'pdbook',
    ]
```

2. Include the pdbook URLconf in your project `urls.py`:
```python
    url(r'^pdb/' include(pdbook.urls')),
```

3. Run `python manage.py migrate` to create the pdbook models.

4. Start the development server and visit http://127.0.0.1:8000/admin/ to add
    Machine, Beam and Data (you'll need the Admin app enabled).
    
5. Visit http://127.0.0.1:8000/pdb/ to view the planning data.

Dependencies
------------
* `django <https://www.djangoproject.com>`_
* `floatThead <https://github.com/mkoryak/floatThead>`_
* `Tablesaw <https://github.com/filamentgroup/tablesaw>`_
