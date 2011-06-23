from zope.publisher.browser import BrowserView


class ReferenceView(BrowserView):
    
    name = 'none'

    def __call__(self):
        return u"View %s for %s not implemented" % (self.name, self.context.__class__)


class AuthorView(ReferenceView):

    name = 'author'


class TitleView(ReferenceView):

    name = 'title'


class YearView(ReferenceView):

    name = 'year'


