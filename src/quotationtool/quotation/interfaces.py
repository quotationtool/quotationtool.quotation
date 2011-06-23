from zope.interface import Interface, Attribute, invariant, Invalid
from zope.container.interfaces import IContained, IContainer
from zope.container.constraints import containers, contains
from zope.schema import Text, TextLine, List, Int, Choice, Object
from zope.i18nmessageid import MessageFactory

from quotationtool.relation.schema import Relation


_ = MessageFactory('quotationtool')


class IReference(Interface):
    """ A marker interface for objects one can cite from."""


class IQuotation(Interface):
    """ The interface for quotation objects defines the structure of
    its data.

        >>> from quotationtool.quotation.interfaces import IQuotation

        >>> bad = object()
        >>> IQuotation['reference'].validate(bad)
        Traceback (most recent call last):
        ...
        RelationPreconditionError

        >>> from quotationtool.quotation.interfaces import IReference
        >>> import zope.interface
        >>> class Book(object):
        ...     pass
        >>> zope.interface.classImplements(Book, IReference)

        >>> somebook = Book()
        >>> IQuotation['reference'].validate(somebook)


        >>> IQuotation['quotation'].validate(u"She feels like a shark, slimy and abrasive.")
        >>> IQuotation['position'].validate(u"42")
        >>> IQuotation['source_type'].validate('plaintext')
        >>> IQuotation['source_type'].validate(IQuotation['source_type'].default)

    """

    reference = Relation(
        title = _('iquotation-reference-title',
                  u"Cited from"),
        description = _('iquotation-reference-desc',
                        u"The publication (book, article etc.) the text is taken from"),
        required = True,
        precondition = [IReference],
        )

    quotation = Text(
        title = _('iquotation-quotation-title',
                  u"Quotation"),
        description = _('iquotation-quotation-desc',
                        u"Passage in the text; without quotationmarks."),
        required = True,
        )

    length = Int(
        title = _('iquotation-length-title',
                  u"Lenght"),
        description = _('iquotation-length-desc',
                        u"Length in bytes of the quotation attribute. Calculated automatically when quotation is set."),
        required = True,
        )

    source_type = Choice(
        title = _('iquotation-source-type-title', u"Text Format"),
        description = _('iquotation-source-type-desc',
                        u"Choose text format"),
        required = True,
        default = 'plaintext',
        vocabulary = 'quotationtool.quotation.SourceTypes',
        )

    page = TextLine(
        title = _('iquotation-page-title',
                  u"Page"),
        description = _('iquotation-page-desc',
                        u"Number of page without ''p.''."),
        required = False,
        )

    volume = TextLine(
        title = _('iquotation-volume-title',
                  u"Volume"),
        description = _('iquotation-volume-desc',
                        u"Number of Volume without ''vol.''."),
        required = False,
        )

    position = TextLine(
        title = _('iquotation-position-title',
                  u"Position within Division/Disposition"),
        description = _('iquotation-position-desc',
                        u"If no page is available one might relocate the quotation by chapter or paragraph. Use this field to help others finding the quotation."),
        required = False,
        )
    
    @invariant
    def assertPageOrPosition(obj):
        if not (getattr(obj, 'page', u"") or getattr(obj, 'position', u"")):
            raise Invalid(_('neitherPageNorPosition',
                            u"Either page or position must be given."))


class IQuotationSourceFactory(Interface):
    """A source format for a quotation text (attribute 'quotation' of
    ISimpleComment objects)."""


class IQuotationContainer(Interface):
    """ A container for quotations."""

    _count = Int(
        title = _('iquotationcontainer-count-title',
                  u"Count"),
        description = _('iquotationcontainer-count-desc',
                        u"How many examples there are"),
        required = True,
        default = 0,
        )


class IQuotationContainerContainer(IContainer):
    """ The container part of the IQuotationContainer interface."""

