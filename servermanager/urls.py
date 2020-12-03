from django.conf.urls import url
from django.urls import path

from servermanager import views

urlpatterns = [
    # path(r'robot', make_view(robot)),
    url(r'^robot', views.robot, name='robot'),
]