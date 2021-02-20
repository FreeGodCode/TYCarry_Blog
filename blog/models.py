from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy
from django.utils.timezone import now


# Create your models here.
# 用户
class User(models.Model):
    # __tablename__ = "user"
    username = models.CharField(max_length=50)
    password = models.CharField(max_length=200)
    nickname = models.CharField(max_length=50, default="匿名")
    email = models.EmailField()
    # 创建时间默认为创建当前之间
    created_time = models.CharField(max_length=50, default=now)
    # 评论数为正整数
    comment_num = models.PositiveIntegerField(verbose_name="评论数", default=0)
    # 头像,上传文件
    avatar = models.ImageField(upload_to='media', default="media/default.png")

    def __str__(self):
        return self.username

    # 有评论,评论数加1,更新评论数
    def comment(self):
        self.comment_num += 1
        self.save(update_fields=['comment_num'])

    # 删除评论,评论数量减1,然后保存
    def del_comment(self):
        self.comment_num -= 1
        self.save(update_fields=['comment_num'])


# 文章评论
class ArticleComment(models.Model):
    # __tablename__ = 'comment'
    body = models.TextField()
    username = models.CharField(max_length=50)
    userimg = models.CharField(max_length=70)
    nickname = models.CharField(max_length=50, default='匿名')
    create_time = models.DateTimeField(verbose_name='创建时间', default=now)
    article = models.CharField(max_length=50)
    title = models.CharField(max_length=50)

    def __str__(self):
        return self.article

    # 通过内部类定义展示形式
    class Meta:
        # 指定数据在后台管理中的排列方式,默认为升序,降序在字段名前加'-'
        ordering = ['-create_time']
        # 指定后台显示的名称(单数)
        verbose_name = '评论'
        # 指定后台显示模型复数名称
        verbose_name_plural = '评论列表'
        # 指定实体类映射到表的名称
        db_table = 'comment'

    list_display = ('article', 'body')


# 文章标签
class Tag(models.Model):
    # __tablename__ = "tag"
    name = models.CharField(verbose_name='标签名', max_length=64)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']
        verbose_name = "标签名称"
        verbose_name_plural = "标签列表"
        db_table = 'tag'


# 博客文章分类
class Category(models.Model):
    # __tablename__ = "category"
    name = models.CharField(verbose_name="类别名称", max_length=64)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']
        verbose_name = '类别名称'
        verbose_name_plural = "类别列表"
        db_table = 'category'


# 博客文章
# class Article(models.Model):
#     STATIC_CHOICES = (
#         ('d', '草稿'),
#         ('p', "发表"),
#     )
#     article_id = models.CharField(verbose_name='标号', max_length=100)
#     title = models.CharField(verbose_name='标题', max_length=100)
#     content = models.TextField(verbose_name="正文", blank=True, null=True)
#     status = models.CharField(verbose_name="状态", max_length=1, choices=STATIC_CHOICES, default='p')
#     views = models.PositiveIntegerField(verbose_name="浏览量", default=0)
#     created_time = models.DateTimeField(verbose_name='创建时间', default=now)
#     category = models.ForeignKey(Category, verbose_name='分类', on_delete=models.CASCADE, blank=False, null=False)
#     tags = models.ManyToManyField(Tag, verbose_name='标签集合', blank=True)
#
#     def __str__(self):
#         return self.title
#
#     # 更新浏览量
#     def viewed(self):
#         self.views += 1
#         self.save(update_fields=['views'])
#
#     # 下一篇
#     def next_article(self):
#         return Article.objects.filter(id__gt=self.id, status='p', pub_time__isnull=False).first()
#
#     # 上一篇
#     def pre_article(self):
#         return Article.objects.filter(id__lt=self.id, status='p', pub_time__isnull=False).first()
#
#     class Meta:
#         ordering = ['-created_time']
#         verbose_name = '文章'
#         verbose_name_plural = '文章列表'
#         db_table = 'article'
#         get_latest_by = 'created_time'


