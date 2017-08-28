import codecs
import csv
from heapq import nsmallest
import json
import re

from django.http import HttpResponse
from django.shortcuts import render, render_to_response, get_object_or_404

import numpy
from scipy.interpolate import interp1d, interp2d

from pdbook.models import Machine, Beam, Data


def index(request):
    """Return a page with the available Machines

    Parameters
    ----------
    request : django.core.handlers.wsgi.WSGIRequest
        The request

    Returns
    -------
    response : HttpResponse
    """
    machine_list = _get_machines()

    # Build response
    context = {}
    if machine_list:
        context = {'machine_list' : machine_list}

    return render(request, 'pdbook/index.html', context)

def get_machine(request, machine_slug):
    """Return a page with the available Beams for the selected Machine

    Parameters
    ----------
    request : django.core.handlers.wsgi.WSGIRequest
        The request
    machine_slug :str
        The slug for the selected Machine object

    Returns
    -------
    response : HttpResponse
    """
    m = get_object_or_404(Machine, slug=machine_slug)

    machine_list = _get_machines()
    beam_list = _get_beams(m)

    # Build response
    context = {}
    if beam_list:
        context = {'machine_list' : machine_list,
                   'beam_list' : beam_list,
                   'selected_machine' : m}

    return render(request, 'pdbook/index.html', context)

def get_beam(request, machine_slug, beam_slug):
    """Return a page with the available Data for the selected Beam

    Parameters
    ----------
    request : django.core.handlers.wsgi.WSGIRequest
        The request
    machine_slug :str
        The slug for the selected Machine object
    beam_slug : str
        The slug for the selected Beam object

    Returns
    -------
    response : HttpResponse
    """
    m = get_object_or_404(Machine, slug=machine_slug)
    b = get_object_or_404(Beam, slug=beam_slug, machine=m)

    machine_list = _get_machines()
    beam_list = _get_beams(m)
    data_list = _get_data(b)

    # Build response
    context = {}
    if beam_list:
        context = {'machine_list' : machine_list,
                   'beam_list' : beam_list,
                   'data_list' : data_list,
                   'selected_machine' : m,
                   'selected_beam' : b}

    return render(request, 'pdbook/index.html', context)

def get_data(request, machine_slug, beam_slug, data_slug):
    """Return a page with the table data for the selected Data.

    CSV File Special Characters
    ---------------------------
    The hash character, #, is used to denote comments, the caret character, ^,
    can be used to escape the delimiter character ','.

    CSV File Keywords
    -----------------
    DESCRIPTION=
        Optional. The description of the data. Supports HTML tags and unicode
        characters. Will override the django Data model's description field.
        Example: DESCRIPTION=Some sort of data
    SOURCE=
        Optional. The source of the data. Supports HTML tags and unicode
        characters. Will override the django Data model's data_source field.
        Example: SOURCE=Data source from somewhere
    X_TITLE=
        Optional. This is the displayed title for the X parameters. Supports
        HTML tags and unicode characters.
        Example: X_TITLE=Data source from somewhere
    X_HEADERS=
        Required, this is the displayed column labels. Supports HTML tags and
        unicode characters.
        Example: X_HEADERS=Depth<br/>(cm), 2 x 2, 3 x 3, 4 x 4, 5 x 5, 6 x 6,
                 7 x 7, 8 x 8, 9 x 9, 10 x 10
    X_FORMAT=
        Optional, must be a valid python new stype formatting string. Used to
        control the formatting of the X_VALUES values.
        Example: X_FORMAT={:.1f}
    X_VALUES=
        Required if 2D data. For f(x, y) this is the X-values/ If using
        interpolation then values should be ordered so they are increasing (and
        the tabular data ordered in a corresponding manner).
        Example: X_VALUES=2,3,4,5,6,7,8,9,10
    Y_TITLE=
        Optional. This is the displayed title for the Y parameters. Supports
        HTML tags and unicode characters.
        Example: Y_TITLE=Depth in water<br/>(cm)
    Y_HEADERS=
        Required, this is the displayed row labels. Supports HTML tags and
        unicode characters.
        Example: Y_HEADERS=2 x 2, 3 x 3, 4 x 4, 5 x 5, 6 x 6, 7 x 7, 8 x 8,
                 9 x 9, 10 x 10
    Y_FORMAT=
        Optional, must be a valid python new stype formatting string. Used to
        control the formatting of the Y_VALUES values.
        Example: Y_FORMAT={:.1f}
    Y_VALUES=
        Required if interpolation is supported if or Y_HEADERS is missing. For
        2D data f(x, y) or 1D data f(y), this is the Y-values. If using
        interpolation then values should be ordered so they are increasing (and
        then tabular data ordered in a corresponding manner).
        Example: Y_VALUES=2, 3, 4, 5, 6, 7, 8, 9, 10
    XY_FORMAT=
        Optional, must be a valid python new stype formatting string. Used to
        control the formatting of the XY_VALUES values.
        Example: XY_FORMAT={:.3f}
    XY_TYPE=
        Optional, must be either 'NUMERIC' or 'VERBATIM'. if the table data is
        to be displayed exactly as entered or contains non-numeric data then
        use 'VERBATIM'. Interpolation is only supported with NUMERIC type data.
        Example: XY_TYPE=VERBATIM

    All lines that don't start with a keyword will be considered to be part of
    the tabular data.

    Parameters
    ----------
    request : django.core.handlers.wsgi.WSGIRequest
        The request
    machine_slug :str
        The slug for the selected Machine object
    beam_slug : str
        The slug for the selected Beam object
    data_slug : str
        The slug for the selected Data object

    Returns
    -------
    response : HttpResponse
    """
    m = get_object_or_404(Machine, slug=machine_slug)
    b = get_object_or_404(Beam, slug=beam_slug, machine=m)
    d = get_object_or_404(Data, slug=data_slug, beam=b)

    machine_list = _get_machines()
    beam_list = _get_beams(m)
    data_list = _get_data(b)

    # Parse the data
    try:
        table_data = _read_data_file(d)
    except Exception as ex:
        table_data = 'There was an error reading the data file'

    if isinstance(table_data, str):
        context = {}
        if beam_list:
            context = {'machine_list' : machine_list,
                       'beam_list' : beam_list,
                       'data_list' : data_list,
                       'selected_machine' : m,
                       'selected_beam' : b,
                       'selected_data' : d,
                       'error_message' : table_data,
                       'description' : d.description,
                       'source' : d.data_source}
        response = render(request, 'pdbook/index.html', context)
    else:
        context = {}
        if beam_list:
            context = {'machine_list' : machine_list,
                       'beam_list' : beam_list,
                       'data_list' : data_list,
                       'selected_machine' : m,
                       'selected_beam' : b,
                       'selected_data' : d}
        if table_data:
            context.update(table_data)
        response = render(request, 'pdbook/index.html', context)

    return response

