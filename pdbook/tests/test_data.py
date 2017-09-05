from django.db.utils import IntegrityError
from django.test import TestCase, Client

from pdbook.models import Machine, Beam, Data

class TestDataModel(TestCase):
    """Test the Data model"""
    def setUp(self):
        self.m1 = Machine.objects.create(description="Linac Description 01",
                                         machine_type="LINAC",
                                         manufacturer="Linac Manufacturer 01",
                                         model="Linac Model 01",
                                         name="Linac Name 01",
                                         serial_number="Linac 0001",
                                         visible_name="Linac 01")
        self.m2 = Machine.objects.create(description="Linac Description 02",
                                         machine_type="LINAC",
                                         manufacturer="Linac Manufacturer 02",
                                         model="Linac Model 02",
                                         name="Linac Name 02",
                                         serial_number="Linac 0002",
                                         visible_name="Linac 02")
        self.m1_b1 = Beam.objects.create(name="Beam Name M01B01",
                                         visible_name="Beam M01B01",
                                         machine=self.m1)
        self.m1_b2 = Beam.objects.create(name="Beam Name M01B02",
                                         visible_name="Beam M01B02",
                                         machine=self.m1)
        self.m1_b3 = Beam.objects.create(name="Beam Name M01B03",
                                         visible_name="Beam M01B03",
                                         machine=self.m1)
        self.m2_b1 = Beam.objects.create(name="Beam Name M02B01",
                                         visible_name="Beam M02B01",
                                         machine=self.m1)
        self.m1_b1_d1 = Data.objects.create(beam=self.m1_b1,
                                            name='Data Name M01B01D01',
                                            visible_name='Data M01B01D01')
        self.m1_b2_d1 = Data.objects.create(beam=self.m1_b2,
                                            name='Data Name M01B02D01',
                                            visible_name='Data M01B02D01')

    def test_str(self):
        """Test the data __str__ output"""
        d = Data.objects.get(id=1)
        self.assertEqual(str(d), d.visible_name)

    def test_get_absolute_url(self):
        """Test the absolute urls"""
        d = Data.objects.get(id=1)
        self.assertEqual(d.get_absolute_url(), '/pdb/linac-name-01/beam-name-m01b01/data-name-m01b01d01')
        d = Data.objects.get(id=2)
        self.assertEqual(d.get_absolute_url(), '/pdb/linac-name-01/beam-name-m01b02/data-name-m01b02d01')

    def test_slug(self):
        """Test the slug value is correct"""
        d = Data.objects.get(id=1)
        self.assertEqual(d.slug, "data-name-m01b01d01")

    def test_save_changes_slug(self):
        """Test changing the data name updates the slug"""
        d = Data.objects.get(id=1)
        d.name = "Data Name M01B01D01a"
        self.assertEqual(d.slug, "data-name-m01b01d01")
        d.save()
        self.assertEqual(d.slug, "data-name-m01b01d01a")

    def test_data_name_must_be_unique_for_beam_a(self):
        """Test exception raised if data name value is not unique for beam"""
        with self.assertRaises(IntegrityError):
            Data.objects.create(beam=self.m1_b1,
                                name="Data Name M01B01D01",
                                visible_name="Data M01B01D01")

    def test_data_name_must_be_unique_for_beam_b(self):
        """Test same data name OK for different beam"""
        Data.objects.create(beam=self.m1_b2,
                                name="Data Name M01B01D01",
                                visible_name="Data M01B01D01")
