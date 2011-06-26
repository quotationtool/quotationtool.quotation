Browser Components
------------------

The browser package's zcml is not included automatically by the
quotationtool.quotation package's zcml.

    >>> from zope.configuration.xmlconfig import XMLConfig
    >>> import quotationtool.quotation
    >>> XMLConfig('configure.zcml', quotationtool.quotation)()
    >>> XMLConfig('configure.zcml', quotationtool.quotation.browser)()

First we need a references which we want to cite our quotations from.

    >>> import zope.interface
    >>> import zope.component
    >>> from quotationtool.quotation.interfaces import IReference

    >>> class IBook(zope.interface.Interface):
    ...     author = zope.interface.Attribute("author")
    ...     title = zope.interface.Attribute("title")
    ...     year = zope.interface.Attribute("year")
    >>> from zope.location.interfaces import ILocation
    >>> class Book(object):
    ...     zope.interface.implements(IBook, ILocation)
    ...	    __name__ = __parent__ = None

Our book class also has to implement IReference. Normally one would do
this in ZCML.

    >>> zope.interface.classImplements(Book, IReference)

    >>> root['samplebook'] = samplebook = Book()
    >>> samplebook.author = u"Updike, John"
    >>> samplebook.title = u"Cunts"
    >>> samplebook.year = 1974

We also need a container for quotations.

    >>> from quotationtool.quotation.quotationcontainer import QuotationContainer
    >>> root['quotations'] = quotations = QuotationContainer()
    >>> from quotationtool.quotation.interfaces import IQuotationContainer
    >>> zope.component.provideUtility(quotations, IQuotationContainer)


Forms
-----

Add Form
~~~~~~~~

Now we can use the add form. This form takes as context the reference the
quotation is taken from.

    >>> from quotationtool.quotation.browser.testing import TestRequest
    >>> from quotationtool.quotation.browser.form import AddQuotationInReferenceContext

    >>> addform = AddQuotationInReferenceContext(samplebook, TestRequest())
    >>> addform.update()
    >>> isinstance(addform.render(), unicode)
    True

    >>> addform = AddQuotationInReferenceContext(samplebook, TestRequest(form={
    ...     'form.widgets.quotation': u"She feels slimy and abrasive.",
    ...	    'form.widgets.source_type': u"html",
    ...	    'form.buttons.add': u"Add",}))
    >>> addform.update()
    >>> addform.status
    u'There were some errors.'

    >>> addform = AddQuotationInReferenceContext(samplebook, TestRequest(form={
    ...     'form.widgets.quotation': u"She feels slimy and abrasive.",
    ...	    'form.widgets.page': u"???",
    ...	    'form.widgets.source_type': u"html",
    ...	    'form.buttons.add': u"Add",}))
    >>> addform.update()
    >>> addform.status
    ''

Now we have a quotation in the quotations container:

    >>> len(quotations)
    1

    >>> list(quotations.keys())
    [u'1']

The name was choosen by the namechooser in this package.

Edit Form
~~~~~~~~~

There is also an edit form:

    >>> from quotationtool.quotation.browser.form import QuotationEditForm
    >>> she = quotations.values()[0]
    >>> editform = QuotationEditForm(she, TestRequest(form={
    ...    'form.widgets.quotation': u"She feels slimy and abrasive.",
    ...    'form.widgets.page': u"5",
    ...    'form.widgets.source_type': u"html",
    ...    'form.buttons.apply': u"Apply",}))
    >>> editform.update()

    >>> editform.status
    u'Data successfully updated.'

    >>> she.page
    u'5'


Tables
------

There is a table for the quotations in the container:

    >>> from quotationtool.quotation.browser.table import QuotationContainerTable
    >>> request = TestRequest()
    >>> request.principal = None
    >>> table = QuotationContainerTable(quotations, request)
    >>> table.update()
    Traceback (most recent call last):
    ...
    ComponentLookupError: (<Book object at 0x...>, <InterfaceClass z3c.indexer.interfaces.IIndexer>, 'year-field')

