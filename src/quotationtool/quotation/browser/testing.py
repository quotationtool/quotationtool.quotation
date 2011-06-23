import zope.publisher
import z3c.form
from zope.security.testing import Principal

from quotationtool.skin.interfaces import IQuotationtoolBrowserLayer


class TestRequest(zope.publisher.browser.TestRequest):
    zope.interface.implements(
        z3c.form.interfaces.IFormLayer,
        IQuotationtoolBrowserLayer,
        )

    principal = Principal('testing')
