======
pdbook
======
*pdbook* is a Django app to display radiotherapy planning data in an easily
accessible tabular form.

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

    url(r'^pdb/', include(pdbook.urls')),

3. Run ``python manage.py migrate`` to create the *pdbook* models in the database.
4. Start the development server and visit http://127.0.0.1:8000/admin/ to add
   your *Machines*, *Beams* and *Data* (you'll need the Admin app enabled).
5. Visit http://127.0.0.1:8000/pdb/ to view the planning data.

Adding Machines
~~~~~~~~~~~~~~~

* Login to the admin site and under the *Planning Data Book* section, click on
  'Machines' then 'Add Machine'.
* Fill out the fields for:

  * Machine Type: Required, one of 'Linear Accelerator', 'Orthovoltage Unit' or
  'Radiation Source'.
  * Manufacturer: Optional, the manufacturer of the machine.
  * Model: Optional, the model of the machine.
  * Serial Number: Optional, the machine's serial number.
  * Name: Required, the name to use for the machine. Must be unique.
  * Visible name: Required, the displayed name of the machine.
  * Description: Optional, the machine's description.
* Once all the required fields are filled out, click 'Save'.

Adding Beams
~~~~~~~~~~~~

* Login to the admin site and under the *Planning Data Book* section, click on
  'Machines' then click on the name of the machine you wish to add beams to.
* Under the 'Beams' section, click on 'Add another Beam'.
* Fill out the fields for:

  * Machine: Required, the machine this beam belongs to.
  * Modality: Required, the modality of the beam. One of 'MV Photons',
    'MeV Electrons', 'kV Photons' or 'Radioisotope'.
  * Energy: Required, the nominal energy of the beam.
  * Name: Required, the name to use for the beam. Must be unique.
  * Visible name: Required, the displayed name of the beam.
  * Description: Optional, a description of the beam.
* Once all the required fields are filled out, click 'Save'.

Adding Data
~~~~~~~~~~~

* Login to the admin site and under the *Planning Data Book* section, click on
  'Beams' then click on the name of the beam you wish to add data to.
* Under the 'Data' section, click on 'Add another Beam'.
* Fill out the fields for:

  * Beam: Required, the beam this data belongs to.
  * Data: Required, upload the CSV file containing the data.
  * Interpolation type: Required, the type of interpolation available for the data,
  one of 'No interpolation', '1D interpolation', '2D interpolation'.
  * Show Y Values: Optional, set to true to display both Y row labels and Y
  parameter values.
  * Name: Required, the name to use for the data. Must be unique.
  * Visible Name: Required, the displayed name for the data.
  * Description: Optional, a description of the data.
  * Data Source: Optional, a description of the source used for the data.
* Once all the required fields are filled out, click 'Save'

Dependencies
------------

* `django <https://www.djangoproject.com>`_
* `numpy <https://www.numpy.org>`_ and `scipy <https://www.scipy.org>`_ (for data interpolation)
* `jQuery <https://jquery.com>`_ (included)
* `floatThead <https://github.com/mkoryak/floatThead>`_ (included)
* `tablesaw <https://github.com/filamentgroup/tablesaw>`_ (included)
* `leanModal.js <https://leanmodal.finelysliced.com.au>`_ (included)
