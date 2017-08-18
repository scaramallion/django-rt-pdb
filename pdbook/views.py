import json

from django.http import HttpResponse
from django.shortcuts import render, render_to_response
from django.template import RequestContext
from django.views.decorators.csrf import csrf_protect

from pdbook.models import Machine, Beam, Data


def index(request):
    """Return a page with a list of available Machines"""
    #m = get_object_or_404(Machine, slug=slug)
    
    # Get all machines
    machine_list = _get_machines()

    # Build response
    context = {}
    if machine_list:
        context = {'machine_list' : machine_list}

    return render(request, 'pdbook/index.html', context)

def get_machine(request, machine_slug):
    """Return a page with a list of available Beams for the selected Machine."""
    # Get all machines
    machine_list = _get_machines()

    # Get selected machine
    # FIXME: use id instead
    m = Machine.objects.get(slug=machine_slug)

    # Get all beams for the selected machine
    beam_list = _get_beams(m)

    # Build response
    context = {}
    if beam_list:
        context = {'machine_list' : machine_list,
                   'beam_list' : beam_list,
                   'selected_machine' : m}

    return render(request, 'pdbook/index.html', context)

def get_beam(request, machine_slug, beam_slug):
    """Return a page with a list of available Data for the selected Beam."""
    # Get all machines
    machine_list = _get_machines()

    # Get selected machine
    m = Machine.objects.get(slug=machine_slug)

    # Get all beams for the selected machine
    beam_list = _get_beams(m)

    # Get the selected beam
    b = Beam.objects.get(slug=beam_slug, machine=m)

    # Get all data for the selected beam
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
    """Return a page with the table data for the selected Data."""
    # Get all machines
    machine_list = _get_machines()

    # Get selected machine
    m = Machine.objects.get(slug=machine_slug)

    # Get all beams for the selected machine
    beam_list = _get_beams(m)

    # Get the selected beam
    b = Beam.objects.get(slug=beam_slug, machine=m)

    # Get all data for the selected beam
    data_list = _get_data(b)

    # Get the selected data
    d = Data.objects.get(slug=data_slug, beam=b)

    # Parse the data
    #try:
    table_data = _read_data_file(d)
    #except:
    #    print('Error reading data file')
    if isinstance(table_data, str):
        context = {}
        if beam_list:
            context = {'machine_list' : machine_list,
                       'beam_list' : beam_list,
                       'data_list' : data_list,
                       'selected_machine' : m,
                       'selected_beam' : b,
                       'selected_data' : d,
                       'error_message' : table_data}
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
    # Get all machines
    #machine_list = _get_machines()

    # Get selected machine
    m = Machine.objects.get(slug=machine_slug)

    # Get all beams for the selected machine
    #beam_list = _get_beams(m)

    # Get the selected beam
    b = Beam.objects.get(slug=beam_slug, machine=m)

    # Get all data for the selected beam
    #data_list = _get_data(b)

    # Get the selected data
    d = Data.objects.get(slug=data_slug, beam=b)

    data = _read_data_file(d)

    if 'x_value' in request.POST.keys():
        x = float(request.POST['x_value'])

    if 'y_value' in request.POST.keys():
        y = float(request.POST['y_value'])

    result = _do_interpolate('2D', x, y, data)

    return result

def _get_machines():
    """
    Returns
    -------
    list of FIXME
    """
    return Machine.objects.order_by('-name')[:].reverse

def _get_beams(machine):
    """
    Parameters
    ----------
    machine : django_rt_pdb.models.Machine

    Returns
    -------
    list of FIXME
    """
    return Beam.objects.filter(machine=machine).order_by('modality', '-name')[:].reverse

def _get_data(beam):
    """
    Parameters
    ----------
    beam : django_rt_pdb.models.Beam

    Returns
    -------
    list of FIXME
    """
    return Data.objects.filter(beam=beam).order_by('-name')[:].reverse

def _parse_csv_line(line):
    """
    Parameters
    ----------
    line : str
        A non-empty line from the CSV data file with starting and ending white
        space stripped out.

    Returns
    -------
    str, list of str or None
        The variable name, and list of variable values. If the line contains
        no variable then returns None.
    """
    variables = ['X_TITLE', 'X_HEADERS', 'X_VALUES', 'X_FORMAT',
                 'Y_TITLE', 'Y_HEADERS', 'Y_VALUES', 'Y_FORMAT',
                 'XY_FORMAT', 'XY_TYPE', 'DESCRIPTION', 'SOURCE']

    csv_data = line.split(',')
    
    # Variables
    if '=' in csv_data[0]:
        variable_name = csv_data[0].split('=')[0].strip()
        variable_values = [csv_data[0].split('=')[1].strip()]

        if variable_name not in variables:
            raise ValueError('The CSV data file contains an unknown variable.')

        if csv_data[1:]:
            variable_values.extend(csv_data[1:])

        return variable_name, variable_values

    return None, None

