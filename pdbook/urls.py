from django.conf.urls import url

from . import views

urlpatterns = [
    # ex: /pdb/
    url(r'^$', views.index, name='index'),
    # ex: /pdb/TestMachine/
    url(r'^(?P<machine_name>\w+)/$', views.get_machine, name='machine'),
    # ex: /pdb/TestMachine/6MVPhotons/
    url(r'^(?P<machine_name>\w+)/(?P<beam_name>\w+)$', views.get_beam, name='beam'),
    # ex: /pdb/TestMachine/6MVPhotons/PDD
    url(r'^(?P<machine_name>\w+)/(?P<beam_name>\w+)/(?P<data_name>\w+)$', views.get_data, name='data'),
    # interpolation function
    url(r'^(?P<machine_name>\w+)/(?P<beam_name>\w+)/(?P<data_name>\w+)/interpolate$', views.interpolate, name='interpolate'),
]
