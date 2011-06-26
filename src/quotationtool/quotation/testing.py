import zope.interface
from zope.location.interfaces import ILocation
from persistent import Persistent


class IBook(zope.interface.Interface):
    author = zope.interface.Attribute("author")
    title = zope.interface.Attribute("title")
    year = zope.interface.Attribute("year")


class Book(Persistent):
    zope.interface.implements(IBook, ILocation)
    __name__ = __parent__ = None
    author = title = year = None