def interpolate(request, machine_slug, beam_slug, data_slug):
    """Returns the results from the interpolation widget

    Parameters
    ----------
    request : django.core.handlers.wsgi.WSGIRequest
        The interpolation request
    machine_slug :str
        The slug for the selected Machine object
    beam_slug : str
        The slug for the selected Beam object
    data_slug : str
        The slug for the selected Data object to be interpolated

    Returns
    -------
    result : dict
        The result of the interpolation. For 1D keys are 'x_value_ok',
        'table_type', 'y_values', 'table_data'.
        For 2D keys are 'y_value_ok', 'x_value_ok', 'table_type', 'x_values',
        'y_values', 'table_data'.
    """
    m = get_object_or_404(Machine, slug=machine_slug)
    b = get_object_or_404(Beam, slug=beam_slug, machine=m)
    d = get_object_or_404(Data, slug=data_slug, beam=b)

    data = _read_data_file(d)

    if request.POST['interp_type'] == '1D':
        y = None
        if 'y_value' in request.POST.keys() and request.POST['y_value']:
            y = float(request.POST['y_value'])

        result = _do_interpolate_1d(y, data)
    elif request.POST['interp_type'] == '2D':
        x = None
        if 'x_value' in request.POST.keys() and request.POST['x_value']:
            x = float(request.POST['x_value'])

        y = None
        if 'y_value' in request.POST.keys() and request.POST['y_value']:
            y = float(request.POST['y_value'])

        result = _do_interpolate_2d(x, y, data)
    else:
        result = Http404('No such interpolation type')

    return result

def _get_machines():
    """Return a list of Machine model objects, sorted by name"""
    return Machine.objects.order_by('-name')[:].reverse

def _get_beams(machine):
    """Return a list of Beam model objects for Machine `machine`, sorted by modality and name"""
    return Beam.objects.filter(machine=machine).order_by('modality', '-name')[:].reverse

def _get_data(beam):
    """Return a list of Data model objects for Beam `beam`, sorted by name"""
    return Data.objects.filter(beam=beam).order_by('-name')[:].reverse

