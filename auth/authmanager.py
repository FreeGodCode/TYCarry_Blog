import json
import logging
import urllib
from urllib import parse

import requests

from Blog.utils import cache_decorator
from auth.models import AuthConfig, AuthUser

logger = logging.Logger(__name__)

class AuthAccessTokenException(Exception):
    """auth授权失败"""
    pass


class BaseAuthManager(metaclass=ABCMeta):
    """获取用户权限"""
    AUTH_URL = None
    # 获取token
    TOKEN_URL = None
    # 获取用户信息
    API_URL = None
    # icon图标名
    ICON_NAME = None

    def __init__(self, access_token=None, openid=None):
        self.access_token = access_token
        self.openid = openid

    @property
    def is_access_token_set(self):
        return self.access_token is not None

    @property
    def is_authorized(self):
        return self.is_access_token_set and self.access_token is not None and self.openid is not None

    @abstractmethod
    def get_authorization_url(self, nexturl='/'):
        pass

    @abstractmethod
    def get_access_token_by_code(self, code):
        pass

    @abstractmethod
    def get_auth_userinfo(self):
        pass

    def do_get(self, url, params, headers=None):
        resp = requests.get(url=url, params=params, headers=headers)
        logger.info(resp.text)
        return resp.text

    def do_post(self, url, params, headers=None):
        resp = requests.post(url, params, headers=headers)
        logger.info(resp.text)
        return resp.text

    def get_config(self):
        value = AuthConfig.objects.filter(type=self.ICON_NAME)
        return value[0] if value else None


class WBauthManager(BaseAuthManager):
    AUTH_URL = 'https://api.weibo.com/auth2/authorize'
    TOKEN_URL = 'https://api.weibo.com/auth2/access_token'
    API_URL = 'https://api.weibo.com/2/users/show.json'
    ICON_NAME = 'weibo'

    def __init__(self, access_token=None, openid=None):
        config = self.get_config()
        self.client_id = config.appkey if config else ''
        self.client_secret = config.appsecret if config else ''
        self.callback_url = config.callback_url if config else ''
        super(WBauthManager, self).__init__(access_token=access_token, openid=openid)

    def get_authorization_url(self, nexturl = '/'):
        params = {
            'client_id': self.client_id,
            'response_type': 'code',
            'redirect_url': self.callback_url + '&next_url=' + nexturl
        }
        url = self.AUTH_URL + '?' + urllib.parse.urlencode(params)
        return url

    def get_access_token_by_code(self, code):
        params = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'grant_type': 'authorization_code',
            'code': code,
            'redircet_url': self.callback_url,
        }
        resp = self.do_post(self.TOKEN_URL, params)
        obj = json.loads(resp)
        if 'access_token' in obj:
            self.access_token = str(obj['access_token'])
            self.openid = str(obj['uid'])
            return self.get_auth_userinfo()
        else:
            raise AuthAccessTokenException(resp)

    def get_auth_userinfo(self):
        if not self.is_authorized:
            return None
        params =  {
            'uid': self.openid,
            'access_token': self.access_token,
        }
        resp = self.do_get(self.API_URL, params)
        try:
            datas = json.loads(resp)
            user = AuthUser()
            user.matadata = resp
            user.picture = datas['avatar_large']
            user.nickname = datas['screen_name']
            user.openid = datas['id']
            user.type = 'weibo'
            user.token = self.access_token
            if 'email' in datas and datas['email']:
                user.email = datas['email']
            return user
        except Exception as e:
            logger.error(e)
            logger.error('weibo auth error.resp:' + resp)
            return None


