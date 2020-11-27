from django.contrib.admin import AdminSite


class BlogAdminSite(AdminSite):
    """博客管理站点类"""
    site_header = 'Blog administration'
    site_title = 'Blog site admin'

    def _init__(self, name='admin'):
        super(BlogAdminSite, self)._init__(name)

    def has_permission(self, request):
        return request.user.is_superuser


admin_site = BlogAdminSite(name='admin')

admin_site.register()

