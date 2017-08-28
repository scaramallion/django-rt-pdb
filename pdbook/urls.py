from django.conf.urls import url

from . import views

urlpatterns = [
    # ex: /pdb
    url(r'^$', views.index, name='index'),
    # ex: /pdb/test-machine
    url(r'^(?P<machine_slug>[-\w]+)$', views.get_machine, name='machine'),
    # ex: /pdb/test-machine/06-mv-photons
    url(r'^(?P<machine_slug>[-\w]+)/(?P<beam_slug>[-\w]+)$', views.get_beam, name='beam'),
    # ex: /pdb/test-machine/06-mv-photons/pdd
    url(r'^(?P<machine_slug>[-\w]+)/(?P<beam_slug>[-\w]+)/(?P<data_slug>[-\w]+)$', views.get_data, name='data'),
    # ex: /pdb/test-machine/06-mv-photons/pdd/interpolate
    url(r'^(?P<machine_slug>[-\w]+)/(?P<beam_slug>[-\w]+)/(?P<data_slug>[-\w]+)/interpolate$', views.interpolate, name='interpolate'),
]