class GoogleAuthManager(BaseAuthManager):
    """docstring"""
    AUTH_URL = 'https://www.googleapis.com/o/auth2/v2/auth'
    TOKEN_URL = 'https://www.googleapis.com/auth2/v4/token'
    API_URL = 'https://www.googleapis.com/auth2/v3/userinfo'
    ICON_NAME = 'google'

    def __init__(self, access_token=None, openid=None):
        config = self.get_config()
        self.client_id = config.appkey if config else ''
        self.client_secret = config.appsecret if config else ''
        self.callback_url = config.callback_url if config else ''
        super(GoogleAuthManager, self).__init__(access_token=access_token, openid=openid)

    def get_authorization_url(self, nexturl='/'):
        params = {
            'client_id': self.client_id,
            'response_type': 'code',
            'redirect_url': self.callback_url,
            'scope': 'openid email',
        }
        # url = self.AUTH_URL + '?' + urllib.parse.urlencode(params, quote_via=urllib.parse.quote)
        url = self.AUTH_URL + '?' + urllib.parse.urlencode(params)
        return url

    def get_access_token_by_code(self, code):
        params = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_url': self.callback_url,
        }
        resp = self.do_post(self.TOKEN_URL, params)
        obj = json.loads(resp)
        if 'access_token' in obj:
            self.access_token = str(obj['access_token'])
            self.openid = str(obj['id_token'])
            logger.info(self.ICON_NAME + 'auth' + resp)
            return self.access_token
        else:
            raise AuthAccessTokenException(resp)

    def get_auth_userinfo(self):
        if not self.is_authorized:
            return None
        params = {
            'access_token': self.access_token
        }
        resp = self.do_get(self.API_URL, params)
        try:
            datas = json.loads(resp)
            user = AuthUser()
            user.metadata = resp
            user.picture = datas['picture']
            user.nickname = datas['name']
            user.openid = datas['sub']
            user.token = self.access_token
            user.type = 'google'
            if datas['email']:
                user.email = datas['email']
            return user
        except Exception as e:
            logger.error(e)
            logger.error('google auth error.resp: ' + resp)
            return None


class GitHubAuthManager(BaseAuthManager):
    """"""
    AUTH_URL = 'https://github.com/login/auth/authorize'
    TOKEN_URL = 'https://github.com/login/auth/access_token'
    API_URL = 'https://api.github.com/user'
    ICON_NAME = 'github'

    def __init__(self, access_token=None, openid=None):
        config = self.get_config()
        self.client_id = config.appkey if config else ''
        self.client_secret = config.appsecret if config else ''
        self.callback_url = config.callback_url if config else ''
        super(GitHubAuthManager, self).__init__(access_token=access_token, openid=openid)

    def get_authorization_url(self, nexturl='/'):
        params = {
            'client_id': self.client_id,
            'response_type': 'code',
            'redirect_url': self.callback_url + '&next_url=' + nexturl,
            'scope': 'user',
        }
        url = self.AUTH_URL + "?" + urllib.parse.urlencode(params)
        return url

    def get_access_token_by_code(self, code):
        params = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_url': self.callback_url,
        }
        resp = self.do_post(self.TOKEN_URL, params)
        r = parse.parse_qs(resp)
        if 'access_token' in r:
            self.access_token = r['access_token'][0]
            return self.access_token
        else:
            raise AuthAccessTokenException(resp)

    def get_auth_userinfo(self):
        resp = self.do_get(self.API_URL, params={}, headers={'Authorization': 'token' + self.access_token})
        try:
            datas = json.loads(resp)
            user = AuthUser()
            user.picture = datas['avatar_url']
            user.nickname = datas['name']
            user.openid = datas['id']
            user.type = 'github'
            user.token = self.access_token
            user.matedata = resp
            if 'email' in datas and datas['email']:
                user.email = datas['email']
            return user
        except Exception as e:
            logger.error(e)
            logger.error('github auth error.resp: ' + resp)
            return None


