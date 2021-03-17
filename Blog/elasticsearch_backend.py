# -*- encoding: utf-8 -*-
import logging

from django.db.models import Q
from django.utils.encoding import force_text
from haystack.backends import BaseSearchBackend, log_query, BaseSearchQuery, BaseEngine
from haystack.models import SearchResult

from blog.documents import ArticleDocumentManager, ArticleDocument
from blog.models import Article

logger = logging.getLogger(__name__)


class ElasticSearchBackend(BaseSearchBackend):
    """es search engine backend"""

    def __init__(self, connection_alias, **connection_options):
        super(ElasticSearchBackend, self).__init__(connection_alias, **connection_options)
        self.manager = ArticleDocumentManager()
        # try:
        #     self._rebuild(None)
        # except:
        #     pass

    def _get_models(self, iterable):
        """"""
        models = iterable if iterable else Article.objects.all()
        docs = self.manager.convert_to_doc(models)
        return docs

    def _create(self, models):
        """新建"""
        self.manager.create_index()
        docs = self._get_models(models)
        self.manager.rebuild(docs)

    def _delete(self, models):
        """删除"""
        for m in models:
            m.delete()
        return True

    def _rebuild(self, models):
        """重构"""
        models = models if models else Article.objects.all()
        docs = self.manager.convert_to_doc(models)
        self.manager.update_docs(docs)

    def update(self, index, iterable, commit=True):
        """更新"""
        models = self._get_models(iterable)
        self.manager.update_docs(models)

    def remove(self, obj_or_string):
        """"""
        models = self._get_models([obj_or_string])
        self._delete(models)

    def clear(self, models=None, commit=True):
        """"""
        self.remove(None)

    @log_query
    def search(self, query_string, **kwargs):
        """"""
        logger.info('search query_string:' + query_string)
        start_offset = kwargs.get('start_offset')
        end_offset = kwargs.get('end_offset')
        q = Q('bool', should=[Q('match', body=query_string), Q('match', title=query_string)], minmum_should_match="70%")
        search = ArticleDocument.search().query('bool', filter=[q]).filter('term', status='p').filter('term',
                                                                                                      type='a').source(
            False)[start_offset:  end_offset]

        results = search.execute()
        hits = results['hits'].total
        raw_results = []
        for raw_result in results['hits']['hits']:
            app_label = 'blog'
            model_name = 'Article'
            additional_fields = {}

            result_class = SearchResult

            result = result_class(app_label, model_name, raw_result['_id'], raw_result['_score'], **additional_fields)
            raw_results.append(result)
        facets = {}
        spelling_suggestion = None
        data = {
            'results': raw_results,
            'hits': hits,
            'facets': facets,
            'spelling_suggestion': spelling_suggestion
        }
        return data


class ElasticSearchQuery(BaseSearchQuery):
    def _convert_datetime(self, date):
        if hasattr(date, 'hour'):
            return force_text(date.strftime('%Y%m%d%H%M%S'))
        else:
            return force_text(date.strftime('%Y%m%d000000'))

    def clean(self, query_fragment):
        words = query_fragment.split()
        cleaned_words = []
        for word in words:
            if word in self.backend.RESERVED_WORDS:
                word = word.replace(word, word.lower())
            for char in self.backend.RESERVED_CHARACTERS:
                if char in word:
                    word = "'%s" % word
                    break

            cleaned_words.append(word)
        return ''.join(cleaned_words)

    def build_query_fragment(self, field, filter_type, value):
        return value.query_string

    def get_count(self):
        results = self.get_results()
        return len(results) if results else 0


class ElasticSearchEngine(BaseEngine):
    backend = ElasticSearchBackend
    query = ElasticSearchQuery
