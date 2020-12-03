from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from blog.models import Article, Category, Tag


class StaticViewsSiteMap(Sitemap):
    priority = 0.5
    changefreq = 'daily'

    def items(self):
        return ['blog: index', ]

    def location(self, item):
        return reverse(item)


class ArticleSiteMap(Sitemap):
    priority = 0.6
    changefreq = 'monthly'

    def items(self):
         return Article.objects.filter(status='p')

    def lastmod(self, obj):
        return obj.last_mod_time


class CategorySiteMap(Sitemap):
    priority = 0.6
    changefreq = 'Weekly'

    def items(self):
        return Category.objects.all()

    def lastmod(self, obj):
        return obj.last_mod_time


class TagSiteMap(Sitemap):
    priority = 0.3
    changefreq = 'Weekly'

    def items(self):
        return Tag.objects.all()

    def lastmod(self, obj):
        return obj.last_mod_time


class UserSiteMap(Sitemap):
    priority = 0.3
    changefreq = 'Weekly'

    def items(self):
        return list(set(map(lambda x: x.author, Article.objects.all())))

    def lastmod(self, obj):
        return obj.date_joined
