import unittest
import doctest
import zope.component
from zope.component.testing import setUp, tearDown, PlacelessSetup
from zope.configuration.xmlconfig import XMLConfig

import quotationtool.quotation

_flags = doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS



def setUpZCML(test):
    setUp(test)
    XMLConfig('configure.zcml', quotationtool.quotation)()


def setUpOnlySome(test):
    """ Register only some components."""
    from quotationtool.quotation.source import plainTextQuotationFactory, restQuotationFactory 
    from quotationtool.quotation.source import QuotationSourceTypesVocabulary
    from quotationtool.quotation.interfaces import IQuotationSourceFactory
    from zope.schema.interfaces import IVocabularyFactory
    import zope.component
    zope.component.provideUtility(
        plainTextQuotationFactory, IQuotationSourceFactory, 'plaintext')
    zope.component.provideUtility(
        restQuotationFactory, IQuotationSourceFactory, 'rest')
    zope.component.provideUtility(
        QuotationSourceTypesVocabulary, 
        IVocabularyFactory, 
        'quotationtool.quotation.SourceTypes')
    import zope
    import quotationtool
    XMLConfig('meta.zcml', zope.component)()
    XMLConfig('meta.zcml', zope.security)()
    XMLConfig('configure.zcml', zope.security)()
    XMLConfig('configure.zcml', zope.app.schema)()
    XMLConfig('configure.zcml', zope.component)()
    XMLConfig('configure.zcml', zope.security)()
    XMLConfig('configure.zcml', zope.site)()
    XMLConfig('configure.zcml', zope.annotation)()
    XMLConfig('configure.zcml', zope.dublincore)()
    XMLConfig('configure.zcml', quotationtool.site)()
    # subscribers
    from quotationtool.site.interfaces import INewQuotationtoolSiteEvent
    import quotationtool.relation
    zope.component.provideHandler(
        quotationtool.relation.createRelationCatalog,
        adapts=[INewQuotationtoolSiteEvent])
    zope.component.provideHandler(
        quotationtool.quotation.quotation.createRelationIndex,
        adapts=[INewQuotationtoolSiteEvent])
    # container object annotation
    from zope.annotation.interfaces import IAttributeAnnotatable


class SourceTests(PlacelessSetup, unittest.TestCase):

    def setUp(self):
        super(SourceTests, self).setUp()
        setUpZCML(self)

    def test_Types(self):
        import zope.schema
        field = zope.schema.Choice(
            title = u"source type",
            vocabulary = 'quotationtool.quotation.SourceTypes')
        self.assertTrue(field.validate(u'plaintext') is None)
        self.assertTrue(field.validate(u'rest') is None)
        self.assertRaises(zope.schema.interfaces.ConstraintNotSatisfied, 
                          field.validate, (u'fails'))
        # if there is an other type registered in the renderer
        # package that is not known here, it should fail
        from quotationtool.renderer.plaintext import plainTextFactory
        from quotationtool.renderer.interfaces import ISourceFactory
        zope.component.provideUtility(
            plainTextFactory,
            provides = ISourceFactory,
            name = 'other_text_syntax')
        self.assertRaises(zope.schema.interfaces.ConstraintNotSatisfied, 
                          field.validate, (u'other_text_syntax'))
        # but it should be OK for quotationtool.renderer.SourceTypes
        rfield = zope.schema.Choice(
            title = u"source type",
            vocabulary = 'quotationtool.renderer.SourceTypes')
        self.assertTrue(rfield.validate('other_text_syntax') is None)

    def test_PlainText(self):
        """ Test if quotationtool.renderer still works."""
        quotation = zope.component.createObject('plaintext', u"Hello World!")
        from quotationtool.renderer.plaintext import PlainText
        self.assertTrue(isinstance(quotation, PlainText))


class SiteCreationTests(PlacelessSetup, unittest.TestCase):

    def setUp(self):
        super(SiteCreationTests, self).setUp()
        setUpOnlySome(self)
        import quotationtool.site
        XMLConfig('configure.zcml', quotationtool.site)

    def test_RelationIndex(self):
        """ Test if a relation index is created on a new site event."""
        from quotationtool.site.site import QuotationtoolSite
        from zope.container.btree import BTreeContainer
        root = BTreeContainer()
        root['quotationtool'] = site = QuotationtoolSite()
        from zc.relation.interfaces import ICatalog
        cat = zope.component.getUtility(
            ICatalog, context = site)
        #self.assertTrue('ifigure-reference' in list(cat.iterSearchIndexes()))


def test_suite():
    return unittest.TestSuite((
            doctest.DocTestSuite('quotationtool.quotation.interfaces',
                                 setUp = setUpZCML,
                                 tearDown = tearDown,
                                 optionflags=_flags),
            doctest.DocTestSuite('quotationtool.quotation.quotation',
                                 setUp = setUpZCML,
                                 tearDown = tearDown,
                                 optionflags=_flags),
            doctest.DocFileSuite('README.txt',
                                 setUp = setUpOnlySome,
                                 tearDown = tearDown,
                                 optionflags=_flags),
            unittest.makeSuite(SourceTests),
            unittest.makeSuite(SiteCreationTests),
            ))
