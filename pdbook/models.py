from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.files.storage import DefaultStorage, FileSystemStorage
from django.db import models
from django.utils import timezone
from django.utils.html import format_html, mark_safe

import os


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
    description = models.CharField(max_length=100, blank=True)
    machine_type = models.CharField(max_length=10, 
                                    choices=(('LINAC', 'Linear Accelerator'),
                                             ('ORTHO', 'Orthovoltage Unit'),
                                             ('SOURCE', 'Radiation Source'),
                                            ),
                                    default='LINAC')
    manufacturer = models.CharField(max_length=100, blank=True)
    model = models.CharField(max_length=100, blank=True)
    name = models.CharField(max_length=100, unique=True)
    serial_number = models.CharField(max_length=100, blank=True)
    visible_name = models.CharField(max_length=100)

    def __str__(self):
        """Return a str representation of the Machine."""
        return self.visible_name


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
    description = models.CharField(max_length=100, blank=True)
    energy = models.FloatField()
    name = models.CharField(max_length=100)
    machine = models.ForeignKey(Machine, related_name="machine")
    modality = models.CharField(max_length=3, 
                                choices=(('MVP', 'MV Photons'), 
                                         ('MVE', 'MeV Electrons'), 
                                         ('KVP', 'kV Photons'),
                                         ('ISO', 'Radioisotope'),
                                        ),
                                default='MVP')
    visible_name = models.CharField(max_length=100)

    def __str__(self):
        """Return a str representation of the Beam."""
        mode_str = {'MVP' : 'MV Photons',
                    'MVE' : 'MeV Electrons',
                    'KVP' : 'kV Photons',
                    'ISO' : ''}
        energy_mode = ''
        if self.modality != 'ISO':
            energy_mode = '({0} {1})'.format(self.energy, mode_str[self.modality])
        # TODO: Sort by machine name then photons, electrons, then energy
        s = "{2} - {0} - ({1})".format(self.visible_name, self.description, self.machine.visible_name)
        return s

    def validate_unique(self, exclude=None):
        """All Beam objects for a given Machine must have a unique `name`."""
        # Get a list of all the Data objects for the current Beam
        beams = Beam.objects.filter(machine=self.machine)
        beam_names = [b.name for b in beams]

        if self.name in beam_names and self not in beams:
            raise ValidationError("A Beam entry with the name '{}' already "
                                  "exists for the current Machine."
                                  .format(self.name))
        
        return super(Beam, self).validate_unique(exclude)

class OverwriteStorage(FileSystemStorage):
    """Override the FileSystemStorage class to overwrite existing files."""
    def get_available_name(self, name, max_length=None):
        if self.exists(name):
            os.remove(os.path.join(settings.MEDIA_ROOT, name))
        return super(OverwriteStorage, self).get_available_name(name, max_length)


class DataManager(models.Manager):
    """Provide management for the Data model."""
    def _upload_directory_path(self, instance, filename):
        """Return the path the data file was uploaded to.

        Parameters
        ----------
        instance : Data
            The Data instance uploading the file.
        filename : str
            The filename of the uploaded file.

        Returns
        -------
        str
            The upload path, including the filename. The file will then be
            uploaded to <MEDIA_ROOT>/<MACHINE NAME>/<BEAM NAME>/<DATA NAME>
            where <MEDIA_ROOT> is the Django MEDIA_ROOT location.
        """
        m_name = instance.beam.machine.name
        b_name = instance.beam.name
        return '{0}/{1}/{2}'.format(m_name, b_name, filename) 


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
    has_interpolation : str
        The data has an interpolation widget (default False)
    name : str
        The beam name used in URLs, max 25 characters. Must be unique.
    visible_name : str
        The text used in the data selection link. May include HTML text
        formatting tags.
    """
    class Meta:
        verbose_name_plural = "Data"
    
    objects = DataManager()
    
    beam = models.ForeignKey(Beam, related_name="beam_name", default=0)
    data = models.FileField(upload_to=objects._upload_directory_path,
                            storage=OverwriteStorage())
    data_source = models.CharField(max_length=100, blank=True)
    description = models.CharField(max_length=200, blank=True)
    interpolation_type = models.CharField(default='NA',
                                          max_length=3,
                                          choices=(('NA', 'No interpolation'),
                                                   ('1D', '1D interpolation'),
                                                   ('2D', '2D interpolation')))
    interp1D_indexes = models.CharField(max_length=100, blank=True)
    name = models.CharField(max_length=100)
    visible_name = models.CharField(max_length=100)

    def __str__(self):
        """Return a str representation of the Data."""
        return self.html_visible_name()

    def html_visible_name(self):
        """Return a non-escaped `visible_name`."""
        return format_html('{}', mark_safe(self.visible_name))

    def validate_unique(self, exclude=None):
        """All Data objects for a given Beam must have a unique `name`."""
        # Get a list of all the Data objects for the current Beam
        data = Data.objects.filter(beam=self.beam)
        data_names = [d.name for d in data]

        if self.name in data_names and self not in data:
            raise ValidationError("A Data entry with the name '{}' already "
                                  "exists for the current Beam."
                                  .format(self.name))
        
        return super(Data, self).validate_unique(exclude)
        
