from django.db import models

# Create your models here.
from django.utils.timezone import now


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
        self.comment_num -=1
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
class Article(models.Model):
    STATIC_CHOICES = (
        ('d', '草稿'),
        ('p', "发表"),
    )
    article_id = models.CharField(verbose_name='标号', max_length=100)
    title = models.CharField(verbose_name='标题', max_length=100)
    content = models.TextField(verbose_name="正文", blank=True, null=True)
    status = models.CharField(verbose_name="状态", max_length=1, choices=STATIC_CHOICES, default='p')
    views = models.PositiveIntegerField(verbose_name="浏览量", default=0)
    created_time = models.DateTimeField(verbose_name='创建时间', default=now)
    category = models.ForeignKey(Category, verbose_name='分类', on_delete=models.CASCADE, blank=False, null=False)
    tags = models.ManyToManyField(Tag, verbose_name='标签集合', blank=True)

    def __str__(self):
        return self.title

    # 更新浏览量
    def viewed(self):
        self.views += 1
        self.save(update_fields=['views'])

    # 下一篇
    def next_article(self):
        return Article.objects.filter(id__gt=self.id, status='p', pub_time__isnull=False).first()

    # 上一篇
    def pre_article(self):
        return Article.objects.filter(id__lt=self.id, status='p', pub_time__isnull=False).first()

    class Meta:
        ordering = ['-created_time']
        verbose_name = '文章'
        verbose_name_plural = '文章列表'
        db_table = 'article'
        get_latest_by = 'created_time'
