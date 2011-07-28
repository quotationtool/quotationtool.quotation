import zope.interface
import zope.component
from z3c.indexer.interfaces import IIndex, IValueIndexer
from z3c.indexer.indexer import MultiIndexer, ValueIndexer
from z3c.indexer.index import TextIndex, FieldIndex

from quotationtool.site.interfaces import INewQuotationtoolSiteEvent

from quotationtool.quotation.interfaces import IQuotation


class QuotationIndexer(MultiIndexer):
    
    zope.component.adapts(IQuotation)

    def doIndex(self):

        quotation_fulltext = self.getIndex('quotation-fulltext')
        quotation_fulltext.doIndex(
            self.oid, getattr(self.context, 'quotation', u""))

        quotation_field = self.getIndex('quotation-field')
        quotation_field.doIndex(
            self.oid, getattr(self.context, 'quotation', u""))

        page_field = self.getIndex('page-field')
        page_field.doIndex(
            self.oid, getattr(self.context, 'page', u""))

    def doUnIndex(self):

        quotation_fulltext = self.getIndex('quotation-fulltext')
        quotation_fulltext.doUnIndex(self.oid)

        quotation_field = self.getIndex('quotation-field')
        quotation_field.doUnIndex(self.oid)

        page_field = self.getIndex('page-field')
        page_field.doUnIndex(self.oid)


class AnyValueIndexer(ValueIndexer):

    indexName = 'any-fulltext'

    zope.component.adapts(IQuotation)
    
    @property
    def value(self):
        rc =  getattr(self.context, 'quotation', u"")
        rc += u" " + getattr(self.context, 'page', u"")
        rc += u" " + getattr(self.context, 'volume', u"")
        rc += u" " + getattr(self.context, 'position', u"")
        reference_indexer = zope.component.queryAdapter(
            self.context.reference,
            IValueIndexer, name='any-fulltext')
        if reference_indexer is not None:
            rc += u" " + reference_indexer.value
        return rc


class IdValueIndexer(ValueIndexer):

    indexName = 'id-field'

    zope.component.adapts(IQuotation)

    @property
    def value(self):
        return self.context.__name__


class ReferenceIndexerBase(ValueIndexer):
    """ A base class for indexer that call indexers on the reference
    attribute."""

    zope.component.adapts(IQuotation)

    indexName = None
    
    @property
    def value(self):
        adapter = zope.component.getAdapter(
            self.context.reference,
            interface=IValueIndexer, name=self.indexName)
        #raise Exception(adapter.value)
        return adapter.value


class AuthorTextIndexer(ReferenceIndexerBase):

    indexName = 'author-fulltext'


class AuthorFieldIndexer(ReferenceIndexerBase):

    indexName = 'author-field'


class TitleTextIndexer(ReferenceIndexerBase):

    indexName = 'title-fulltext'


class TitleFieldIndexer(ReferenceIndexerBase):

    indexName = 'title-field'


class YearSetIndexer(ReferenceIndexerBase):

    indexName = 'year-set'


class OrigYearSetIndexer(ReferenceIndexerBase):

    indexName = 'origyear-set'


def createQuotationIndices(site):
    """ Create indexes for quotation objects."""

    sm = site.getSiteManager()
    default = sm['default']

    quotation_fulltext = default['quotation-fulltext'] = TextIndex()
    sm.registerUtility(quotation_fulltext, IIndex, name='quotation-fulltext')

    quotation_field = default['quotation-field'] = FieldIndex()
    sm.registerUtility(quotation_field, IIndex, name='quotation-field')

    page_field = default['page-field'] = FieldIndex()
    sm.registerUtility(page_field, IIndex, name='page-field')


@zope.component.adapter(INewQuotationtoolSiteEvent)
def createQuotationIndicesSubscriber(event):
    """Create quotation indices when a new quotationtool site is
    created.
    """

    createQuotationIndices(event.object)
