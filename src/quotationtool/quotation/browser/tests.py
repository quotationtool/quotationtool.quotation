import unittest
import doctest
import zope.component
from zope.component.testing import setUp, tearDown, PlacelessSetup
from zope.site.testing import siteSetUp
from zope.app.testing.setup import placefulSetUp
from ZODB.tests.util import DB
import transaction

from zope.keyreference.testing import SimpleKeyReference

_flags = doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS


def setUpRoot(test):
    db = DB()
    conn = db.open()
    dbroot = conn.root()
    dbroot['root'] = root = siteSetUp(True)
    transaction.commit()
    test.globs['root'] = root
    
    zope.component.provideAdapter(SimpleKeyReference)


def test_suite():
    return unittest.TestSuite((
            doctest.DocFileSuite('README.txt',
                                 setUp = setUpRoot,
                                 tearDown = tearDown,
                                 optionflags=_flags),
            ))
