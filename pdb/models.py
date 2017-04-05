from django.db import models
from django.utils import timezone

import os
import sys

from picklefield.fields import PickledObjectField


class Machine(models.Model):
    """Define the model for a machine that produces radiation.

    Attributes
    ----------
    description : str
        A short description of the Machine.
    machine_type : str
        The type of radiation producing machine, one of:
            'LINAC' - linear accelerator (default)
            'ORTHO' - Orthovoltage unit
            'SOURCE' - Radiation source
    manufacturer : str
        The manufacturer of the machine.
    model : str
        The model of the machine.
    name : str
        The machine name used in URLs. Must be unique.
    serial_number : str
        The machine's serial number, default 00000000.
    visible_name : str
        The text used in the machine selection link. May include HTML text
        formatting tags.
    """
    description = models.CharField(default='Description')
    machine_type = models.CharField(choices=(('LINAC', 'Linear Accelerator'),
                                             ('ORTHO', 'Orthovoltage Unit'),
                                             ('SOURCE', 'Radiation Source'),
                                            ),
                                    default='LINAC')
    manufacturer = models.CharField(default='Manufacturer')
    model = models.CharField(default='Model')
    name = models.CharField(default='Name')
    serial_number = models.CharField(default='00000000')
    visible_name = models.CharField(default='Machine Name')


class Beam(models.Model):
    """Define the model for a radiation beam.

    Attributes
    ----------
    description : str
        A short description of the Beam.
    energy : float
        The beam's nominal energy.
    machine : Machine
        The Machine used to produce the beam.
    modality : str
        The beam's modality, one of the following:
            'MVP' - MV photons (default)
            'MVE' - MV electrons
            'KVP' - kV photons
            'ISO' - Radioisotope
    name : str
        The beam name used in URLs.
    visible_name : str
        The text used in the beam selection link. May include HTML text
        formatting tags.
    """
    description = models.CharField(default='Description')
    energy = models.FloatField()
    name = models.CharField(default='Name')
    machine = models.ForeignKey(Machine, related_name="machine")
    modality = models.CharField(choices=(('MVP', 'MV Photons'), 
                                         ('MVE', 'MV Electrons'), 
                                         ('KVP', 'kV Photons'),
                                         ('ISO', 'Radioisotope'),
                                        ),
                                default='MVP')
    visible_name = models.CharField(default='Beam Name')


class Data(models.Model):
    """Define the model for beam data.

    Attributes
    ----------
    beam : Beam
        The Beam used to produce the data.
    data : numpy ndarray
        A pickled list of numpy ndarrays that store the header and table data.
        For a 2D table this should be [x array, y array, f(x,y) array]. For a
        1D table this should be [column headers array, table values array].
    data_source : str
        A description of the origin of the data, such as a journal article or
        internal record keeping location.
    description : str
        A short description of the Data.
    formats : str
        The new style python formatting strings to use for the X variables, 
        Y variable and data (as a comma-separated string). If the data is 2D
        then there should be three CSV formats, if 1D then there should be a
        format for the column headers then a format for each column of data.
    has_interpolation : str
        The data has an interpolation widget (default False)
    name : str
        The beam name used in URLs, max 25 characters. Must be unique.
    visible_name : str
        The text used in the data selection link. May include HTML text
        formatting tags.
    """
    beam = models.ForeignKey(Beam, related_name="beam_name", default=0)
    data = PickledObjectField()
    data_source = models.CharField()
    description = models.CharField(default='Description')
    formats = models.CharField()
    has_interppolation = models.BooleanField(default=False)
    interp1D_indexes = models.CharField()
    name = models.CharField(default='Name')
    visible_name = models.CharField(default='Data Name')

