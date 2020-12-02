from django.conf.urls import url

from owntracks import views

urlpatterns = [
    url(r'^owntracks/logtracks', views.manage_owntrack_log, name='logtracks'),
    url(r'^owntracks/show_maps', views.show_maps, name='show_maps'),
    url(r'^owntracks/get_datas', views.get_datas, name='get_datas'),
    url(r'^owntracks/show_datas', views.show_dates, name='show_dates'),
]