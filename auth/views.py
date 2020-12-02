import datetime
import logging
from urllib.parse import urlparse

from django.conf import settings
from django.contrib.auth import get_user_model, login
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.views.generic import FormView

from Blog.utils import get_current_site, get_md5
from auth.authmanager import get_manager_by_type, AuthAccessTokenException
from auth.forms import RequireEmailForm
from auth.models import AuthUser

logger = logging.getLogger(__name__)

# Create your views here.
def get_redirecturl(request):
    """
    :param request:
    :return:
    """
    nexturl = request.GET.get('next_url', None)
    if not nexturl or nexturl == '/login/' or nexturl == '/login':
        nexturl = '/'
        return nexturl
    p = urlparse(nexturl)
    if p.netloc:
        site = get_current_site().domain
        if not p.netloc.replace('www.', '') == site.replace('www.', ''):
            logger.info('非法的url:' + nexturl)
            return '/'
    return nexturl


def authlogin(request):
    """
    :param request:
    :return:
    """
    type = request.GET.get('type', None)
    if not type:
        return HttpResponseRedirect('/')
    manager = get_manager_by_type(type)
    if not manager:
        return HttpResponseRedirect('/')
    nexturl = get_redirecturl(request)
    authorizeurl = manager.get_authorization_url(nexturl)
    return HttpResponseRedirect(authorizeurl)


def authorize(request):
    """
    :param request:
    :return:
    """
    type = request.GET.get('type', None)
    if not type:
        return HttpResponseRedirect('/')
    manager = get_manager_by_type(type)
    if not manager:
        return HttpResponseRedirect('/')
    code = request.GET.get('code', None)
    try:
        resp = manager.get_access_token_by_code(code)
    except AuthAccessTokenException as e:
        logger.warning('AuthAccessTokenException:' + str(e))
        return HttpResponseRedirect('/')
    except Exception as e:
        logger.error(e)
        resp = None
    nexturl = get_redirecturl(request)
    if not resp:
        return HttpResponseRedirect(manager.get_authorization_url(nexturl))
    user = manager.get_auth_userinfo()
    if user:
        if not user.nickname or not user.nickname.strip():
            user.nickname = 'blog' + datetime.datetime.now().strftime('%y%m%d%H%M%S')
        try:
            temp = AuthUser.objects.get(type=type, openid=user.openid)
            temp.picture = user.picture
            temp.matedata = user.matedata
            temp.nickname = user.nickname
            user = temp
        except ObjectDoesNotExist:
            pass

        if type == 'facebook':
            user.token = ''
        if user.email:
            with transaction.atomic():
                author = None
                try:
                    author = get_user_model().objects.get(id=user.author_id)
                except ObjectDoesNotExist:
                    pass

                if not author:
                    result = get_user_model().objects.get_or_create(email=user.email)
                    author = result[0]
                    if result[1]:
                        try:
                            get_user_model().objects.get(username=user.nickname)
                        except ObjectDoesNotExist:
                            author.username = user.nickname
                        else:
                            author.username = 'blog' + datetime.datetime.now().strftime('%y%m%d%H%M%S')
                        author.source = 'authorize'
                        author.save()
                user.author = author
                user.save()

                auth_user_login_signal.send(sender=authorize.__class__, id=user.id)
                login(request, author)
                return HttpResponseRedirect(nexturl)
        else:
            user.save()
            url = reverse('auth:require_email', kwargs={'authid': user.id})
            return HttpResponseRedirect(url)
    else:
        return HttpResponseRedirect(nexturl)


def emailconfirm(request, id, sign):
    """
    :param request:
    :param id:
    :param sign:
    :return:
    """
    if not sign:
        return HttpResponseForbidden()
    if not get_md5(settings.SECRET_KEY + str(id) + settings.SECRET_KEY).upper() == sign.upper():
        return HttpResponseForbidden()
    authuser = get_object_or_404(AuthUser, pk=id)
    with transaction.atomic():
        if authuser.author:
            author = get_user_model().objects.get(pk=authuser.author_id)
        else:
            result = get_user_model().objects.get_or_create(email=authuser.email)
            author = result[0]
            if result[1]:
                author.source = 'emailconfirm'
                author.username = authuser.nickname.strip() if authuser.nickname.strip() else 'bolg' + datetime.datetime.now().strftime('%y%m%d%H%M%S')
                author.save()
        authuser.author = author
        author.save()
    auth_user_login_signal.send(sender=emailconfirm.__class__, id=authuser.id)
    login(request, author)
    site = get_current_site().domain
    content = f'''
    <p>恭喜您, 您已经成功绑定您的邮箱,您可以使用{type}来直接免密码登录
    '''
    send_email(emailto=[authuser.email, ], title='恭喜您绑定成功!', content=content)
    url = reverse('auth:bindsuccess', kwargs={'authid': id})
    url = url + '?type=success'
    return HttpResponseRedirect(url)


class RequireEmailView(FormView):
    """docstring"""
    form_class = RequireEmailForm
    template_name = 'auth/require_email.html'

    def get(self, request, *args, **kwargs):
        authid = self.kwargs['authid']
        authuser = get_object_or_404(AuthUser, pk=authid)
        if authuser.email:
            return HttpResponseRedirect('/')
        return super(RequireEmailView, self).get(request, *args, **kwargs)

    def get_initial(self):
        authid = self.kwargs['authid']
        return {
            'email': '',
            'authid': authid,
        }

    def get_context_data(self, **kwargs):
        authid = self.kwargs['authid']
        authuser = get_object_or_404(AuthUser, pk=authid)
        if authuser.picture:
            kwargs['picture'] = authuser.picture
        return super(RequireEmailView, self).get_context_data(**kwargs)

    def form_valid(self, form):
        email = form.cleaned_data['email']
        authid = form.cleaned_data['authid']
        authuser = get_object_or_404(AuthUser, pk=authid)
        authuser.email = email
        authuser.save()
        sign = get_md5(settings.SECRET_KEY + str(authuser.id) + settings.SECRET_KEY)
        site = get_current_site().domain

        if settings.DEBUG:
            site = '127.0.0.1:8000'
        path = reverse('auth: email_confirm', kwargs={'id': authid, 'sign': sign})
        url = 'http://{site}{path}'.format(site=site, path=path)

        content = """
        <a href="{url}" rel="bookmark">{url}</a>
        """.format(url=url)
        senf_email(emailto=[email, ], title='绑定您的电子邮箱', content=content)
        url = reverse('auth: bindsuccess', kwargs={'authid': authid})
        url = url + "?type=email"
        return HttpResponseRedirect(url)


def bindsuccess(request, authid):
    """
    :param request:
    :param authid:
    :return:
    """
    type = request.GET.get('type', None)
    authuser = get_object_or_404(AuthUser, pk=authid)
    if type == 'email':
        title = 'bind success'
        content = ''
    else:
        title = 'bind success'
        content = '{type}'.format(type=authuser.type)
    return render(request, 'auth/bindsuccess.html', {'title': title, 'content': content})