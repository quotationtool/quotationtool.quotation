import zope.interface
from z3c.searcher.interfaces import ISearchFilter
from z3c.searcher.criterium import TextCriterium, SearchCriterium
from z3c.searcher.criterium import factory
from z3c.searcher.filter import EmptyTerm, SearchFilter

from quotationtool.search.interfaces import ITypeExtent

from quotationtool.quotation.interfaces import _


class IQuotationSearchFilter(ISearchFilter):
    """ Search filter for quotation objects."""


class QuotationSearchFilter(SearchFilter):
    """ Quotation search filter."""

    zope.interface.implements(IQuotationSearchFilter,
                              ITypeExtent)

    def getDefaultQuery(self):
        return EmptyTerm()

    def delimit(self):
        """ See ITypeExtent"""
        crit = self.createCriterium('type-field')
        crit.value = u'quotationtool.quotation.interfaces.IQuotation'
        crit.connectorName = 'AND'
        self.addCriterium(crit)


class QuotationCriterium(TextCriterium):
    """ Full text criterium for 'quotation-fulltext' index."""

    indexOrName = 'quotation-fulltext'

    label = _('quotation-fulltext-label', u"Quotation")

quotation_factory = factory(QuotationCriterium, 'quotation-fulltext')


class AuthorCriterium(TextCriterium):
    """ Full text criterium for 'author-fulltext' index."""

    indexOrName = 'author-fulltext'

    label = _('author-fulltext-label', u"Author")

author_factory = factory(AuthorCriterium, 'author-fulltext')


class TitleCriterium(TextCriterium):
    """ Full text criterium for 'title-fulltext' index."""

    indexOrName = 'title-fulltext'

    label = _('title-fulltext-label', u"Title")

title_factory = factory(TitleCriterium, 'title-fulltext')


