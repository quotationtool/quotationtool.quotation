import zope.interface
import zope.component
from zope.publisher.browser import BrowserView
from zope.proxy import removeAllProxies
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile

from quotationtool.renderer.interfaces import IHTMLRenderer 

from quotationtool.quotation.interfaces import _


class RenderQuotation(object):
    """A mixin class that provides a method for rendering the
    quotation text."""

    limit = None
    
    def renderQuotation(self):
        source = zope.component.createObject(
            self.context.source_type,
            self.context.quotation)
        renderer = zope.component.getMultiAdapter(
            (removeAllProxies(source), self.request),
            IHTMLRenderer, name = u'')
        return renderer.render(limit = self.limit)


class DetailsView(BrowserView, RenderQuotation):
    """The @@details view which can be called from within a zpt.
    """

    template = ViewPageTemplateFile('details.pt')

    def __call__(self):
        return self.template()


class ListView(BrowserView, RenderQuotation):
    """The @@list view which can be called from within a zpt."""

    limit = 200

    template = ViewPageTemplateFile('list.pt')

    def __call__(self):
        return self.template()


class QuotationLabelView(BrowserView):
    """A view that informs about the object type."""

    def __call__(self):
        return _('quotation-labelview', u"Quotation #$ID", 
                 mapping = {'ID': self.context.__name__})


class QuotationContainerLabelView(BrowserView):
    """A view that informs about the object type."""

    def __call__(self):
        return _('quotationcontainer-labelview', u"Quotations")