class FaceBookAuthManager(BaseAuthManager):
    """"""
    AUTH_URL = 'https://www.facebook.com/v2.10/dialog/auth'
    TOKEN_URL = 'https://graph.facebook.com/v2.10/auth/access_token'
    API_URL = 'https://graph.facebook.com/me'
    ICON_NAME = 'facebook'

    def __init__(self, access_token=None, openid=None):
        config = self.get_config()
        self.client_id = config.appkey if config else ''
        self.client_secret = config.appsecret if config else ''
        self.callback_url = config.callback_url if config else ''
        super(FaceBookAuthManager, self).__init__(access_token=access_token, openid=openid)

    def get_authorization_url(self, nexturl='/'):
        params = {
            'client_id': self.client_id,
            'response_type': 'code',
            'redirect_url': self.callback_url + '&next_url=' + nexturl,
            'scope': 'email, public_profile'
        }
        url = self.AUTH_URL + "?" + urllib.parse.urlencode(params)
        return url

    def get_access_token_by_code(self, code):
        params = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'code': code,
            'redirect_url': self.callback_url,
        }
        resp = self.do_post(self.TOKEN_URL, params)
        obj = json.loads(resp)
        if 'access_token' in obj:
            token = str(obj['access_token'])
            self.access_token = token
            return self.access_token
        else:
            raise AuthAccessTokenException(resp)

    def get_auth_userinfo(self):
        params = {
            'access_token': self.access_token,
            'fields': 'id, name, picture, email'
        }
        try:
            resp = self.do_get(self.API_URL, params)
            datas = json.loads(resp)
            user = AuthUser()
            user.nickname = datas['name']
            user.openid = datas['id']
            user.type = 'facebook'
            user.token = self.access_token
            user.metadata = resp
            if 'email' in datas and datas['email']:
                user.email = datas['email']
            if 'picture' in datas and datas['picture'] and datas['picture']['data'] and datas['picture']['data']['url']:
                user.picture = str(datas['picture']['data']['url'])
            return user
        except Exception as e:
            logger.error(e)
            return None


class QQauthManager(BaseAuthManager):
    """"""
    AUTH_URL = ''
    TOKEN_URL = ''
    API_URL = ''
    OPEN_ID_URL = ''
    ICON_NAME = ''

    def __init__(self, access_token=None, openid=None):
        config = self.get_config()
        self.client_id = config.appkey if config else ''
        self.client_secret = config.appsecret if config else ''
        self.callback_url = config.callback_url if config else ''
        super(QQauthManager, self).__init__(access_token=access_token, openid=openid)

    def get_authorization_url(self, nexturl='/'):
        params = {
            'response_type': 'code',
            'client_id': self.client_id,
            'redirect_url': self.callback_url + '&next_url=' + nexturl,
        }
        url = self.AUTH_URL + "?" + urllib.parse.urlencode(params)
        return url

    def get_access_token_by_code(self, code):
        params = {
            'grant_type': 'authorization_code',
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'code': code,
            'redirect_url': self.callback_url,
        }
        resp = self.do_get(self.TOKEN_URL, params)
        if resp:
            d = urllib.parse.parse_qs(resp)
            if 'access_token' in d:
                self.access_token = d['access_token']
                return d['access_token']
            else:
                raise AuthAccessTokenException(resp)

    def get_open_id(self):
        if self.is_access_token_set:
            params = {
                'access_token': self.access_token,
            }
            resp = self.do_get(self.OPEN_ID_URL, params)
            if resp:
                resp = resp.replace('callback(', '').replace(')', '').replace(';', '')
                obj = json.loads(resp)
                openid = str(obj['openid'])
                self.openid = openid
                return openid

    def get_auth_userinfo(self):
        openid = self.get_open_id()
        if openid:
            params = {
                'access_token': self.access_token,
                'auth_consumer_key': self.client_id,
                'openid': self.openid,
            }
            resp = self.do_get(self.API_URL, params)
            logger.info(resp)
            obj = json.loads(resp)
            user = AuthUser()
            user.nickname = obj['nickname']
            user.openid = openid
            user.type = 'qq'
            user.token = self.access_token
            user.matedata = resp
            if 'email' in obj:
                user.email = obj['email']
            if 'figureurl' in obj:
                user.picture = str(obj['figureurl'])
            return user

@cache_decorator(expiration = 60 *60)
def get_auth_apps():
    """

    :return:
    """
    configs = AuthConfig.objects.filter(is_enable=True).all()
    if not configs:
        return []
    configtypes = [x.type for x in configs]
    applications = BaseAuthManager.__subclasses__()
    apps = [x() for x in applications if x().ICON_NAME.lower() in configtypes]
    return apps

def get_manager_by_type(type):
    applications = get_auth_apps()
    if applications:
        finds = list(filter(lambda x: x.ICON_NAME.lower() == type.lower(), applications))
        if finds:
            return finds[0]
    return None
