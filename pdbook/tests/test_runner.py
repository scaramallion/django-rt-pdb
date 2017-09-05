import os
import shutil
import tempfile

from django.apps import apps
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.core.urlresolvers import reverse
from django.db.models import FileField
from django.test.runner import DiscoverRunner


SAMPLE_DIR = os.path.join(os.path.dirname(__file__), 'sample_data')


class LocalStorageDiscoverRunner(DiscoverRunner):
    """Taken from https://gist.github.com/kemar/5f9290cb6843c98d1699"""
    def setup_test_environment(self):
        super().setup_test_environment()

        settings._original_media_root = settings.MEDIA_ROOT
        settings._original_file_storage = settings.DEFAULT_FILE_STORAGE
        settings._original_fields_storages = {}

        settings._temp_media_dir = tempfile.mkdtemp(dir=SAMPLE_DIR)

        settings.MEDIA_ROOT = settings._temp_media_dir
        settings.DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'

        for model in apps.get_models():
            fields = [f for f in model._meta.fields if isinstance(f, FileField)]
            for field in fields:
                model_path = '%s.%s' %(model._meta.app_label, model._meta.model_name)
                original_storage = (field.name, field.storage)
                original_storages = settings._original_fields_storages.setdefault(model_path, [])
                original_storages.append(original_storage)
                field.storage = FileSystemStorage(location=settings.MEDIA_ROOT)

    def teardown_test_environment(self):
        super().teardown_test_environment()

        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)

        settings.MEDIA_ROOT = settings._original_media_root
        settings.DEFAULT_FILE_STORAGE = settings._original_file_storage

        for model_path, original_storages in settings._original_fields_storages.items():
            model = apps.get_model(*model_path.split('.'))
            for field_name, original_storage in original_storages:
                field = model._meta.get_field(field_name)
                field.storage = original_storage

        del settings._original_media_root
        del settings._original_file_storage
        del settings._original_fields_storages
