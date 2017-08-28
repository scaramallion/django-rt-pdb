import os

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.files.storage import DefaultStorage, FileSystemStorage
from django.db import models
from django.template.defaultfilters import slugify
from django.urls import reverse
from django.utils import timezone
from django.utils.html import format_html, mark_safe


class Machine(models.Model):
    """Define the model for a device that produces radiation.

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
        The machine's serial number.
    visible_name : str
        The text used in the machine selection link. May include HTML text
        formatting tags.
    """
    description = models.CharField(max_length=100, blank=True,
                                   help_text="A description of the machine.")
    machine_type = models.CharField(max_length=10, 
                                    choices=(('LINAC', 'Linear Accelerator'),
                                             ('ORTHO', 'Orthovoltage Unit'),
                                             ('SOURCE', 'Radiation Source'),
                                            ),
                                    default='LINAC',
                                    help_text="The type of machine.")
    manufacturer = models.CharField(max_length=100, blank=True,
                                    help_text="The machine's manufacturer.")
    model = models.CharField(max_length=100, blank=True,
                             help_text="The machine's model name/number.")
    name = models.CharField(max_length=100, unique=True,
                            help_text="The name to use for this machine, "
                                      "must be unique (case independant).")
    slug = models.SlugField(max_length=200,
                            help_text="The text that will be used for "
                                      "the machine's part of the url (derived "
                                      "from the Name value).")
    serial_number = models.CharField(max_length=100, blank=True,
                             help_text="The machine's serial number.")
    visible_name = models.CharField(max_length=100,
                                    help_text="The (short) text that will be "
                                              "displayed as a name for this "
                                              "machine. HTML tags are supported.")
    

    def __str__(self):
        """Return a str representation of the Machine."""
        return self.visible_name

    def get_absolute_url(self):
        """Return the absolute url for the Machine"""
        return reverse('machine', kwargs={'machine_slug' : self.slug})

    def save(self, *args, **kwargs):
        """Regenerate the slug every time the object gets saved"""
        # Otherwise changes to self.name may not get reflected in slug
        self.slug = slugify(self.name)
        super(Machine, self).save(*args, **kwargs)


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
    description = models.CharField(max_length=100, blank=True,
                                   help_text="A description of the beam.")
    energy = models.FloatField(help_text="The nominal energy of the beam.")
    name = models.CharField(max_length=100,
                            help_text="The name to use for this beam, "
                                      "must be unique (case independant).")
    machine = models.ForeignKey(Machine, related_name="machine",
                             help_text="The machine object this beam belongs to.")
    modality = models.CharField(max_length=3, 
                                choices=(('MVP', 'MV Photons'), 
                                         ('MVE', 'MeV Electrons'), 
                                         ('KVP', 'kV Photons'),
                                         ('ISO', 'Radioisotope'),
                                        ),
                                default='MVP',
                                help_text="The modality of the beam.")
    slug = models.SlugField(max_length=200,
                            help_text="The text that will be used for "
                                      "the beam's part of the url (derived "
                                      "from the Name value).")
    visible_name = models.CharField(max_length=100,
                                    help_text="The (short) text that will be "
                                              "displayed as a name for this "
                                              "beam. HTML tags are supported.")

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
        s = "{1} - {0}".format(self.visible_name, self.machine.visible_name)
        return s

    def validate_unique(self, exclude=None):
        """All Beam objects for a given Machine must have a unique `name`."""
        # Get a list of all the Beam objects for the current Machine
        beams = Beam.objects.filter(machine=self.machine)
        beam_names = [b.name for b in beams]

        if self.name in beam_names and self not in beams:
            raise ValidationError("A Beam entry with the name '{}' already "
                                  "exists for the current Machine."
                                  .format(self.name))
        
        return super(Beam, self).validate_unique(exclude)

    def get_absolute_url(self):
        """Return the absolute url for the Beam"""
        return reverse('beam',
                       kwargs={'machine_slug' : self.machine.slug,
                               'beam_slug' : self.slug})

    def save(self, *args, **kwargs):
        """Regenerate the slug every time the object gets saved"""
        self.slug = slugify(self.name)
        super(Beam, self).save(*args, **kwargs)


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
            uploaded to <MEDIA_ROOT>/<MACHINE SLUG>/<BEAM SLUG>/<FILE NAME>
            where <MEDIA_ROOT> is the Django MEDIA_ROOT location.
        """
        m_slug = instance.beam.machine.slug
        b_slug = instance.beam.slug
        return '{0}/{1}/{2}'.format(m_slug, b_slug, filename) 


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
    
    beam = models.ForeignKey(Beam, related_name="beam_name", default=0,
                             help_text="The beam object this data belongs to.")
    data = models.FileField(upload_to=objects._upload_directory_path,
                            storage=OverwriteStorage(),
                            help_text="The CSV file containing the table data.")
    data_source = models.CharField(max_length=100, blank=True,
                                   help_text="The source of the table data. Will "
                                   "overwrite the SOURCE= value in the CSV data file.")
    description = models.CharField(max_length=200, blank=True,
                                   help_text="A description of the table data. Will "
                                   "overwrite the DESCRIPTION= value in the CSV file.")
    interpolation_type = models.CharField(default='NA',
                                          max_length=3,
                                          choices=(('NA', 'No interpolation'),
                                                   ('1D', '1D interpolation'),
                                                   ('2D', '2D interpolation')),
                                          help_text="If 1D/2D interpolation is "
                                                    "chosen then the interpolation "
                                                    "widget will be available.")
    show_y_values = models.BooleanField(default=False,
                                        help_text="Show the Y parameter values "
                                        "in addition to the Y row labels.")
    name = models.CharField(max_length=100, unique=True,
                            help_text="The name to use for the table data, "
                                      "must be unique (case independant).")
    slug = models.SlugField(max_length=200,
                            help_text="The text that will be used for "
                                      "the data's part of the url (derived "
                                      "from the Name value).")
    visible_name = models.CharField(max_length=100,
                                    help_text="The (short) text that will be "
                                              "displayed as a name for this "
                                              "data. HTML tags are supported.")

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

    def get_absolute_url(self):
        """Return the absolute url for the Data"""
        return reverse('data',
                       kwargs={'machine_slug' : self.beam.machine.slug,
                               'beam_slug' : self.beam.slug,
                               'data_slug' : self.slug})

    def save(self, *args, **kwargs):
        """Regenerate the slug every time the object gets saved"""
        self.slug = slugify(self.name)
        super(Data, self).save(*args, **kwargs)
        
