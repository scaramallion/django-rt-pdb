from django.core.urlresolvers import reverse
from django.test import TestCase, Client

from pdbook.models import Machine, Beam, Data


class TestBeamView(TestCase):
    """Test the beam view"""
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
        

    def test_beam_selector_no_data(self):
        """Test the beam selector shows no data message if none"""
        c = Client()
        rsp = c.get(reverse('beam', args=[self.m1.slug, self.m1_b2.slug]))
        self.assertEqual(rsp.status_code, 200)
        with self.assertRaises(KeyError):
            rsp.context['data_list']
        self.assertFalse(b"No machines have been added" in rsp.content)
        self.assertFalse(b"No beams have been added" in rsp.content)
        self.assertTrue(b"No data has been added" in rsp.content)

        Data.objects.create(beam=self.m1_b2,
                            name='Data Name M01B02D01',
                            visible_name='Data M01B02D01')

        rsp = c.get(reverse('beam', args=[self.m1.slug, self.m1_b2.slug]))
        self.assertEqual(rsp.status_code, 200)
        self.assertFalse(b"No data has been added" in rsp.content)
        self.assertEqual(len(rsp.context['data_list']), 1)

    def test_machine_selector_some_beams(self):
        """Test the machine selector shows the available machines"""
        Data.objects.create(beam=self.m1_b2,
                            name='Data Name M01B02D01',
                            visible_name='Data M01B02D01')
        Data.objects.create(beam=self.m1_b2,
                            name='Data Name M01B02D02',
                            visible_name='Data M01B02D02')
        return
        c = Client()
        rsp = c.get(reverse('beam', args=[self.m1.slug, self.m1_b2.slug]))
        self.assertEqual(rsp.status_code, 200)
        self.assertEqual(len(rsp.context['data_list']), 2)

