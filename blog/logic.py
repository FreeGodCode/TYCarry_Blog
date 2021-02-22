# -*- coding: utf-8 -*-
# @Author:  ty
# @FileName: logic.py
# @Time:  2021/2/19 下午11:09
# @Description: 逻辑实现
import datetime
import logging
import os

from django import forms
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.http import HttpResponseForbidden, HttpResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView, DetailView

from Blog.utils import get_md5, get_blog_setting
from blog.models import LinkShowType, Article, Category, Tag, Links
from comment.forms import CommentForm

logger = logging.getLogger(__name__)


class ArticleListView(ListView):
    """文章列表页面"""
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
            logger.info('get view cache.key: {key}'.format(key=cache_key))
            return value
        else:
            article_list = self.get_queryset_data()
            cache.set(cache_key, article_list)
            logger.info('set view cache.key: {key}'.format(key=cache_key))
            return article_list

    def get_queryset(self):
        """重写默认，从缓存获取数据"""
        key = self.get_queryset_cache_key()
        value = self.get_queryset_from_cache(key)
        return value

    def get_context_data(self, **kwargs):
        kwargs['linktype'] = self.link_type
        return super(ArticleListView, self).get_context_data(**kwargs)


class IndexView(ArticleListView):
    """首页"""
    link_type = LinkShowType.I  # 友情链接类型

    def get_queryset_data(self):
        article_list = Article.objects.filter(type='a', status='p')
        return article_list

    def get_queryset_cache_key(self):
        cache_key = 'index_{page}'.format(page=self.page_number)
        return cache_key


class ArticleDetailView(DetailView):
    """文章详情页面"""
    template_name = 'blog/article_detail.html'
    model = Article
    pk_url_kwarg = 'article_id'
    context_object_name = 'article'

    def get_object(self, queryset=None):
        obj = super(ArticleDetailView, self).get_object()
        obj.viewed()
        self.object = obj
        return obj

    def get_context_data(self, **kwargs):
        articleid = int(self.kwargs[self.pk_url_kwarg])
        comment_form = CommentForm()
        user = self.request.user
        if user.is_authenticated and not user.is_anonymous and user.email and user.username:
            comment_form.fields.update({
                'email': forms.CharField(widget=forms.HiddenInput()),
                'name': forms.CharField(widget=forms.HiddenInput()),
            })
            comment_form.fields['email'].initial = user.email
            comment_form.fields['name'].initial = user.username

        article_comments = self.object.comment_list()
        kwargs['form'] = comment_form
        kwargs['article_comments'] = article_comments
        kwargs['comment_count'] = len(article_comments) if article_comments else 0
        kwargs['next_article'] = self.object.next_article
        kwargs['prev_article'] = self.object.prev_article

        return super(ArticleDetailView, self).get_context_data(**kwargs)


class CategoryDetailView(ArticleListView):
    """分类目录列表"""
    page_type = '分类目录归档'

    def get_queryset_data(self):
        slug = self.kwargs['category_name']
        category = get_object_or_404(Category, slug=slug)
        categoryname = category.name
        self.categoryname = categoryname
        categorynames = list(map(lambda c: c.name, category.get_sub_categorys()))
        article_list = Article.objects.filter(category_name__in=categorynames, status='p')
        return article_list

    def get_queryset_cache_key(self):
        slug = self.kwargs['category_name']
        category = get_object_or_404(Category, slug=slug)
        categoryname = category.name
        self.categoryname = categoryname
        cache_key = 'category_list_{categoryname}_{page}'.format(categoryname=categoryname, page=self.page_number)
        return cache_key

    def get_context_data(self, **kwargs):
        categoryname = self.categoryname
        try:
            categoryname = categoryname.split('/')[-1]
        except BaseException:
            pass
        kwargs['page_type'] = CategoryDetailView.page_type
        kwargs['tag_name'] = categoryname
        return super(CategoryDetailView, self).get_context_data(**kwargs)


class AuthorDetailView(ArticleListView):
    """作者详情页"""
    page_type = '作者文章归档'

    def get_queryset_data(self):
        author_name = self.kwargs['author_name']
        article_list = Article.objects.filter(author__username=author_name, type='a', status='p')
        return article_list

    def get_queryset_cache_key(self):
        author_name = self.kwargs['author_name']
        cache_key = 'author_{author_name}_{page}'.format(author_name=author_name, page=self.page_number)
        return cache_key

    def get_context_data(self, **kwargs):
        author_name = self.kwargs['author_name']
        kwargs['page_type'] = AuthorDetailView.page_type
        kwargs['tag_name'] = author_name
        return super(AuthorDetailView, self).get_context_data(**kwargs)


