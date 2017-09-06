======
pdbook
======
*pdbook* is a Django app to display radiotherapy planning data in an easily
accessible tabular form. It should only be used for internal sites and is
not recommended for use on anything public facing.

Screenshots
-----------

<img src=samples/linac-6X-pdd.png width="30%" />
<img src=samples/linac-6X-tpr-interp.png width="30%" />
<img src=samples/ortho-30-bsf-info.png width="30%" />

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

Tabular Data CSV File Format
----------------------------
Tabular data should stored in CSV files (with comma ',' as the delimiter character,
caret '^' as an escape character and hash '#' as a comment character). See the
`samples <samples>`_ directory for example CSV files.

CSV File Keywords
~~~~~~~~~~~~~~~~~

DESCRIPTION=
    Optional. The description of the data. Supports HTML tags and unicode
    characters. Will override the *Data* model's **description** field. Any commas
    in the value will be automatically escaped.
    
    ::

        DESCRIPTION=Some sort of data taken from somewhere
SOURCE=
    Optional. The source of the data. Supports HTML tags and unicode
    characters. Will override the *Data* model's **data_source** field. Any commas
    in the value will be automatically escaped.
    
    ::

        SOURCE=Ata et al, <i>"Interesting data"</i>, Journal of Data, <b>8</b>, pp 2901-3 (1999)
X_TITLE=
    Optional. This is the displayed title for the X parameter. Supports
    HTML tags and unicode characters.
    
    ::

        X_TITLE=Field Size
X_HEADERS=
    Required, this is the displayed column labels. Supports HTML tags and
    unicode characters.
    
    ::

        X_HEADERS=Depth<br/>(cm), 2 x 2, 3 x 3, 4 x 4, 5 x 5, 6 x 6, 7 x 7, 8 x 8, 9 x 9, 10 x 10
X_FORMAT=
    Optional, must be a valid python new style formatting string. Used to
    control the formatting of the X_VALUES values.
    
    ::

        X_FORMAT={:.1f}
X_VALUES=
    Required if 2D data. For f(x, y) these are the X parameter values. If using
    interpolation then values should be ordered so they are increasing (and
    the tabular data ordered to match).
    
    ::

        X_VALUES=2,3,4,5,6,7,8,9,10
Y_TITLE=
    Optional. This is the displayed title for the Y parameter. Supports
    HTML tags and unicode characters.
    
    ::

        Y_TITLE=Depth in water<br/>(cm)
Y_HEADERS=
    Required, these are the displayed row labels. Supports HTML tags and
    unicode characters.

    ::

        Y_HEADERS=2 x 2, 3 x 3, 4 x 4, 5 x 5, 6 x 6, 7 x 7, 8 x 8, 9 x 9, 10 x 10
Y_FORMAT=
    Optional, must be a valid python new style formatting string. Used to
    control the formatting of the Y_VALUES values.
    
    ::

        Y_FORMAT={:.1f}
Y_VALUES=
    Required if interpolation is supported if or Y_HEADERS is missing. For
    2D data f(x, y) or 1D data f(y), these are the Y parameter values. If using
    interpolation then values should be ordered so they are increasing (and
    the tabular data ordered to match).
    
    ::

        Y_VALUES=2, 3, 4, 5, 6, 7, 8, 9, 10
XY_FORMAT=
    Optional, must be a valid python new style formatting string. Used to
    control the formatting of the tabular data values.
    
    ::

        XY_FORMAT={:.3f}
XY_TYPE=
    Optional, must be either 'NUMERIC' or 'VERBATIM', defaults to 'NUMERIC'.
    If the table data is to be displayed exactly as entered or contains
    non-numeric data then use 'VERBATIM'. Interpolation is only supported with
    NUMERIC type data.
    
    ::

        XY_TYPE=VERBATIM

All lines that don't start with a keyword will be considered to be part of
the tabular data as f(x, y) or f(y).


Dependencies
------------

* `django <https://www.djangoproject.com>`_
* `numpy <https://www.numpy.org>`_ and `scipy <https://www.scipy.org>`_ (for data interpolation)
* `jQuery <https://jquery.com>`_ (included)
* `floatThead <https://github.com/mkoryak/floatThead>`_ (included)
* `tablesaw <https://github.com/filamentgroup/tablesaw>`_ (included)
* `leanModal.js <https://leanmodal.finelysliced.com.au>`_ (included)
