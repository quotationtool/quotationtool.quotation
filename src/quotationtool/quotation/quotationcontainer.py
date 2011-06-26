import zope.interface
import zope.component
from zope.container.btree import BTreeContainer
from zope.schema.fieldproperty import FieldProperty
from zope.container.contained import NameChooser
from zope.exceptions.interfaces import UserError
from zope.dublincore.interfaces import IWriteZopeDublinCore

from quotationtool.site.interfaces import INewQuotationtoolSiteEvent

from quotationtool.quotation.interfaces import _, IQuotationContainer, IQuotationContainerContainer


class QuotationContainer(BTreeContainer):
    """ An implementation of a container for quotation objects."""

    zope.interface.implements(IQuotationContainer,
                              IQuotationContainerContainer)
    
    __name__ = __parent__ = None

    _count = FieldProperty(IQuotationContainer['_count'])

    def __setitem__(self, key, val):
        super(QuotationContainer, self).__setitem__(key, val)
        self._count += 1


class QuotationNameChooser(NameChooser):
    """ A name chooser for quotation objects in the container context."""
    
    def chooseName(self, name, obj):
        self.checkName(unicode(self.context._count + 1), obj)
        return unicode(self.context._count + 1)


@zope.component.adapter(INewQuotationtoolSiteEvent)
def createQuotationContainer(event):
    sm = event.object.getSiteManager()
    container = event.object['quotations'] = QuotationContainer()
    sm.registerUtility(container, IQuotationContainer)

    IWriteZopeDublinCore(container).title = u"Quotations"

    IWriteZopeDublinCore(container).description = u"""A collection of quotations."""
