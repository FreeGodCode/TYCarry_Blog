from django.conf.urls import url

from notice import views

app_name = 'notice'

urlpatterns = [
    url(r'^my_notifications/$', views.my_notifications, name='my_notifications'),
    url(r'^my_notification/<int: my_notifications_pk>/', views.my_notification, name='my_notification'),
    url(r'^delete_my_read_notifications/$', views.delete_my_read_notifications, name='delete_my_read_notifications'),

]