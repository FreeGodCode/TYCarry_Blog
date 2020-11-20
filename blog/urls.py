from django.conf.urls import url

from blog import views

urlpatterns = [
    url(r'', views.index_unlogin, name='index_unlogin'),
    url(r'^login/$', views.login, name='login'),
    url(r'^log/$', views.login_success, name='login_success'),
    url(r'^register/$', views.register, name='register'),
    url(r'^forget/$', views.forget_password, name='forget_password'),
    url(r'^reset/$', views.reset_possword, name='reset_possword')
]