# class MovieCategory(models.Model):
#     """电影分类"""
#     name = models.CharField(max_length=100, verbose_name='电影分类')
#
#     def __str__(self):
#         return self.name
#
#     class Meta:
#         db_table = 'db_movie_category'
#         verbose_name = '电影分类'
#         verbose_name_plural = '电影分类列表'
#
#
# class MovieTag(models.Model):
#     """电影标签"""
#     name = models.CharField(max_length=100, verbose_name='标签名称', blank=True)
#
#     def __str__(self):
#         return self.name
#
#     def get_absolute_url(self):
#         return reverse('blog: movie_list', kwargs={'pk': self.pk})
#
#     class Meta:
#         db_table = 'db_movie_tag'
#         verbose_name = '电影标签名称'
#         verbose_name_plural = '电影标签列表'
#
#
# class Movie(models.Model):
#     """电影"""
#     name = models.CharField(max_length=100, verbose_name='电影名称')
#     director = models.CharField(max_length=100, verbose_name='导演')
#     actor = models.CharField(max_length=50, verbose_name='主演')
#     category = models.ForeignKey(MovieCategory, on_delete=models.CASCADE, verbose_name='电影分类')
#     tag = models.ForeignKey(MovieTag, on_delete=models.CASCADE, verbose_name='电影标签')
#     cover = models.ImageField(upload_to='movies', blank=True, null=True, verbose_name='上传封面')
#     score = models.DecimalField(max_digits=2, decimal_places=1, verbose_name='豆瓣评分')
#     release_time = models.DateField('上映时间')
#     created_time = models.DateField(default=timezone.now, verbose_name='添加时间')
#     length_time = models.PositiveIntegerField(default=0, verbose_name='电影时长')
#     watch_time = models.DateField(default=timezone.now(), verbose_name='观看时间')
#     pid = models.CharField(max_length=100, blank=True, null=True, verbose_name='文章id')
#
#     def __str__(self):
#         return self.name
#
#     def get_absolute_url(self):
#         return reverse('blog: article', kwargs={'pk': self.pid})
#
#     class Meta:
#         db_table = 'db_movie'
#         verbose_name = '电影'
#         verbose_name_plural = '电影列表'
#
#
# class Message(models.Model):
#     """docstring"""
#     name = models.CharField(max_length=100, verbose_name='留言')
#     admin = models.ForeignKey(User, verbose_name='站长', on_delete=models.CASCADE, blank=True, null=True)
#
#     def get_absolute_url(self):
#         return reverse('blog: messages')
#
#     def get_user(self):
#         return self.admin
#
#     class Meta:
#         db_table = 'db_messages'
#         verbose_name = '网站留言'
#         verbose_name_plural = verbose_name
#
#
# class MeanList(models.Model):
#     """菜单"""
#     STATUS_CHOICES = (
#         ('y', '显示'),
#         ('n', '隐藏')
#     )
#     title = models.CharField(max_length=100, verbose_name='菜单名称')
#     link = models.CharField(max_length=100, verbose_name='菜单链接', blank=True, null=True)
#     icon = models.CharField(max_length=100, verbose_name='菜单图标', blank=True, null=True)
#     status = models.CharField(max_length=1, verbose_name='显示状态', choices=STATUS_CHOICES, default='y')
#
#     class Meta:
#         db_table = 'db_mean_list'
#         verbose_name = '菜单栏'
#         verbose_name_plural = verbose_name

class LinkShowType(models.TextChoices):
    I = ('i', '首页')
    L = ('l', '列表页')
    P = ('p', '文章页面')
    A = ('a', '全站')
    S = ('s', '友情链接页面')


class BaseModel(models.Model):
    id = models.AutoField(primary_key=True)
    created_time = models.DateTimeField(verbose_name='创建时间', default=now)
    last_modify_time = models.DateTimeField(verbose_name='修改时间', default=now)

    def save(self, *args, **kwargs):
        is_update_views = isinstance(self, Article) and 'update_fields' in kwargs and kwargs['update_fields'] == [
            'views']
        if is_update_views:
            Article.objects.filter(pk=self.pk).update(views=self.views)
        else:
            if 'slug' in self.__dict__:
                slug = getattr(self, 'title') if 'title' in self.__dict__ else getattr(self, 'name')
                setattr(self, 'slug', slugify(slug))
            super(BaseModel, self).save(*args, **kwargs)

    def get_full_url(self):
        site = get_current_site().domain
        url = 'http://{site}{path}'.format(site=site, path=self.get_absolute_url())
        return url

    class Meta:
        abstract = True

    @abstractmethod
    def get_absolute_url(self):
        pass


