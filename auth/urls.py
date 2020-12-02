from django.conf.urls import url

from auth import views

app_name = 'auth'
urlpatterns = [
    url(r'^auth/authorize$', views.authorize, name='authorize'),
    url(r'^auth/requireemail/<int: authid>.html', views.RequireEmailView.as_view(), name='require_email'),
    url(r'^auth/emailconfirm/<int: id>/<sign>.html', views.emailconfirm, name='email_comfirm'),
    url(r'^auth/bindsuccess/<int: authid>.html', views.bindsuccess, name='bindsuccess'),
    url(r'^auth/authlogin', views.authlogin, name='authlogin'),
]