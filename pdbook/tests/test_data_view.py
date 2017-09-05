import json
import os

from django.core.urlresolvers import reverse
from django.test import TestCase, Client

from pdbook.models import Machine, Beam, Data


SAMPLE_DIR = os.path.join(os.path.dirname(__file__), 'sample_data')
SAMPLE_1D = os.path.join(SAMPLE_DIR, 'iso_ci.csv')
SAMPLE_2D = os.path.join(SAMPLE_DIR, 'ssd_pdd.csv')


class TestDataView(TestCase):
    """Test the data view"""
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

    def test_data_selector_no_csv(self):
        """Test the data selector shows no csv message if none"""
        c = Client()
        rsp = c.get(reverse('data', args=[self.m1.slug, self.m1_b2.slug, self.m1_b2_d1.slug]))
        self.assertEqual(rsp.status_code, 200)
        self.assertFalse(b"No machines have been added" in rsp.content)
        self.assertFalse(b"No beams have been added" in rsp.content)
        self.assertFalse(b"No data has been added" in rsp.content)
        self.assertTrue(b'There was an error reading the data file' in rsp.content)
        self.assertTrue('error_message' in rsp.context)

    def test_data_selector_some_csvs(self):
        """Test the data selector shows the table data"""
        d = Data.objects.get(id=1)
        d.data.save(os.path.basename(SAMPLE_2D), open(SAMPLE_2D, 'r'), False)
        d.save()
        
        c = Client()
        rsp = c.get(reverse('data', args=[self.m1.slug, self.m1_b1.slug, self.m1_b1_d1.slug]))
        self.assertEqual(rsp.status_code, 200)
        self.assertFalse(b"No machines have been added" in rsp.content)
        self.assertFalse(b"No beams have been added" in rsp.content)
        self.assertFalse(b"No data has been added" in rsp.content)
        self.assertFalse('error_message' in rsp.context)


class Test1DInterpolation(TestCase):
    """Test 1D interpolation works correctly"""
    def setUp(self):
        self.m = Machine.objects.create(description="Linac Description 01",
                                        machine_type="LINAC",
                                        manufacturer="Linac Manufacturer 01",
                                        model="Linac Model 01",
                                        name="Linac Name 01",
                                        serial_number="Linac 0001",
                                        visible_name="Linac 01")
        self.b = Beam.objects.create(name="Beam Name 01",
                                     visible_name="Beam 01",
                                     machine=self.m)
        self.d = Data.objects.create(beam=self.b,
                                     name='Data Name 01',
                                     visible_name='Data 01')
        self.d.data.save(os.path.basename(SAMPLE_1D), open(SAMPLE_1D, 'r'), False)

    def test_no_interpolation(self):
        """Test results when no interpolation"""
        c = Client()
        rsp = c.get(reverse('data',
                            args=[self.m.slug, self.b.slug, self.d.slug]))
        self.assertEqual(rsp.status_code, 200)
        self.assertFalse(b'<a rel="leanModal" href=\'#modal-interpolate-1D\'>Interpolate</a>' in rsp.content)
        self.assertFalse(b'<a rel="leanModal" href=\'#modal-interpolate-2D\'>Interpolate</a>' in rsp.content)

    def test_1d_interpolation(self):
        """Test results from 1D interpolation"""
        self.d.interpolation_type = '1D'
        self.d.save()

        c = Client()
        rsp = c.get(reverse('data',
                            args=[self.m.slug, self.b.slug, self.d.slug]))
        self.assertEqual(rsp.status_code, 200)
        self.assertTrue(b'<a rel="leanModal" href=\'#modal-interpolate-1D\'>Interpolate</a>' in rsp.content)
        self.assertFalse(b'<a rel="leanModal" href=\'#modal-interpolate-2D\'>Interpolate</a>' in rsp.content)

        data = {'y_value' : '2.5', 'interp_type' : '1D'}
        rsp = c.post(reverse('interpolate',
                             args=[self.m.slug, self.b.slug, self.d.slug]),
                     data)
        out = json.loads(rsp.content.decode('utf-8'))
        self.assertEqual(out['y_values'], ["2.0", "2.5", "3.0"])
        self.assertEqual(out['table_data'], ["0.653", "0.670", "0.688"])


class Test2DInterpolation(TestCase):
    """Test 2D interpolation works correctly"""
    def setUp(self):
        self.m = Machine.objects.create(description="Linac Description 01",
                                        machine_type="LINAC",
                                        manufacturer="Linac Manufacturer 01",
                                        model="Linac Model 01",
                                        name="Linac Name 01",
                                        serial_number="Linac 0001",
                                        visible_name="Linac 01")
        self.b = Beam.objects.create(name="Beam Name 01",
                                     visible_name="Beam 01",
                                     machine=self.m)
        self.d = Data.objects.create(beam=self.b,
                                     name='Data Name 01',
                                     visible_name='Data 01')
        self.d.data.save(os.path.basename(SAMPLE_1D), open(SAMPLE_2D, 'r'), False)

    def test_no_interpolation(self):
        """Test results when no interpolation"""
        c = Client()
        rsp = c.get(reverse('data',
                            args=[self.m.slug, self.b.slug, self.d.slug]))
        self.assertEqual(rsp.status_code, 200)
        self.assertFalse(b'<a rel="leanModal" href=\'#modal-interpolate-1D\'>Interpolate</a>' in rsp.content)
        self.assertFalse(b'<a rel="leanModal" href=\'#modal-interpolate-2D\'>Interpolate</a>' in rsp.content)

    def test_2d_interpolation(self):
        """Test results from 2D interpolation"""
        self.d.interpolation_type = '2D'
        self.d.save()

        c = Client()
        rsp = c.get(reverse('data',
                            args=[self.m.slug, self.b.slug, self.d.slug]))
        self.assertEqual(rsp.status_code, 200)
        self.assertFalse(b'<a rel="leanModal" href=\'#modal-interpolate-1D\'>Interpolate</a>' in rsp.content)
        self.assertTrue(b'<a rel="leanModal" href=\'#modal-interpolate-2D\'>Interpolate</a>' in rsp.content)

        data = {'y_value' : '2.3', 'x_value' : '5.8', 'interp_type' : '2D'}
        rsp = c.post(reverse('interpolate',
                             args=[self.m.slug, self.b.slug, self.d.slug]),
                     data)
        out = json.loads(rsp.content.decode('utf-8'))
        self.assertEqual(out['y_values'], ["2.2", "2.3", "2.4"])
        self.assertEqual(out['x_values'], ["5.0", "5.8", "6.0"])
        self.assertEqual(out['table_data'], [["98.6", "98.4", "98.4"],
                                             ["98.0", "98.0", "98.0"],
                                             ["97.5", "97.5", "97.5"]])