For the table to work we need indexer adapters named 'year-field',
'author-field' and 'title-field' for our book class. (The suffix
'-field' says that they are field indices, not text indices or value
indices.)

    >>> from z3c.indexer.indexer import ValueIndexer

    >>> class YearIndexer(ValueIndexer):
    ...	    zope.component.adapts(IBook)
    ...	    def value(self): return self.context.year
    ...
    >>> class AuthorIndexer(ValueIndexer):
    ...	    zope.component.adapts(IBook)
    ...	    def value(self): return self.context.author
    ...
    >>> class TitleIndexer(ValueIndexer):
    ...	    zope.component.adapts(IBook)
    ...	    def value(self): return self.context.title
    ...
    >>> zope.component.provideAdapter(YearIndexer, name='year-field')
    >>> zope.component.provideAdapter(AuthorIndexer, name='author-field')
    >>> zope.component.provideAdapter(TitleIndexer, name='title-field')

    >>> from zope.security.management import newInteraction
    >>> newInteraction()

    >>> table.update()
    >>> table.render()
    Traceback (most recent call last):
    ...
    ComponentLookupError: ((<Book object at 0x...>, <quotationtool.quotation.browser.testing.TestRequest instance URL=http://127.0.0.1>), <InterfaceClass zope.interface.Interface>, 'year')

So we also have to register views called 'year', 'author' and 'title'
for objects of the book class.

    >>> from zope.publisher.browser import BrowserView
    >>> from zope.publisher.interfaces.browser import IBrowserView
    >>> from quotationtool.skin.interfaces import IQuotationtoolBrowserLayer
    >>> class ViewBase(object):
    ...     zope.interface.implements(IBrowserView)
    ...     zope.component.adapts(IBook, IQuotationtoolBrowserLayer)
    ...     attr_name = None
    ...	    def __init__(self, context, request):
    ...	        self.context = context
    ...	        self.request = request
    ...     def __call__(self): 
    ...	        return getattr(self.context, self.attr_name, u"")
    >>> class YearView(ViewBase):
    ...     attr_name = 'year'
    >>> class AuthorView(ViewBase):
    ...     attr_name = 'author'
    >>> class TitleView(ViewBase):
    ...     attr_name = 'title'
    >>> zope.component.provideAdapter(YearView, name='year')
    >>> zope.component.provideAdapter(AuthorView, name='author')
    >>> zope.component.provideAdapter(TitleView, name='title')

    >>> table.render()
    u'...<td>1974</td>...<td>Updike, John</td>...<td>Cunts</td>...'

To see a reference's quotations we need something to track 1/n
relations. We do this by using a relation catalog. (Note: The relation
catalog is based on integer ids. An intids utility is set up in test
setup.)

    >>> from zc.relation.catalog import Catalog
    >>> from zc.relation.interfaces import ICatalog
    >>> from quotationtool.relation import dump, load
    >>> import quotationtool.relation
    >>> relations = Catalog(dump, load)
    >>> zope.component.provideUtility(relations, ICatalog)
    >>> from quotationtool.quotation.interfaces import IQuotation
    >>> relations.addValueIndex(
    ...     IQuotation['reference'],
    ...     dump = dump, load = load,
    ...     name = 'iquotation-reference')
    >>> relations.index(she)
    
There is also a table that lists the quotations in a reference:

    >>> from quotationtool.quotation.browser.table import QuotationsInReferenceTable
    >>> table = QuotationsInReferenceTable(samplebook, TestRequest())
    >>> table.update()
    >>> table.render()
    u'...<div>She feels slimy and abrasive.</div>...'
    
Flags
-----

Flags are viewlets:

>>> from quotationtool.quotation.browser.flags import SchemaErrorFlag
>>> flag = SchemaErrorFlag(she, TestRequest(), None, None)
>>> flag.update()
>>> flag.render()
u''

>>> from quotationtool.quotation.browser.flags import QuotationCountFlag
>>> flag = QuotationCountFlag(samplebook, TestRequest(), None, None)
>>> flag.update()
>>> flag.render()
u'<span class="quotationcount">\n  <abbr title="Number of Quotations">Ex</abbr>:1\n</span>\n'


Views
-----

>>> from quotationtool.quotation.browser import view
>>> view.QuotationLabelView(she, TestRequest())()
u'quotation-labelview'

>>> view.QuotationContainerLabelView(quotations, TestRequest())()
u'quotationcontainer-labelview'

For the details and list view we need a view called 'citation' for our
book objects.

>>> class BookCitation(object):
...     zope.interface.implements(IBrowserView)
...     zope.component.adapts(IBook, IQuotationtoolBrowserLayer)
...     def __init__(self, context, request):
...         self.context = context
...	    self.request = request
...     def __call__(self):
...         return self.context.author + u': ' + self.context.title + u', ' + unicode(self.context.year)
>>> zope.component.provideAdapter(BookCitation, name='citation')

>>> view.DetailsView(she, TestRequest())()
u'...href="http://127.0.0.1/samplebook/@@quotations.html">Updike, John: Cunts, 1974</a>...'

>>> view.ListView(she, TestRequest())()
u'...href="http://127.0.0.1/samplebook/@@quotations.html">Updike, John: Cunts, 1974</a>...'
