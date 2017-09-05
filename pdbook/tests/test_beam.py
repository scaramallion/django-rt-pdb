import unittest

from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from django.test import TestCase, Client

from pdbook.models import Machine, Beam

class TestBeamModel(TestCase):
    """Test the Beam model"""
    def setUp(self):
        Machine.objects.create(description="Linac Description 01",
                               machine_type="LINAC",
                               manufacturer="Linac Manufacturer 01",
                               model="Linac Model 01",
                               name="Linac Name 01",
                               serial_number="Linac 0001",
                               visible_name="Linac 01")
        self.m1 = Machine.objects.get(id=1)
        Machine.objects.create(description="Linac Description 02",
                               machine_type="LINAC",
                               manufacturer="Linac Manufacturer 02",
                               model="Linac Model 02",
                               name="Linac Name 02",
                               serial_number="Linac 0002",
                               visible_name="Linac 02")
        self.m2 = Machine.objects.get(id=2)

        Beam.objects.create(description="Beam Description 01",
                            energy='6',
                            machine=self.m1,
                            modality='MVP',
                            name="Beam Name 01",
                            visible_name="Beam 01")
        Beam.objects.create(description="Beam Description 01",
                            energy='6',
                            machine=self.m2,
                            modality='ISO',
                            name="Beam Name 02",
                            visible_name="Beam 02")

    def test_str(self):
        """Test the beam __str__ output"""
        b = Beam.objects.get(id=1)
        ref = "{1} - {0}".format(b.visible_name, b.machine.visible_name)
        self.assertEqual(str(b), ref)

    def test_get_absolute_url(self):
        """Test the absolute urls"""
        b = Beam.objects.get(id=1)
        self.assertEqual(b.get_absolute_url(), '/pdb/linac-name-01/beam-name-01')
        b = Beam.objects.get(id=2)
        self.assertEqual(b.get_absolute_url(), '/pdb/linac-name-02/beam-name-02')

    def test_slug(self):
        """Test the slug value is correct"""
        b = Beam.objects.get(id=1)
        self.assertEqual(b.slug, "beam-name-01")

    def test_save_changes_slug(self):
        """Test changing the machine name updates the slug"""
        b = Beam.objects.get(id=1)
        b.name = "Beam Name 01a"
        self.assertEqual(b.slug, "beam-name-01")
        b.save()
        self.assertEqual(b.slug, "beam-name-01a")

    def test_beam_name_must_be_unique_for_machine_a(self):
        """Test exception raised if beam name value is not unique for machine"""
        with self.assertRaises(IntegrityError):
            Beam.objects.create(description="Beam Description 03",
                                energy='6',
                                machine=self.m1,
                                modality='MVP',
                                name="Beam Name 01",
                                visible_name="Beam 03")

    def test_beam_name_must_be_unique_for_machine_b(self):
        """Test same beam name value OK for different machine"""
        Beam.objects.create(description="Beam Description 03",
                                energy='6',
                                machine=self.m2,
                                modality='MVP',
                                name="Beam Name 01",
                                visible_name="Beam 03")

    @unittest.skip("Can't test")
    def test_beam_name_required(self):
        """Test exception raised if no beam name value"""
        with self.assertRaises(IntegrityError):
            Beam.objects.create(description="Beam Description 03",
                                energy='6',
                                machine=self.m1,
                                modality='MVP',
                                visible_name="Beam 03")

    @unittest.skip("Can't test")
    def test_beam_visible_name_required(self):
        """Test exception raised if no beam visible name value"""
        with self.assertRaises(IntegrityError):
            Beam.objects.create(description="Beam Description 03",
                                energy='6',
                                machine=self.m1,
                                modality='MVP',
                                name="Beam Name 03")

    def test_minimal_beam(self):
        """Test creating a beam using the minimum required fields"""
        Beam.objects.create(machine=self.m1,
                            name="Beam Name 03",
                            visible_name="Beam 03")

