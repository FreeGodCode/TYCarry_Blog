# -*- coding: utf-8 -*-
# @Author:  ty
# @FileName: documents.py
# @Time:  2021/2/20 下午5:26
# @Description:
import time

from django.conf import settings
from elasticsearch_dsl import Document, Text, Long, Date, Object, Integer
from elasticsearch_dsl.connections import connections

from blog.models import Article

ELASTICSEARCH_ENABLED = hasattr(settings, 'ELASTICSEARCH_DSL')

if ELASTICSEARCH_ENABLED:
    connections.create_connection(hosts=[settings.ELASTICSEARCH_DSL['default']['hosts']])


class ElapsedTimeDocument(Document):
    """过期文档管理"""
    url = Text()
    time_taken = Long()
    log_datetime = Date()
    type = Text(analyzer='ik_max_word')
    useragent = Text()

    class Index:
        name = 'performance'
        settings = {
            "number_of_shards": 1,
            "number_of_replicas": 0
        }

    class Meta:
        doc_type = 'ElapsedTime'


class ElaspedTimeDocumentManager():
    """过期文档管理器"""
    @staticmethod
    def create(url, time_taken, log_datetime, type, useragent):
        # if not hasattr(ElaspedTimeDocumentManager, 'mapping_created'):
        #     ElapsedTimeDocument.init()
        #     setattr(ElaspedTimeDocumentManager, 'mapping_created', True)
        doc = ElapsedTimeDocument(
            meta={'id': int(round(time.time() * 1000))},
            url=url,
            time_taken=time_taken,
            log_datetime=log_datetime,
            type=type,
            useragent=useragent)
        doc.save()


class ArticleDocument(Document):
    """文章文档"""
    body = Text(analyzer='ik_max_word', search_analyzer='ik_smart')
    title = Text(analyzer='ik_max_word', search_analyzer='ik_smart')
    author = Object(properties={
        'nickname': Text(analyzer='ik_max_word', search_analyzer='ik_smart'),
        'id': Integer()
    })
    category = Object(properties={
        'name': Text(analyzer='ik_max_word', search_analyzer='ik_smart'),
        'id': Integer()
    })
    tags = Object(properties={
        'name': Text(analyzer='ik_max_word', search_analyzer='ik_smart'),
        'id': Integer()
    })

    pub_time = Date()
    status = Text()
    comment_status = Text()
    type = Text()
    views = Integer()
    article_order = Integer()

    class Index:
        name = 'blog'
        settings = {
            "number_of_shards": 1,
            "number_of_replicas": 0
        }

    class Meta:
        doc_type = 'Article'


class ArticleDocumentManager():
    """文章文档管理器"""
    def __init__(self):
        self.create_index()

    def create_index(self):
        ArticleDocument.init()

    def delete_index(self):
        from elasticsearch import Elasticsearch
        es = Elasticsearch(settings.ELASTICSEARCH_DSL['default']['hosts'])
        es.indices.delete(index='blog', ignore=[400, 404])

    def convert_to_doc(self, articles):
        return [
            ArticleDocument(
                meta={'id': article.id},
                body=article.body,
                title=article.title,
                author={'nikename': article.author.username, 'id': article.author.id},
                category={'name': article.category.name, 'id': article.category.id},
                tags=[{'name': t.name, 'id': t.id} for t in article.tags.all()],
                pub_time=article.pub_time,
                status=article.status,
                comment_status=article.comment_status,
                type=article.type,
                views=article.views,
                article_order=article.article_order) for article in articles]

    def rebuild(self, articles=None):
        ArticleDocument.init()
        articles = articles if articles else Article.objects.all()
        docs = self.convert_to_doc(articles)
        for doc in docs:
            doc.save()

    def update_docs(self, docs):
        for doc in docs:
            doc.save()
