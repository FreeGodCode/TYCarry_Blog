from django.shortcuts import render, get_object_or_404, redirect


# Create your views here.
from django.urls import reverse


def my_notifications(request):
    """消息通知页面"""
    context = {}
    return render(request, 'notice/my_notifications.html', context)


def my_notification(request, my_notifications_pk):
    """未读变已读,跳转至消息添加页面"""
    my_notification = get_object_or_404(Notification, pk=my_notifications_pk)
    my_notification.unread = False
    my_notification.save()
    return redirect(my_notification.data['url'])


def delete_my_read_notifications(request):
    notifications = request.user.notifications.read()
    notifications.delete()
    return redirect(reverse('notice: my_notifications'))