import unittest

from django.db.utils import IntegrityError
from django.test import TestCase, Client

from pdbook.models import Machine

class TestMachineModel(TestCase):
    """Test the Machine model"""
    def setUp(self):
        Machine.objects.create(description="Linac Description 01",
                               machine_type="LINAC",
                               manufacturer="Linac Manufacturer 01",
                               model="Linac Model 01",
                               name="Linac Name 01",
                               serial_number="Linac 0001",
                               visible_name="Linac 01")
        Machine.objects.create(description="Linac Description 02",
                               machine_type="LINAC",
                               manufacturer="Linac Manufacturer 02",
                               model="Linac Model 02",
                               name="Linac Name 02",
                               serial_number="Linac 0002",
                               visible_name="Linac 02")

    def test_str(self):
        """Test the machine __str__ output"""
        m = Machine.objects.get(id=1)
        self.assertEqual(str(m), m.visible_name)

    def test_get_absolute_url(self):
        """Test the absolute urls"""
        m = Machine.objects.get(id=1)
        self.assertEqual(m.get_absolute_url(), '/pdb/linac-name-01')
        m = Machine.objects.get(id=2)
        self.assertEqual(m.get_absolute_url(), '/pdb/linac-name-02')

    def test_slug(self):
        """Test the slug value is correct"""
        m = Machine.objects.get(id=1)
        self.assertEqual(m.slug, "linac-name-01")

    def test_save_changes_slug(self):
        """Test changing the machine name updates the slug"""
        m = Machine.objects.get(id=1)
        m.name = "Linac Name 01a"
        self.assertEqual(m.slug, "linac-name-01")
        m.save()
        self.assertEqual(m.slug, "linac-name-01a")

    def test_machine_name_must_be_unique(self):
        """Test exception raised if machine name value is not unique"""
        with self.assertRaises(IntegrityError):
            Machine.objects.create(description="Linac Description 03",
                                   machine_type="LINAC",
                                   manufacturer="Linac Manufacturer 03",
                                   model="Linac Model 03",
                                   name="Linac Name 02",
                                   serial_number="Linac 0003",
                                   visible_name="Linac 03")

    @unittest.skip("Can't test")
    def test_machine_name_required(self):
        """Test exception raised if no machine name value"""
        machines = Machine.objects.filter()
        machine_names = [m.name for m in machines]
        with self.assertRaises(IntegrityError):
            Machine.objects.create(description="Linac Description 03",
                                   machine_type="LINAC",
                                   manufacturer="Linac Manufacturer 03",
                                   model="Linac Model 03",
                                   serial_number="Linac 0003",
                                   visible_name="Linac 03")

    @unittest.skip("Can't test")
    def test_machine_visible_name_required(self):
        """Test exception raised if no machine visible name value"""
        with self.assertRaises(IntegrityError):
            Machine.objects.create(description="Linac Description 03",
                                   machine_type="LINAC",
                                   manufacturer="Linac Manufacturer 03",
                                   model="Linac Model 03",
                                   name="Linac Name 03",
                                   serial_number="Linac 0003")

    def test_minimal_machine(self):
        """Test creating a machine using the minimum required fields"""
        Machine.objects.create(name="Linac Name 03",
                               visible_name="Linac 03")
