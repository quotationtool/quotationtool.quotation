import zope.interface
import zope.component
from z3c.searcher.interfaces import ISearchFilter, CONNECTOR_OR, CONNECTOR_AND
from z3c.searcher.criterium import TextCriterium, SearchCriterium
from z3c.searcher.criterium import factory
from z3c.searcher.filter import EmptyTerm, SearchFilter
from zope.traversing.browser import absoluteURL

from quotationtool.search.interfaces import IQuotationtoolSearchFilter
from quotationtool.search.interfaces import ITypeExtent, ICriteriaChainSpecifier, IResultSpecifier
from quotationtool.search.interfaces import ICriteriumDescription

from quotationtool.quotation.interfaces import _, IQuotationSearchFilter, IQuotationContainer


class QuotationSearchFilter(SearchFilter):
    """ Quotation search filter."""

    zope.interface.implements(IQuotationSearchFilter,
                              ITypeExtent,
                              ICriteriaChainSpecifier,
                              IResultSpecifier)

    def getDefaultQuery(self):
        return EmptyTerm()

    def delimit(self):
        """ See ITypeExtent"""
        crit = self.createCriterium('type-field')
        crit.value = u'quotationtool.quotation.interfaces.IQuotation'
        crit.connectorName = CONNECTOR_AND
        self.addCriterium(crit)

    first_criterium_connector_name = CONNECTOR_OR

    ignore_empty_criteria = True

    def resultURL(self, context, request):
        quotations = zope.component.getUtility(
            IQuotationContainer,
            context=context)
        return absoluteURL(quotations, request) + u"/@@searchResult.html"

    session_name = 'quotations'


quotation_search_filter_factory = zope.component.factory.Factory(
    QuotationSearchFilter,
    _('QuotationSearchFilter-title', u"Quotations"),
    _('QuotationSearchFilter-desc', u"Search for quotations.")
    )


class QuotationCriterium(TextCriterium):
    """ Full text criterium for 'quotation-fulltext' index."""

    zope.interface.implements(ICriteriumDescription)

    indexOrName = 'quotation-fulltext'

    label = _('quotation-fulltext-label', u"Quotation")

    description = _('quotation-fulltext-desc', u"Matches in quotation field.")

    ui_weight = 90

quotation_factory = factory(QuotationCriterium, 'quotation-fulltext')


class AuthorCriterium(TextCriterium):
    """ Full text criterium for 'author-fulltext' index."""

    zope.interface.implements(ICriteriumDescription)

    indexOrName = 'author-fulltext'

    label = _('author-fulltext-label', u"Author")

    description = _('author-fulltext-desc', u"Matches author or editor.")

    ui_weight = 110

author_factory = factory(AuthorCriterium, 'author-fulltext')


class TitleCriterium(TextCriterium):
    """ Full text criterium for 'title-fulltext' index."""

    zope.interface.implements(ICriteriumDescription)

    indexOrName = 'title-fulltext'

    label = _('title-fulltext-label', u"Title")

    description = _('title-fulltext-desc', u"Matches title, original title, subtitle and the like.")

    ui_weight = 120

title_factory = factory(TitleCriterium, 'title-fulltext')
