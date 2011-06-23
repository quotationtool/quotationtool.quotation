import transaction

import zope.component
from zope.app.appsetup.bootstrap import ensureUtility, getInformationFromEvent

from zope.intid.interfaces import IIntIds
from zope.intid import IntIds


def bootStrapSubscriber(event):
    """ Subscriber to the IDatabaseOpenedWithRoot event. Create a global
    intid utility if there is not yet one.

    The intid utility is needed for indexing entries in the
    bibliography catalog."""

    db, connection, root, root_folder = getInformationFromEvent(event)
    
    ensureUtility(
        root_folder,
        IIntIds, '',
        IntIds,
        )

    #ut = zope.component.queryUtility(
    #    IIntIds, default = None)
    #assert(ut is not None)

    transaction.commit()
    connection.close()
