from django.shortcuts import render, redirect

# Create your views here.
from django.urls import reverse

from comment.forms import CommentForm
from comment.models import Comment


def update_comment(request):
    """更新评论视图函数"""
    referer = request.META.get('HTTP_REFERER', reverse('blog: index'))
    comment_form = CommentForm(request.POST, user=request.user)
    if comment_form.is_valid():
        comment = Comment()
        comment.user = comment_form.cleaned_data['user']
        comment.text = comment_form.cleaned_data['text']
        comment.content_object = comment_form.cleaned_data['content_object']
        parent = comment_form.cleaned_data['parent']

        if not parent is None:
            comment.root = parent.root if not parent.root is None else parent
            comment.parent = parent
            comment.reply_to = parent.user

        comment.save()

        # 发送站内通知
        # 判断评论时博客还是
        # if comment.reply_to is None:
        #     # 接收者是文章
        #     recipient = comment.content_object.get_user()
        #     if comment.content_type.model == 'post':
        #         blog = comment.content_object
        #         verb = '{0}评论了你的<<{1}>>'.format(comment.user, blog.title)
        #     else:
        #         raise Exception('不明评论')
        # else:
        #     recipient = comment.reply_to
        #     verb = '{0}评论类了你的评论{1}'.format(comment.user, strip_tags(comment.parent.text))
        # notify.send(comment.user, recipient=recipient, verb=verb, action_object=comment)

    return redirect(referer+'$comment')

