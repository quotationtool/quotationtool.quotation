import zope.interface
import zope.component
from z3c.table import table, column, value, header
from z3c.table.interfaces import ITable, IColumn
from z3c.pagelet.browser import BrowserPagelet
from zope.contentprovider.interfaces import IContentProvider
from zope.publisher.interfaces.browser import IBrowserRequest
from z3c.indexer.search import ResultSet
from z3c.indexer.interfaces import IIndexer
import zc.relation
from zope.intid.interfaces import IIntIds
from zope.proxy import removeAllProxies
import urllib

from quotationtool.skin.interfaces import ITabbedContentLayout
from quotationtool.renderer.interfaces import IHTMLRenderer

from quotationtool.quotation.interfaces import _, IQuotation, IReference


class IQuotationsTable(ITable):
    """ A table for quotation objects."""


class IAuthorTitleQuotationsTable(ITable):
    """ A table for quotation objects with columns for author and
    title."""


class IQuotationsInReferenceTable(ITable):
    """ A table of quotation objects all taken from the same reference
    (or somehow else it is clear who the author, title etc. is). """


class ISortingColumn(IColumn):
    """ A column that offers sorting."""


class QuotationContainerTable(table.Table, BrowserPagelet):
    """ A table with all quotations in the quotation container."""

    zope.interface.implements(IQuotationsTable, 
                              IAuthorTitleQuotationsTable)

    render = BrowserPagelet.render

    cssClasses = {
        'table': u'container-listing',
        'thead': u'head',
        }

    cssClassEven = u'even'
    cssClassOdd = u'odd'


class QuotationsInReferenceTable(table.SequenceTable, BrowserPagelet):
    """ A table with all quotations from a certain reference."""

    zope.interface.implements(IQuotationsTable,
                              IQuotationsInReferenceTable, 
                              ITabbedContentLayout)

    render = BrowserPagelet.render

    cssClasses = {
        'table': u'container-listing',
        'thead': u'head',
        }

    cssClassEven = u'even'
    cssClassOdd = u'odd'


class QuotationsInReference(value.ValuesMixin):
    """ Values (quotations) from a reference."""

    zope.component.adapts(IReference,
                          IBrowserRequest, 
                          IQuotationsInReferenceTable)

    @property
    def values(self):
        """ We use ResultSet from the z3c.indexer package because it
        is slicable and fast."""
        intids = zope.component.getUtility(
            IIntIds,
            context=self.context)
        cat = zope.component.getUtility(
            zc.relation.interfaces.ICatalog,
            context=self.context)
        quotations = cat.findRelationTokens(
            cat.tokenizeQuery({'iquotation-reference': self.context}))
        return ResultSet(quotations, intids)


class YearColumn(column.Column):
    """ The publication year of the reference from which the quotation
    is cited."""

    zope.interface.implements(ISortingColumn)

    header = _('year-column-head', u"Year") 
    weight = 105

    def renderCell(self, item):
        view = zope.component.getMultiAdapter(
            (item.reference, self.request),
            name='year')
        return view()

    def getSortKey(self, item):
        indexer = zope.component.getAdapter(item.reference, IIndexer, name='year')
        return indexer.value


class AuthorColumn(column.Column):
    """ The author of the reference from which the quotation is
    cited."""

    zope.interface.implements(ISortingColumn)

    header = _('author-column-header', u"Author")
    weight = 110

    def renderCell(self, item):
        view = zope.component.getMultiAdapter(
            (item.reference, self.request),
            name='author')
        return view()

    def getSortKey(self, item):
        indexer = zope.component.getAdapter(item.reference, IIndexer, name='author')
        return indexer.value


class TitleColumn(column.Column):
    """ The title of the reference from which the quotation was
    cited."""

    zope.interface.implements(ISortingColumn)

    header = _('title-column-header', u"Title")
    weight = 120

    def renderCell(self, item):
        view = zope.component.getMultiAdapter(
            (item.reference, self.request),
            name='title')
        return view()

    def getSortKey(self, item):
        indexer = zope.component.getAdapter(item.reference, IIndexer, name='title')
        return indexer.value


class PageColumn(column.GetAttrColumn):
    """ The position of the quotation in the reference."""

    zope.interface.implements(ISortingColumn)

    header = IQuotation['page'].title
    weight = 5
    attrName = 'page'

    def getSortKey(self, item):
        s = getattr(item, 'page', u"")
        try:
            i = int(s)
        except ValueError:
            i = s
        return i


class QuotationColumn(column.LinkColumn):
    """ The quotation."""

    header = IQuotation['quotation'].title
    weight = 210

    def getLinkContent(self, item):
        source = zope.component.createObject(
            item.source_type,
            item.quotation)
        renderer = zope.component.getMultiAdapter(
            (removeAllProxies(source), self.request),
            IHTMLRenderer, name = u'')
        return renderer.render(limit=200)

    def getSortKey(self, item):
        return self.renderCell(item)


class FlagsColumn(column.Column):
    """ The flags of a quotation."""

    header = _(u"flags")
    weight = 99999
    
    def renderCell(self, item):
        flags = zope.component.getMultiAdapter(
            (item, self.request, self.table),
            IContentProvider, name='flags')
        flags.update()
        return flags.render()