class Article(BaseModel):
    """文章"""
    STATUS_CHOICES = (
        ('d', '草稿'),
        ('p', '发表'),
    )
    COMMENT_STATUS = (
        ('o', '打开'),
        ('c', '关闭'),
    )
    TYPE = (
        ('a', '文章'),
        ('p', '页面'),
    )
    title = models.CharField(verbose_name='标题', max_length=200, unique=True)
    body = MDTextField(verbose_name='正文')
    pub_time = models.DateTimeField(verbose_name='发布时间', blank=False, null=False, default=now)
    status = models.CharField(verbose_name='文章状态', max_length=1, choices=STATUS_CHOICES, default='p')
    comment_status = models.CharField(verbose_name='评论状态', max_length=1, choices=COMMENT_STATUS, default='o')
    type = models.CharField('类型', max_length=1, choices=TYPE, default='a')
    views = models.PositiveIntegerField('浏览量', default=0)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name='作者', blank=False, null=False,
                               on_delete=models.CASCADE)
    article_order = models.IntegerField(verbose_name='排序,数字越大越靠前', blank=False, null=False, default=0)
    category = models.ForeignKey('Category', verbose_name='分类', on_delete=models.CASCADE, blank=False, null=False)
    tags = models.ManyToManyField('Tag', verbose_name='标签集合', blank=True)

    def body_to_string(self):
        return self.body

    def __str__(self):
        return self.title

    class Meta:
        db_table = 'db_article'
        ordering = ['-article_order', '-pub_time']
        verbose_name = '文章'
        verbose_name_plural = verbose_name
        get_latest_by = 'id'

    def get_absolute_url(self):
        return reverse('blog: detailbyid',
                       kwargs={'article_id': self.id, 'year': self.created_time.year, 'month': self.created_time.month,
                               'day': self.created_time.day})

    @cache_decoratoor(60 * 60 * 10)
    def get_category_tree(self):
        tree = self.category.get_category_tree()
        names = list(map(lambda c: (c.name, c.get_absolute_url()), tree))
        return names

    def save(self, *args, **kwargs):
        super(Article, self).save(*args, **kwargs)

    def viewed(self):
        self.views += 1
        self.save(update_fields=['views'])

    def comment_list(self):
        cache_key = 'article_comments_{id}'.format(id=self.id)
        value = cache.get(cache_key)
        if value:
            logger.info('get article comments: {id}'.format(id=self.id))
            return value
        else:
            comments = self.comment_set.filter(is_enable=True)
            cache.set(cache_key, comments, 60 * 100)
            logger.info('set article comments: {id}'.format(id=self.id))
            return comments

    def get_admin_url(self):
        info = (self._meta.app_label, self._meta.model_name)
        return reverse('admin: %s_%s_change' % info, args=(self.pk,))

    from Blog.utils import cache_decorator
    @cache_decorator(expiration=60 * 100)
    def next_article(self):
        """下一篇"""
        return Article.objects.filter(id__gt=self.id, status='p').order_by('id').first()

    @cache_decorator(expiration=60 * 100)
    def prev_article(self):
        """前一篇"""
        return Article.objects.filter(id__lt=self.id, status='p').first()


