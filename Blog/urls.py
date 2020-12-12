"""Blog URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls import url
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from Blog.sitemap import ArticleSiteMap, CategorySiteMap, TagSiteMap, UserSiteMap, StaticViewsSiteMap

sitemaps = {
    'blog': ArticleSiteMap,
    'Category': CategorySiteMap,
    'Tag': TagSiteMap,
    'User': UserSiteMap,
    'static': StaticViewsSiteMap,
}

handler404 = 'blog.views.page_not_found_view'
handler500 = 'blog.views.server_error_view'
handler403 = 'blog.views.permission_denied_view'

urlpatterns = [
    path('admin/', admin.site.urls),
    url(r'^blog/', include(("blog.urls", 'blog'), namespace='blog')),
    url(r'^comment/', include(('comment.urls', 'comment'), namespace='comment')),
    url(r'^auth/', include(('auth.urls', 'auth'), namespace='auth')),
    url(r'^owntracks/', include(('owntracks.urls', 'owntracks'), namespace='owntracks')),
    url(r'^servermanager/', include(('servermanager.urls', 'servermanager'), namespace='servermanager')),

    url(r'^mdeditor/', include('mdeditor.urls')),
    url(r'^search/', include(haystack.urls), name='search'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root = settings.MEDIA_URL)