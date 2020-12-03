import json
import logging

import requests

logger = logging.getLogger(__name__)

class Tuling():
    def __init__(self):
        self.__key__ = ''
        self.__appid__ = ''

    def __build_req_url(self, content):
        return 'http://www.xxx.com/openapi/api?key=%s&info=%s&userid=%s' %(self.__key__, content, self.__appid__)

    def UserAgent(self, url):
        resp = requests.get(url)
        return resp.content

    def getdata(self, content):
        try:
            requrl = self.__build_req_url((content))
            resp = self.UserAgent(requrl).decode('utf-8')
            jsons = json.loads(resp, encode='utf-8')
            if str(jsons['code']) == '10000':
                return jsons['text']
        except Exception as e:
            logger.error(e)
        return 'Error!'