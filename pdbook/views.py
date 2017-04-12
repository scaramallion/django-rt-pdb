import json

from django.http import HttpResponse
from django.shortcuts import render, render_to_response
from django.template import RequestContext
from django.views.decorators.csrf import csrf_protect

from pdbook.models import Machine, Beam, Data


def index(request):
    # Get all machines
    machine_list = _get_machines()

    # Build response
    context = {}
    if machine_list:
        context = {'machine_list' : machine_list}

    return render(request, 'pdbook/index.html', context)

def get_machine(request, machine_name):
    # Get all machines
    machine_list = _get_machines()

    # Get selected machine
    m = Machine.objects.filter(name=machine_name)[0]

    # Get all beams for the selected machine
    beam_list = _get_beams(m)

    # Build response
    context = {}
    if beam_list:
        context = {'machine_list' : machine_list,
                   'beam_list' : beam_list,
                   'selected_machine' : m}

    return render(request, 'pdbook/index.html', context)

def get_beam(request, machine_name, beam_name):
    # Get all machines
    machine_list = _get_machines()

    # Get selected machine
    m = Machine.objects.filter(name=machine_name)[0]

    # Get all beams for the selected machine
    beam_list = _get_beams(m)

    # Get the selected beam
    b = Beam.objects.filter(name=beam_name)[0]

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

@csrf_protect
def get_data(request, machine_name, beam_name, data_name):
    # Get all machines
    machine_list = _get_machines()

    # Get selected machine
    m = Machine.objects.filter(name=machine_name)[0]

    # Get all beams for the selected machine
    beam_list = _get_beams(m)

    # Get the selected beam
    b = Beam.objects.filter(name=beam_name)[0]

    # Get all data for the selected beam
    data_list = _get_data(b)

    # Get the selected data
    d = Data.objects.filter(beam=b).filter(name=data_name)[0]

    # Parse the data
    try:
        table_data = _read_data_file(d)
    except:
        print('Error reading data file')

    # Build response
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

    return render(request, 'pdbook/index.html', context)

def interpolate(request, machine_name, beam_name, data_name):
    # Get all machines
    machine_list = _get_machines()

    # Get selected machine
    m = Machine.objects.filter(name=machine_name)[0]

    # Get all beams for the selected machine
    beam_list = _get_beams(m)

    # Get the selected beam
    b = Beam.objects.filter(name=beam_name)[0]

    # Get all data for the selected beam
    data_list = _get_data(b)

    # Get the selected data
    d = Data.objects.filter(beam=b).filter(name=data_name)[0]

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
    return Beam.objects.filter(machine=machine).order_by('-name')[:].reverse

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

def _read_data_file(data):
    """Parse the uploaded data file for the contents

    Parameters
    ----------
    data : django_rt_pdb.models.Data

    Returns
    -------
    dict
        A dict containing the table data
    """
    header_labels = None
    x_title = ''
    x_values = None
    x_format = '{}'
    y_title = ''
    y_values = None
    y_format = '{}'
    xy_values = []
    xy_format = '{}'

    with open(data.data.path, 'r') as f:
        contents = f.readlines()
        for line in contents:
            # Strip out any comments
            if '#' in line:
                line = line[:line.index('#')]
            # Remove white space
            line = line.strip()
            if line != '':
                line_list = line.split(',')
                if '=' in line_list[0]:
                    line_type = line_list[0].split('=')[0].strip()
                    values = [line_list[0].split('=')[1]]
                    values.extend(line_list[1:])
                    if line_type == 'X_HEADERS':
                        header_labels = values
                    elif line_type == 'X_VALUES':
                        x_values = [float(val) for val in values]
                    elif line_type == 'X_FORMAT':
                        x_format = values[0]
                    elif line_type == 'X_TITLE':
                        x_title = values[0]
                    elif line_type == 'XY_FORMAT':
                        xy_format = values[0]
                    elif line_type == 'Y_VALUES':
                        y_values = [float(val) for val in values]
                    elif line_type == 'Y_FORMAT':
                        y_format = values[0]
                    elif line_type == 'Y_TITLE':
                        y_title = values[0]
                else:
                    xy_values.append([float(val) for val in line_list])

    values_out = []
    for row in xy_values:
        values_out.append([xy_format.format(val) for val in row])

    for data_row, first_row in zip(values_out, y_values):
        data_row.insert(0, y_format.format(first_row))

    return {'header_labels' : header_labels,
             'table_data' : values_out,
             'x_title' : x_title,
             'x_values' : x_values,
             'y_title' : y_title,
             'y_values' : y_values}

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
              'table_data' : result_table}

    return HttpResponse(json.dumps(result), content_type="application/json")
