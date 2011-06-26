Let's set things up first.

    >>> from zope.configuration.xmlconfig import XMLConfig
    >>> import quotationtool.quotation
    >>> XMLConfig('configure.zcml', quotationtool.quotation)()

Quotation
---------

This package defines a Quotation class may be used to store
quotations.

    >>> from quotationtool.quotation.quotation import Quotation
    >>> quote = Quotation()

The reference attribute links the quotation to a reference, i.e. an
object from which it was cited. The value of the attribute must be an
object that implements the IReference interface. IReference does not
define a specific data structure but is a marker interface. That means
that it may be used for a variaty of object class, that may be marked
to be valid references of quotations.

    >>> bad = object()
    >>> quote.reference = bad
    Traceback (most recent call last):
    ...
    RelationPreconditionError

So lets define a book class for example. And then let's mark it to be
a valid reference. Here we use a sample class called Book

    >>> from quotationtool.quotation.testing import Book, IBook

And now we slam the IReference marker interface on it. Note: This may be
done in ZCML or somewhere else where you wire up your components.

    >>> from quotationtool.quotation.interfaces import IReference
    >>> import zope.interface
    >>> zope.interface.classImplements(Book, IReference)

    >>> samplebook = Book()
    >>> quote.reference = samplebook

Yust to make things complete:

    >>> samplebook.author = u"Hebel, J.P."
    >>> samplebook.title = u"Aus dem Schatzkaestlein ..."
    >>> samplebook.year = 1811


Quotation objects also have a quotation attribute:

    >>> quote.quotation = u"Der Zundelheiner und der Zundelfrieder trieben"
    >>> quote.length
    46

For performance reasons there is a length attribute, that stores the
length on writes of the quotation attribute.

The source_type attribute knows which kind of syntax is used for the
quotation.

    >>> quote.source_type = 'bad'
    Traceback (most recent call last):
    ...
    ConstraintNotSatisfied: bad

    >>> quote.source_type = 'plaintext'

Knowing the source type we can make a source from the quotation and
render it.

    >>> import zope.component
    >>> source = zope.component.createObject(quote.source_type, quote.quotation)
    >>> source.__class__
    <class 'quotationtool.renderer.plaintext.PlainText'>
    >>> from quotationtool.renderer.interfaces import IHTMLRenderer
    >>> from zope.publisher.browser import TestRequest
    >>> renderer = IHTMLRenderer(source, TestRequest())
    >>> renderer.render(limit=5)
    u'Der Z...'

There are also attributes named 'page', 'volume' and 'position'. They
are used for relocating the quotation within the reference. Either
'page' or 'position' must be present. Both may be present at the same
time. See interfaces.py for perpose.

    >>> from quotationtool.quotation.interfaces import IQuotation
    >>> from zope.schema import getValidationErrors
    >>> getValidationErrors(IQuotation, quote)
    [(None, Invalid(u'neitherPageNorPosition',))]

    >>> quote.page = u"24"
    >>> getValidationErrors(IQuotation, quote)
    []    

    >>> quote.position = u"Die drei Diebe"
    >>> getValidationErrors(IQuotation, quote)
    []    


Quotation Container
-------------------

    >>> from quotationtool.quotation.quotationcontainer import QuotationContainer
    >>> quotations = QuotationContainer()
    >>> quotations[u'1'] = quote

It is better to let an automatic namechooser choose the name for a new
quotation. The default namechooser will simply count the child objects
of the container. The namechooser has a chooseName method that takes
two arguments. See the INameChooser interface for details.

    >>> quote2 = Quotation()
    >>> quote2.reference = samplebook
    >>> quote2.quotation = u"wieder aus dem Turm kamen"
    >>> quote2.source_type = 'plaintext'
    >>> quote2.page = u"27"

    >>> from zope.container.interfaces import INameChooser
    >>> names = INameChooser(quotations)
    >>> name = names.chooseName(None, quote2)
    >>> name
    u'2'

    >>> quotations[name] = quote2

The namechooser may be used for checking names, too:

    >>> names.checkName(u'1', object())
    Traceback (most recent call last):
    ...
    KeyError: u'The given name is already being used'

    >>> names.checkName(u'3', object())
    True


Indexing/Searching
------------------

