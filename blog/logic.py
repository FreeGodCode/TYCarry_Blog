# -*- coding: utf-8 -*-
# @Author:  ty
# @FileName: logic.py
# @Time:  2021/2/19 下午11:09
# @Description: 逻辑实现
import logging

from django.conf import settings
from django.views.generic import ListView

from blog.models import LinkShowType

logger = logging.getLogger(__name__)


class ArticleListView(ListView):
    template_name = 'blog/article_index.html'  # 指定使用那个模板进行渲染
    context_object_name = 'article_list'  # 用来给上下文变量取名
    page_type = ''
    paginate_by = settings.PAGINATE_BY
    page_kwarg = 'page'
    link_type = LinkShowType.L

    def get_view_cache_key(self):
        return self.request.get['pages']

    @property
    def page_number(self):
        page_kwarg = self.page_kwarg
        page = self.kwargs.get(page_kwarg) or self.request.GET.get(page_kwarg) or 1
        return page

    def get_queryset_cache_key(self):
        """子类重写，获取queryset的缓存key"""
        raise NotImplementedError()

    def get_queryset_data(self):
        """获取queryset的数据"""
        raise NotImplementedError()

    def get_queryset_from_cache(self, cache_key):
        """缓存页面数据"""
        value = cache.get(cache_key)
        if value:
            logger.info()