class TagDetailView(ArticleListView):
    """变迁列表页面"""
    page_type = '分类标签归档'

    def get_queryset_data(self):
        slug = self.kwargs['tag_name']
        tag = get_object_or_404(Tag, slug=slug)
        tag_name = tag.name
        self.name = tag_name
        article_list = Article.objects.filter(tags__name=tag_name, type='a', status='p')
        return article_list

    def get_queryset_cache_key(self):
        slug = self.kwargs['tag_name']
        tag = get_object_or_404(Tag, slug=slug)
        tag_name = tag.name
        self.name = tag_name
        cache_key = 'tag_{tag_name}_{page}'.format(tag_name=tag_name, page=self.page_number)
        return cache_key

    def get_context_data(self, **kwargs):
        tag_name = self.name
        kwargs['page_type'] = TagDetailView.page_type
        kwargs['tag_name'] = tag_name
        return super(TagDetailView, self).get_context_data(**kwargs)


class ArchivesView(ArticleListView):
    """文章归档页面"""
    page_type = '文章归档'
    paginate_by = None
    page_kwarg = None
    template_name = 'blog/article_archives.html'

    def get_queryset_data(self):
        return Article.objects.filter(status='p').all()

    def get_queryset_cache_key(self):
        cache_key = 'archives'
        return cache_key


class LinkListView(ListView):
    """"""
    model = Links
    template_name = 'blog/links_list.html'

    def get_queryset(self):
        return Links.objects.filter(is_enable=True)


@csrf_exempt
def fileupload(request):
    """图片上传"""
    if request.method == 'POST':
        sign = request.GET.get('sign', None)
        if not sign:
            return HttpResponseForbidden()
        if not sign == get_md5(get_md5(settings.SECRET_KEY)):
            return HttpResponseForbidden()
        response = []
        for filename in request.FILES:
            timestr = datetime.datetime.now().strftime('%Y%m%d')
            imgextensions = ['jpg', 'png', 'jpeg', 'bmp']
            file_name = ''.join(str(filename))
            is_image = len([i for i in imgextensions if file_name.find(i) >= 0]) > 0
            blogsetting = get_blog_setting()
            basepath = r'{basedir}/{type}/{timestr}'.format(basedir=blogsetting.resource_path,
                                                            type='files' if not is_image else 'image', timestr=timestr)

            if settings.TESTING:
                basepath = settings.BASE_DIR + '/uploads'
            url = 'http://localhost/{type}/{timestr}/{filename}'.format(type='files' if not is_image else 'image',
                                                                        timestr=timestr, filename=filename)

            if not os.path.exists(basepath):
                os.makedirs(basepath)
            savepath = os.path.join(basepath, filename)
            with open(savepath, 'wb') as f:
                for chunk in request.FILES[filename].chunks():
                    f.write(chunk)
            if is_image:
                from PIL import Image
                image = Image.open(savepath)
                image.save(savepath, quality=20, optimize=True)
            response.append(url)
        return HttpResponse(response)
    else:
        return HttpResponse('only for post')


@login_required
def refresh_memcache(request):
    try:
        if request.user.is_superuser:
            if cache and cache is not None:
                cache.clear()
            return HttpResponse('ok')
        else:
            return HttpResponseForbidden()
    except Exception as e:
        return HttpResponse(e)


def page_not_found_view(request, exception, template_name='blog/error_page.html'):
    """访问的URL地址没有匹配到"""
    if exception:
        logger.error(exception)

    url = request.get_full_path()
    return render(request, template_name, {'message': 'page not found', 'statuscode': '404'}, status=404)


def server_error_view(request, template_name='blog/error_page.html'):
    """服务器内部错误"""
    return render(request, template_name, {'message': 'server internal error', 'statuscode': '500'}, status=500)


def permission_denied_view(request, exception, template_name='blog/error_page.html'):
    """没有权限访问此页面"""
    return render(request, template_name, {'message': 'permission denied', 'statuscode': '403'}, status=403)