def _parse_csv_row(row):
    """Parse the CSV row, returning variables and values.

    Parameters
    ----------
    row : list of str
        A non-empty line from the CSV data file with starting and ending white
        space stripped out.

    Returns
    -------
    str, list of str or None
        The variable name, and list of variable values. If the line contains
        no variable then returns None.
    """
    # Allowed variables
    variables = ['X_TITLE', 'X_HEADERS', 'X_VALUES', 'X_FORMAT',
                 'Y_TITLE', 'Y_HEADERS', 'Y_VALUES', 'Y_FORMAT',
                 'XY_FORMAT', 'XY_TYPE', 'DESCRIPTION', 'SOURCE']

    if '=' in row[0]:
        split_item = row[0].split('=')
        variable_name = split_item[0]
        variable_values = [split_item[1]]

        if variable_name not in variables:
            raise ValueError('The CSV data file contains an unknown variable.')

        if row[1:]:
            variable_values.extend(row[1:])

        return variable_name, variable_values

    return None, None

def _skip_csv_comments(rows, commentchar='#'):
    """Skip everything following `commentchar`.

    Parameters
    ----------
    rows : list of list of str
        The CSV file contents.
    commentchar : str
        The character that indicates a comment follows. Anything after this
        character will be removed.

    Yields
    ------
    list of str
        The CSV row contents without comments.
    """
    pattern = re.compile(r'\s*{}.*$'.format(commentchar))
    for row in rows:
        row = re.sub(pattern, '', row).strip()
        if row:
            yield row

def _read_data_file(data_obj):
    """Parse the uploaded data file for the contents

    Special Characters
    ------------------
    The hash character, #, is used to denote comments, the caret character, ^,
    can be used to escape the delimiter character ','.

    Parameters
    ----------
    data : django_rt_pdb.models.Data

    Returns
    -------
    dict
        A dict containing the table data
    """

    data = {'X_TITLE' : '', 'X_HEADERS' : '', 'X_FORMAT' : '{}', 'X_VALUES' : [],
            'Y_TITLE' : '', 'Y_HEADERS' : '', 'Y_FORMAT' : '{}', 'Y_VALUES' : [],
            'XY_FORMAT' : '{}', 'XY_VALUES' : [], 'XY_TYPE' : ['NUMERIC'],
            'DESCRIPTION' : '', 'SOURCE' : ''}

    with open(data_obj.data.path, 'r') as csvfile:
        reader = csv.reader(_skip_csv_comments(csvfile), quotechar='|', escapechar='^')
        for row in reader:
            try:
                var_name, var_values = _parse_csv_row(row)
            except ValueError:
                msg = 'Unable to parse the data file'
                return msg

            if (var_name, var_values) == (None, None):
                if data['XY_TYPE'][0].upper() == 'NUMERIC':
                    row[:] = [float(val) for val in row]
                data['XY_VALUES'].append(row)
            else:
                data[var_name] = var_values

    data['DESCRIPTION'] = ', '.join(data['DESCRIPTION'])
    data['DESCRIPTION'] = data['DESCRIPTION'].encode('utf-8')
    data['DESCRIPTION'] = data['DESCRIPTION'].decode('unicode-escape')
    data['SOURCE'] = ', '.join(data['SOURCE'])
    data['SOURCE'] = data['SOURCE'].encode('utf-8')
    data['SOURCE'] = data['SOURCE'].decode('unicode-escape')


    if data_obj.description:
        data['DESCRIPTION'] = data_obj.description
    if data_obj.data_source:
        data['SOURCE'] = data_obj.data_source

    if data['X_TITLE']:
        x_title = ', '.join(data['X_TITLE'])
    else:
        x_title = ''

    if data['Y_TITLE']:
        y_title = ', '.join(data['Y_TITLE'])
    else:
        y_title = ''

    # Get the column labels, formatting if necessary
    if data['X_HEADERS'] != '':
        column_labels = data['X_HEADERS']
        column_labels[:] = [val.encode('utf-8') for val in column_labels]
        column_labels[:] = [val.decode('unicode-escape') for val in column_labels]
    elif data['X_VALUES'] != []:
        column_labels = [data['X_FORMAT'][0].format(float(val)) for val in data['X_VALUES']]
    else:
        msg = 'The file must have either non-blank X_HEADERS or X_VALUES values'
        return msg

    # Get the row labels, formatting if necessary
    if data['Y_HEADERS'] != ['']:
        row_labels = data['Y_HEADERS']
        row_labels[:] = [val.encode('utf-8') for val in row_labels]
        row_labels[:] = [val.decode('unicode-escape') for val in row_labels]
    elif data['Y_VALUES'] != ['']:
        row_labels = [data['Y_FORMAT'][0].format(float(val)) for val in data['Y_VALUES']]
    else:
        msg = 'The file must have either non-blank Y_HEADERS or Y_VALUES values'
        return msg

    if data['XY_VALUES'] != [] and data['XY_TYPE'][0].upper() == 'NUMERIC':
        # Apply the XY format to the table data
        values_out = []
        for xy_row, y_val in zip(data['XY_VALUES'], row_labels):
            new_row = [data['XY_FORMAT'][0].format(xy) for xy in xy_row]
            new_row.insert(0, y_val)
            values_out.append(new_row)

        # Force show the Y VALUES if available and user chooses option
        if data_obj.show_y_values and data['Y_VALUES'] != ['']:
            for xy_row, y_val in zip(values_out, data['Y_VALUES']):
                xy_row.insert(1, y_val)
    elif data['XY_VALUES'] != []:
        values_out = data['XY_VALUES']
    else:
        msg = 'The file has no tabular data'
        return msg

    return {'column_labels' : column_labels,
             'table_data' : values_out,
             'x_title' : x_title,
             'x_values' : data['X_VALUES'],
             'y_title' : y_title,
             'y_values' : data['Y_VALUES'],
             'description' : data['DESCRIPTION'],
             'source' : data['SOURCE'],
             'x_format' : data['X_FORMAT'][0],
             'y_format' : data['Y_FORMAT'][0],
             'xy_format' : data['XY_FORMAT'][0],
             }