class Category(BaseModel):
    """文章分类"""
    name = models.CharField(verbose_name='分类名', max_length=30, unique=True)
    parent_category = models.ForeignKey('self', verbose_name='父级分类', null=True, blank=True, on_delete=models.CASCADE)
    slug = models.SlugField(max_length=60, blank=True, default='no_slug')

    class Meta:
        db_table = 'db_category'
        ordering = ['name']
        verbose_name = '分类'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('blog:category_detail', kwargs={'category_name': self.slug})

    def get_category_tree(self):
        """递归获取分类目录的父级"""
        categorys = []
        def parse(category):
            categorys.append(category)
            if category.parent_category:
                parse(category.parent_category)

        parse(self)
        return categorys

    def get_sub_categorys(self):
        """获取当前目录的所有子目录"""
        catetorys = []
        all_categorys = Category.objects.all()
        def parse(category):
            if category not in categorys:
                categorys.append(category)
            childs = all_categorys.filter(parent_category=category)
            for child in childs:
                if category not in categorys:
                    categorys.append(child)
                    parse(child)

        psrse(self)
        return categorys


class Links(models.Model):
    """友情链接"""
    name = models.CharField(verbose_name='链接名称', max_length=30, unique=True)
    link = models.URLField(verbose_name='链接地址')
    sequence = models.IntegerField(verbose_name='排序', unique=True)
    is_enable = models.BooleanField(verbose_name='是否显示', default=True, blank=False, null=False)
    show_type = models.CharField(verbose_name='显示类型', max_length=1, choices=LinkShowType.choices,
                                 default=LinkShowType.I)
    created_time = models.DateTimeField(verbose_name='创建时间', default=now)
    last_modify_time = models.DateTimeField(verbose_name='修改时间', default=now)

    class Meta:
        db_table = 'db_links'
        ordering = ['sequence']
        verbose_name = '友情链接'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class SideBar(models.Model):
    """侧边栏"""
    name = models.CharField(verbose_name='标题', max_length=128)
    content = models.TextField(verbose_name='内容')
    sequence = models.IntegerField(verbose_name='排序', unique=True)
    is_enable = models.BooleanField(verbose_name='是否启用', default=True)
    created_time = models.DateTimeField(verbose_name='创建时间', default=now)
    last_modify_time = models.DateTimeField(verbose_name='修改时间', default=now)

    class Meta:
        db_table = 'db_sidebar'
        ordering = ['sequence']
        verbose_name = '侧边栏'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class BlogSettings(models.Model):
    """站点设置"""
    sitename = models.CharField(verbose_name='网站名称', max_length=256, null=False, blank=False, default='')
    site_description = models.TextField(verbose_name='网站描述', max_length=1024, null=False, blank=False, default='')
    site_seo_description = models.TextField(verbose_name='网站SEO描述', max_length=1024, null=False, blank=False,
                                            default='')
    site_keywords = models.TextField(verbose_name='网站关键字', max_length=1024, null=False, blank=False, default='')
    article_sub_length = models.IntegerField(verbose_name='文章摘要长度', default=300)
    sidebar_article_count = models.IntegerField(verbose_name='侧边栏文章数目', default=10)
    sidebar_comment_count = models.IntegerField(verbose_name='侧边栏评论数目', default=5)
    show_google_adsense = models.BooleanField(verbose_name='是否显示谷歌广告', default=False)
    google_adsense_codes = models.TextField(verbose_name='google广告内容', max_length=2048, null=True, blank=True,
                                            default='')
    open_site_comment = models.BooleanField(verbose_name='是否打开网站评论功能', default=True)
    beiancode = models.TextField(verbose_name='备案号', max_length=1024, null=True, blank=True, default='')
    analyticscode = models.TextField(verbose_name='网站统计代码', max_length=1024, null=True, blank=True, default='')
    show_police_code = models.BooleanField(verbose_name='是否显示公安备案号', null=True, default=False)
    police_beiancode = models.TextField(verbose_name='公安备案号', max_length=1024, null=True, blank=True, default='')
    resource_path = models.CharField(verbose_name='静态文件保存地址', max_length=256, null=False, default='/var/www/resource/')

    class Meta:
        db_table = 'db_blogsetting'
        verbose_name = '网站设置'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.sitename

    def clean(self):
        if BlogSettings.objects.exclude(id=self.id).count():
            raise ValidationError(gettext_lazy('只能有一个配置'))

    def save(self, *args, **kwargs):
        super(BlogSettings, self).save(*args, **kwargs)
        cache.clear()
