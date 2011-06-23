import zope.interface
import zope.component
from zope.component.factory import Factory
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from zope.schema.interfaces import IVocabularyFactory

from quotationtool.renderer import plaintext, rest, html
from interfaces import  IQuotationSourceFactory


htmlQuotationFactory = Factory(
    html.HTMLSource,
    html.htmlSourceFactory.title,
    html.htmlSourceFactory.description
    )


plainTextQuotationFactory = Factory(
    plaintext.PlainText,
    plaintext.plainTextFactory.title,
    plaintext.plainTextFactory.description
    )


restQuotationFactory = Factory(
    rest.ReST,
    rest.restFactory.title,
    rest.restFactory.description,
    )


def QuotationSourceTypesVocabulary(context):
    """ A factory for a vocululary of quotation source types.
    """
    terms = []
    for name, factory in zope.component.getUtilitiesFor(IQuotationSourceFactory):
        terms.append(SimpleTerm(name, title = factory.title))
    return SimpleVocabulary(terms)

zope.interface.alsoProvides(QuotationSourceTypesVocabulary, IVocabularyFactory)
