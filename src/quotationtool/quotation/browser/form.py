import zope.interface
import zope.component
from z3c.form import field
from z3c.formui import form
from z3c.form.interfaces import DISPLAY_MODE, HIDDEN_MODE
from zope.app.container.interfaces import INameChooser
from zope.traversing.browser.absoluteurl import absoluteURL
from zope.proxy import removeAllProxies
from zope.securitypolicy.interfaces import IPrincipalRoleManager
import zc.resourcelibrary
from zope.location.location import LocationIterator

from quotationtool.skin.interfaces import ITabbedContentLayout
from quotationtool.editorial.browser.form import Z3cFormMixin

from quotationtool.quotation.interfaces import _, IQuotation, IQuotationContainer


class AddQuotationInReferenceContext(form.AddForm):
    """A form for adding a quotation object in the context of a
    reference."""

    factory_name = 'quotationtool.quotation.Quotation'

    zope.interface.implements(ITabbedContentLayout)

    label = _('add-quotation', u"Add a new Quotation")

    info = u""
    
    fields = field.Fields(IQuotation).omit(
        '__parent__', '__name__', 'reference', 'length')#, 'source_type')

    def __init__(self, context, request):
        super(AddQuotationInReferenceContext, self).__init__(context, request)
        zc.resourcelibrary.need('quotationtool.tinymce.Quotation')

    def updateWidgets(self):
        super(AddQuotationInReferenceContext, self).updateWidgets()
        self.widgets['source_type'].value = ('html',)
        self.widgets['source_type'].mode = HIDDEN_MODE # TODO: make more secure!

    def create(self, data):
        quotation = zope.component.createObject(self.factory_name)
        form.applyChanges(self, quotation, data)
        quotation.source_type = 'html'
        
        # We want an object which is not security proxied as reference
        # attribute:
        quotation.reference = removeAllProxies(self.context)

        # Grant the current user the Edit permission by assigning him
        # the quotationtool.Creator role, but only locally in the
        # context of the newly created object.
        manager = IPrincipalRoleManager(quotation)
        manager.assignRoleToPrincipal(
            'quotationtool.Creator',
            self.request.principal.id)

        return quotation

    def add(self, quotation):
        container = zope.component.getUtility(
            IQuotationContainer, context=self.context)
        name = INameChooser(container).chooseName(quotation, None)
        self._obj = container[name] = quotation

    def nextURL(self):
        for location in LocationIterator(self._obj):
            if zope.component.interfaces.ISite.providedBy(location):
                break
        return absoluteURL(location, self.request) + u"/account/@@worklist.html"


class QuotationEditForm(Z3cFormMixin, form.EditForm):
    """A form for editing a quotation item."""

    zope.interface.implements(ITabbedContentLayout)

    info = AddQuotationInReferenceContext.info

    fields = field.Fields(IQuotation).omit(
        '__parent__', '__name__', 'reference', 'length')

    def __init__(self, context, request):
        super(QuotationEditForm, self).__init__(context, request)
        if context.source_type == 'html':
            zc.resourcelibrary.need('quotationtool.tinymce.Quotation')

    def updateWidgets(self):
        super(QuotationEditForm, self).updateWidgets()
        self.widgets['source_type'].mode = DISPLAY_MODE
