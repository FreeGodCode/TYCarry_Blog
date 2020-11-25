from django.conf.urls import url

from myzone import views

urlpatterns = [
    url(r'^talk/$', views.TalkView.as_view(), name='talk'),

]