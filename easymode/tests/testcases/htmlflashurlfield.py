from django.test import TestCase
from django.conf import settings

import re

from easymode.tree    import xml
from easymode.tests.models import UrlFieldTestModel
from easymode.tests.testcases import initdb

@initdb
class HtmlFlashUrlFieldTest(TestCase):
    def extraSetUp(self):
        settings.BASE_URL = '/virtuele-camping/'

        UrlFieldTestModel.objects.create( url     ='onderdeel/detail-pagina',
                                          title   ='Main Page',
                                          revision=7 )

    def test_serialization(self):
        """Test HtmlFlashUrlField serialization"""

        t = UrlFieldTestModel.objects.all()[0]

        x = xml(t)

        tm = re.search(r'<field[^>]*name="title"[^>]*>([^<]*)</field>', x)
        self.assertTrue(tm)
        self.assertEquals('Main Page', tm.group(1).strip())

        tr = re.search(r'<field[^>]*name="revision"[^>]*>([^<]*)</field>', x)
        self.assertTrue(tr)
        self.assertEquals('7', tr.group(1).strip())

        tu = re.search(r'<field[^>]*name="url"[^>]*>(.*?)</field>', x)
        self.assertTrue(tu)
        content = tu.group(1)

        hu = re.search(r'<url-html[^>]*value="([^"]*)"', content)
        self.assertTrue(hu)
        self.assertEquals( '/virtuele-camping/onderdeel/detail-pagina',
                           hu.group(1) )

        hf = re.search(r'<url-flash[^>]*value="([^"]*)"', content)
        self.assertTrue(hf)
        self.assertEquals( '/virtuele-camping/onderdeel/detail-pagina',
                           hf.group(1) )
