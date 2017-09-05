from django.core.urlresolvers import reverse
from django.test import TestCase, Client

from pdbook.models import Machine


class TestIndexView(TestCase):
    """Test the index view"""
    def test_machine_selector_none(self):
        """Test the machine selector shows no machine message if none"""
        c = Client()
        rsp = c.get(reverse('index'))
        self.assertEqual(rsp.status_code, 200)
        with self.assertRaises(KeyError):
            rsp.context['machine_list']
        self.assertTrue(b"No machines have been added" in rsp.content)

        Machine.objects.create(name="Linac Name 03",
                               visible_name="Linac 03")

        rsp = c.get(reverse('index'))
        self.assertEqual(rsp.status_code, 200)
        self.assertEqual(len(rsp.context['machine_list']), 1)
        self.assertFalse(b"No machines have been added" in rsp.content)

    def test_machine_selector_some(self):
        """Test the machine selector shows the available machines"""
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
        c = Client()
        rsp = c.get(reverse('index'))
        self.assertEqual(rsp.status_code, 200)
        self.assertEqual(len(rsp.context['machine_list']), 2)

