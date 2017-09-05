from django.core.urlresolvers import reverse
from django.test import TestCase, Client

from pdbook.models import Machine, Beam


class TestMachineView(TestCase):
    """Test the machine view"""
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

    def test_machine_selector_no_beams(self):
        """Test the machine selector shows no beam message if none"""
        c = Client()
        rsp = c.get(reverse('machine', args=[self.m1.slug]))
        self.assertEqual(rsp.status_code, 200)
        with self.assertRaises(KeyError):
            rsp.context['beam_list']
        self.assertFalse(b"No machines have been added" in rsp.content)
        self.assertTrue(b"No beams have been added" in rsp.content)

        Beam.objects.create(name="Beam Name 01",
                            visible_name="Beam 01",
                            machine=self.m1)

        rsp = c.get(reverse('machine', args=[self.m1.slug]))
        self.assertEqual(rsp.status_code, 200)
        self.assertFalse(b"No beams have been added" in rsp.content)
        self.assertEqual(len(rsp.context['beam_list']), 1)

    def test_machine_selector_some_beams(self):
        """Test the machine selector shows the available machines"""
        Beam.objects.create(name="Beam Name 01",
                            visible_name="Beam 01",
                            machine=self.m2)
        Beam.objects.create(name="Beam Name 02",
                            visible_name="Beam 02",
                            machine=self.m2)
        
        c = Client()
        rsp = c.get(reverse('machine', args=[self.m2.slug]))
        self.assertEqual(rsp.status_code, 200)
        self.assertEqual(len(rsp.context['beam_list']), 2)