def _read_data_file(data_obj):
    """Parse the uploaded data file for the contents

    Comments
    --------
    The hash character, #, is used to denote comments.

    Data File Variables
    -------------------
    X_TITLE
    ~~~~~~~
    Required if 2D. Character string, may include HTML tags. One value allowed.
    The title of the x variable data for f(x, y). Examples:
        X_TITLE=Equivalent Field Size (cm)
    
    X_LABELS
    ~~~~~~~~
    Optional. Character strings, may include HTML tags. One label for each
    column of data. The column labels in the table header.
        X_LABELS=10X<br />10Y,20X<br />20Y,30X<br />30Y,40X<br />40Y
        X_LABELS=Field Size (cm),Scatter Factor
        X_LABELS=
    
    X_VALUES
    ~~~~~~~~
    Required if 2D. Numeric strings, may not include HTML tags. One value for each column of
    data. The x variable data for f(x, y). Will be converted to floats.
        X_VALUES=10.0,20.0,30.0,40.0
    
    X_FORMAT
    ~~~~~~~~
    If X_LABELS is blank then the X_VALUES will be converted to a string using
    new style python string formatting. If a single format is supplied then
    that format will apply to all the X_VALUES:
        X_FORMATS={:.2f} # Display float values numeric strings with 2 decimal places
    If multiple values are supplied then the format will be applied to the
    corresponding X_VALUES value:
        X_FORMATS={:.2f},{:.3f},{:.1f} (cm),{:.2f} # 10.00, 20.000, 30.0 (cm), 40.00

    Y_TITLE
    ~~~~~~~
    Required. Character string, may include HTML tags. One value allowed.
    The title of the y variable data for f(x, y) and f(y). Examples:
        Y_TITLE=Depth (cm)
        
    Y_LABELS
    ~~~~~~~~~
    Optional. Character strings, may include HTML tags. One label for each
    row of data. The row labels in the table header.
        Y_LABELS=10X<br />10Y,20X<br />20Y,30X<br />30Y,40X<br />40Y
        Y_LABELS=Field Size (cm),Scatter Factor
        Y_LABELS=
    
    Y_VALUES
    ~~~~~~~~
    Required. Numeric strings, may not include HTML tags. One value for each row of
    data. The y variable data for f(x, y) and f(y). Will be converted to floats.
        Y_VALUES=1.0,2.0,5.0
    
    Y_FORMAT
    ~~~~~~~~
    If Y_LABELS is blank then the Y_VALUES will be converted to a string using
    new style python string formatting. If a single format is supplied then
    that format will apply to all the Y_VALUES:
        Y_FORMAT={:.2f} # Display float values numeric strings with 2 decimal places

    If multiple values are supplied then the format will be applied to the
    corresponding Y_VALUES value:
        Y_FORMAT={:.2f},{:.1f},{:.3f} (cm) # 1.00, 5.0 (cm), 2.000, 2.101, ...
    
    XY_FORMAT
    ~~~~~~~~~
    The values of the 1D/2D data will be converted to a string using
    new style python string formatting. If a single format is supplied then
    that format will apply to all the f(x, y) and f(y) values:
        XY_FORMAT={:.3f} # Display float values numeric strings with 3 decimal places

    If multiple values are supplied then the format will be applied to the
    corresponding column of the table data:
        XY_FORMAT={:.1f},{:.3f} # 1.0, 2.002, 2.004, 2.008, ...
                                # 1.5, 2.123, 2.140, 2.180, ...

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

    with open(data_obj.data.path, 'r') as f:
        contents = f.readlines()
        for line in contents:
            # Strip out any comments
            if '#' in line:
                line = line[:line.index('#')]
            # Remove white space
            line = line.strip()
            if line != '':
                line_list = line.split(',')

                try:
                    var_name, var_values = _parse_csv_line(line)
                except ValueError:
                    msg = 'Unable to parse the file'
                    return msg

                if (var_name, var_values) == (None, None):
                    if data['XY_TYPE'][0].upper() == 'NUMERIC':
                        line_list[:] = [float(val) for val in line_list]
                    data['XY_VALUES'].append(line_list)
                else:
                    data[var_name] = var_values

    if data['X_TITLE']:
        x_title = data['X_TITLE'][0]
    else:
        x_title = ''

    if data['Y_TITLE']:
        y_title = data['Y_TITLE'][0]
    else:
        y_title = ''

    # Get the column labels, formatting if necessary
    if data['X_HEADERS'] != ['']:
        column_labels = data['X_HEADERS']
    elif data['X_VALUES'] != ['']:
        column_labels = [data['X_FORMAT'][0].format(float(val)) for val in data['X_VALUES']]
    else:
        msg = 'The file must have either non-blank X_HEADERS or X_VALUES values'
        return msg

    # Get the row labels, formatting if necessary
    if data['Y_HEADERS'] != ['']:
        row_labels = data['Y_HEADERS']
    elif data['Y_VALUES'] != ['']:
        row_labels = [data['Y_FORMAT'][0].format(float(val)) for val in data['Y_VALUES']]
    else:
        msg = 'The file must have either non-blank Y_HEADERS or Y_VALUES values'
        return msg

    #print(data['XY_VALUES'])
    if data['XY_VALUES'] != [] and data['XY_TYPE'][0].upper() == 'NUMERIC':
        # Apply the XY format to the table data
        values_out = []
        for xy_row, y_val in zip(data['XY_VALUES'], row_labels):
            new_row = [data['XY_FORMAT'][0].format(xy) for xy in xy_row]
            new_row.insert(0, y_val)
            values_out.append(new_row)
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
             'y_values' : data['Y_VALUES']}

def _do_interpolate(interpolation_type, x, y, data):
    x_value_ok = True
    y_value_ok = True

    if not min(data['x_values']) <= x <= max(data['x_values']):
        x_value_ok = False

    if not min(data['y_values']) <= y <= max(data['y_values']):
        y_value_ok = False

    result_table = [['1.000', '1.001', '1.002'],
                    ['1.003', '1.004', '1.005'],
                    ['1.006', '1.007', '1.008']]

    result = {'y_value_ok' : y_value_ok,
              'x_value_ok' : x_value_ok,
              'table_type' : '2D',
              'table_data' : result_table,
              'x_title' : 'X Title',
              'y_title' : 'Y Title'}

    return HttpResponse(json.dumps(result), content_type="application/json")