def _do_interpolate_1d(y, data):
    """Return a HttpResponse containing the results from interpolating `data` at `y`.

    The results will be formatted in accordance with the formats specified
    in the CSV file.

    Parameters
    ----------
    y :
        The Y value to perform the interpolation with
    data :
        The data to interpolate

    Returns
    -------
    HttpResponse
    """
    y_value_ok = False
    y_arr = numpy.asarray(data['y_values'], dtype=numpy.float)
    if y and (min(y_arr) <= y <= max(y_arr)):
        y_value_ok = True
        y_neighbours = nsmallest(2, y_arr, key=lambda k: abs(k - y))
        y_neighbours.sort()

    out = [val[1] for val in data['table_data']]
    out = numpy.asarray(out, dtype=numpy.float)
    interp_func = interp1d(y_arr, out, kind='linear')

    y_vals = []
    if y_value_ok:
        y_vals = [y_neighbours[0], y, y_neighbours[1]]

    result = [data['xy_format'].format(interp_func(val).tolist()) for val in y_vals]

    y_vals[:] = [data['y_format'].format(val) for val in y_vals]
    
    result = {'y_value_ok' : y_value_ok,
              'table_type' : '1D',
              'y_values' : y_vals,
              'table_data' : result}

    return HttpResponse(json.dumps(result), content_type="application/json")

def _do_interpolate_2d(x, y, data):
    """Return a HttpResponse containing the results from interpolating `data` at (`x`, `y`).

    The results will be formatted in accordance with the formats specified
    in the CSV file.

    Parameters
    ----------
    x:
        The X value to perform the interpolation with
    y :
        The Y value to perform the interpolation with
    data :
        The data to interpolate

    Returns
    -------
    HttpResponse
    """
    x_value_ok = False
    y_value_ok = False

    x_arr = numpy.asarray(data['x_values'], dtype=numpy.float)
    y_arr = numpy.asarray(data['y_values'], dtype=numpy.float)

    if x and (min(x_arr) <= x <= max(x_arr)):
        x_value_ok = True

    if y and (min(y_arr) <= y <= max(y_arr)):
        y_value_ok = True

    x_neighbours = nsmallest(2, x_arr, key=lambda k: abs(k - x))
    x_neighbours.sort()
    y_neighbours = nsmallest(2, y_arr, key=lambda k: abs(k - y))
    y_neighbours.sort()

    out = []
    for row in data['table_data']:
        out.append(row[1:])

    out = numpy.asarray(out, dtype=numpy.float)
    interp_func = interp2d(x_arr, y_arr, out, kind='linear')

    x_vals = [x_neighbours[0], x, x_neighbours[1]]
    y_vals = [y_neighbours[0], y, y_neighbours[1]]

    result = []
    for jj in y_vals:
        result.append([data['xy_format'].format(interp_func(ii, jj)[0]) for ii in x_vals])

    x_vals[:] = [data['x_format'].format(val) for val in x_vals]
    y_vals[:] = [data['y_format'].format(val) for val in y_vals]

    result = {'y_value_ok' : y_value_ok,
              'x_value_ok' : x_value_ok,
              'table_type' : '2D',
              'x_values' : x_vals,
              'y_values' : y_vals,
              'table_data' : result}

    return HttpResponse(json.dumps(result), content_type="application/json")
