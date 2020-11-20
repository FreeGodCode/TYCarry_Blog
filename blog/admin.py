from django.contrib import admin

from blog.models import Article, Category, Tag, User, ArticleComment
# Register your models here.


from django_summernote.admin import SummernoteModelAdmin

class PostAdmin(SummernoteModelAdmin):
    summernote_fields = ('content') #给content字段添加富文本
    list_display = ['article_id', 'title', 'created_time'] #列表显示字段
    search_fields = ['title'] #搜索框
    list_filter = ['created_time'] #过滤器


"""
from tinymce.models import HTMLField
class Blog(models.Model):
    sblog = HTMLField()
    
在页面的head中添加script
<script>
    tinyMCE.init({
        'mode': 'textareas',
        'theme': 'advanced',
        'width': 800,
        'height': 600,
    })
</script>
"""


class CommentAdmin(admin.ModelAdmin):
    list_display = ['username', 'body', 'title']
    search_fields = ['title']


admin.site.register(Article, PostAdmin)
admin.site.register(Category)
admin.site.register(Tag)
admin.site.register(User)
admin.site.register(ArticleComment, CommentAdmin)
