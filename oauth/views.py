import datetime
import logging
from urllib.parse import urlparse

from django.conf import settings
from django.contrib.auth import login, get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.views.generic import FormView

from Blog.blog_signals import oauth_user_login_signal
from Blog.utils import get_current_site, get_md5, send_email
from auth.forms import RequireEmailForm
from oauth.models import OAuthUser

logger = logging.getLogger(__name__)


def get_redirect_url(request):
    """获取重定向地址"""
    next_url = request.GET.get('next_url', None)
    if not next_url or next_url == '/login/' or next_url == '/login':
        next_url = '/'
        return next_url
    p = urlparse(next_url)
    if p.netloc:
        site = get_current_site().domain
        if not p.netloc.replace('www.', '') == site.replace('www.', ''):
            logger.info('非法的url: ' + next_url)
            return '/'
    return next_url


def oauth_login(request):
    """"""
    type = request.GET.get('type', None)
    if not type:
        return HttpResponseRedirect('/')
    manager = get_manager_by_type(type)
    if not manager:
        return HttpResponseRedirect('/')
    next_url = get_redirect_url(request)
    authorize_url = manager.get_authorization_url(next_url)
    return HttpResponseRedirect(authorize_url)


def authorize(request):
    """"""
    type = request.GET.get('type', None)
    if not type:
        return HttpResponseRedirect('/')
    manager = get_manager_by_type(type)
    if not manager:
        return HttpResponseRedirect('/')
    code = request.GET.get('code', None)
    try:
        resp = manager.get_access_token_by_code(code)
    except OAuthAccessTokenException as e:
        logger.warning('OAuthAccessTokenException:' + str(e))
        return HttpResponseRedirect('/')
    except Exception as e:
        logger.error(e)
        resp = None

    next_url = get_redirect_url(request)
    if not resp:
        return HttpResponseRedirect(manager.get_authorization_url(next_url))
    user = manager.get_oauth_userinfo()
    if user:
        if not user.nickname or not user.nickname.strip():
            user.nickname = 'blog'  + datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        try:
            obj = OAuthUser.objects.get(type=type, openid=user.openid)
            obj.picture = user.picture
            obj.matedata = user.matedata
            obj.nickname = user.nickname
            user = obj
        except ObjectDoesNotExist:
            pass

        if type == 'facebook':
            user.token = ''
        if user.email:
            with transaction.atomic():
                author = None
                try:
                    author = get_user_model().objects.get(id=user.author.id)
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
                            author.username = 'blog' + datetime.datetime.now().strftime('%Y%m%d%H%M%S')
                            author.source = 'authorize'
                            author.save()
                user.author = author
                user.save()

                oauth_user_login_signal.send(sender=authorize.__class__, id=user.id)
                login(request, author)
                return HttpResponseRedirect(next_url)
        else:
            user.save()
            url = reverse('oauth: require_email', kwargs={'oauthid': user.id})
            return HttpResponseRedirect(url)
    else:
        return HttpResponseRedirect(next_url)


def email_confirm(request, id, sign):
    """邮件确认"""
    if not sign:
        return HttpResponseForbidden()
    if not get_md5(settings.SECRET_KEY + str(id) + settings.SECRET_KEY).upper() == sign.upper():
        return HttpResponseForbidden()

    oauthuser = get_object_or_404(OAuthUser, pk=id)
    with transaction.atomic():
        if oauthuser.author:
            author = get_user_model().objects.get(pk=oauthuser.author_id)
        else:
            result = get_user_model().objects.get_or_create(email=oauthuser.email)
            author = result[0]
            if result[1]:
                author.source = 'email_confirm'
                author.username = oauthuser.nickname.strip() if oauthuser.nickname.strip() else 'blog' + datetime.datetime.now().strftime('%Y%m%d%H%M%S')
                author.save()
        oauthuser.author = author
        oauthuser.save()
    oauth_user_login_signal.send(sender=email_confirm.__class__, id=oauthuser.id)
    login(request, author)

    site = get_current_site().domain
    content = '''
    <p>恭喜您，您已经成功绑定邮箱，您可以使用{type}类绵密登录本网站，欢迎您继续关注本站</p>
    <a href='{url}' rel='bookmark'>{url}</a>
    <br />
    如果上面的链接无法打开，请讲次链接复制到浏览器。
    {url}
    '''.format(type=oauthuser.type, url='http://' + site)
    send_email(emailto=[oauthuser.email, ], title='恭喜您绑定成功！', content = content)
    url = reverse('oauth: bind_success', kwargs={'oauthid': id})
    url = url + '?type=success'
    return HttpResponseRedirect(url)


class RequireEmailView(FormView):
    """邮件"""
    form_class = RequireEmailForm
    template_name = 'oauth/require_email.html'

    def get(self, request, *args, **kwargs):
        oauthid = self.kwargs['oauthid']
        oauthuser = get_object_or_404(OAuthUser, pk=oauthid)
        if oauthuser.email:
            return HttpResponseRedirect('/')
        return super(RequireEmailView, self).get(request, *args, **kwargs)

    def get_initial(self):
        oauthid = self.kwargs['oauthid']
        return {'email': '', 'oauthid': oauthid}

    def get_context_data(self, **kwargs):
        oauthid = self.kwargs['oauthid']
        oauthuser = get_object_or_404(OAuthUser, pk=oauthid)
        if oauthuser.picture:
            kwargs['picture'] = oauthuser.picture
            return super(RequireEmailView, self).get_context_data(**kwargs)

    def form_valid(self, form):
        email = form.cleaned_data['email']
        oauthid = form.cleaned_data['oauthid']
        oauthuser = get_object_or_404(OAuthUser, pk=oauthid)
        oauthuser.email = email
        oauthuser.save()
        sign = get_md5(settings.SECRET_KEY + str(oauthuser.id) + settings.SECRET_KEY)
        site = get_current_site().domain
        if settings.DEBUG:
            site = '127.0.0.1:8000'
        path = reverse('oauth: email_confirm', kwargs={'id': oauthid, 'sign': sign})
        url = 'http://{site}{path}'.format(site=site, path=path)
        content = """
        <p>请点击下面的链接绑定您的邮箱</p>
        <a href="{url}" rel="bookmark">{url}</a>
        再次感谢您！
        <br />
        """.format(url=url)
        send_email(emailto=[email, ], title='绑定您的电子邮箱', content=content)
        url = reverse('oauth: bind_success', kwargs={'oauthid': oauthid})
        url = url + '?type=email'
        return HttpResponseRedirect(url)


def bind_success(request, oauthid):
    """绑定成功"""
    type = request.GET.get('type', None)
    oauthuser = get_object_or_404(OAuthUser, pk=oauthid)
    if type == 'email':
        title = '绑定成功'
        content = '请登录您的邮箱查看邮件完成绑定，谢谢！'
    else:
        title = '绑定成功'
        content = '恭喜您绑定成功， 您可以使用{type}来直接免密登录本网站， 感谢您对本站的支持。'.format(type=oauthuser.type)
    return render(request, 'oauth/bind_success.html', {'title': title, 'content': content})
