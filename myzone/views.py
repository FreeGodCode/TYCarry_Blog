from django.shortcuts import render

from django.views.generic import ListView


# Create your views here.
from myzone.models import TalkContent


ARTICLE_PAGINATE_BY = 10
class TalkView(ListView):
    """说说视图函数类"""
    model = TalkContent
    template_name = 'myzone/talk.html'
    context_object_name = 'talk_lists'
    # paginate_by = settings.ARTICLE_PAGINATE_BY
    paginate_by = ARTICLE_PAGINATE_BY

    def get_queryset(self):
        return TalkContent.objects.filter(status='Y')