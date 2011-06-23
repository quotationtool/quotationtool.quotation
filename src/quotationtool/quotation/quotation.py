import zope.interface
import zope.component
import zc.relation
from persistent import Persistent
from zope.schema.fieldproperty import FieldProperty
from zope.component.factory import Factory

from interfaces import IQuotation
from quotationtool.site.interfaces import INewQuotationtoolSiteEvent
from quotationtool.relation import dump, load


class Quotation(Persistent):
    """Implementation of quotation object. This is a base class for more
    specific quotation types.

        >>> from quotationtool.quotation.quotation import Quotation
        >>> simile = Quotation()


        >>> simile.reference = bad = object()
        Traceback (most recent call last):
        ...
        RelationPreconditionError

        >>> import zope.interface
        >>> from quotationtool.quotation.interfaces import IReference
        >>> class Reference(object):
        ...     pass
        >>> zope.interface.classImplements(Reference, IReference)

        >>> updikescunts = Reference()
        >>> simile.reference = updikescunts

        >>> shark = u"She feels like a shark, slimy and abrasive."
        >>> simile.quotation = shark
        >>> len(shark) == simile.length
        True

        >>> simile.position = u"23"
        >>> simile.source_type = 'plaintext'


    """
    
    zope.interface.implements(IQuotation)

    __name__ = __parent__ = None

    reference = FieldProperty(IQuotation['reference'])
    _quotation = FieldProperty(IQuotation['quotation'])
    length = FieldProperty(IQuotation['length'])
    source_type = FieldProperty(IQuotation['source_type'])
    page = FieldProperty(IQuotation['page'])
    volume = FieldProperty(IQuotation['volume'])
    position = FieldProperty(IQuotation['position'])

    def setQuotation(self, val):
        self._quotation = val
        self.length = len(val)
    def getQuotation(self):
        return self._quotation
    quotation = property(getQuotation, setQuotation)


quotation_factory = Factory(Quotation)


@zope.component.adapter(INewQuotationtoolSiteEvent)
def createRelationIndex(event):
    """ Create a new index in the relation catalog.

    This requires configure.zcml from quotationtool.relation included
    before the config of this package because of the order of the
    subscribers.
    """
    sm = event.object.getSiteManager()
    cat = zope.component.getUtility(
        zc.relation.interfaces.ICatalog,
        context = event.object)
    cat.addValueIndex(
        IQuotation['reference'],
        dump = dump, load = load,
        name = 'iquotation-reference')
        
