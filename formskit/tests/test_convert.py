from formskit.tests.base import FormskitTestCase
from formskit.field import Field
from formskit.field_convert import FakeConvert, ToInt


class TestFakeConvert(FormskitTestCase):

    def setUp(self):
        super().setUp()
        self.field = Field('name1')

    def test_convert(self):
        self.field.set_values(['data'])
        assert self.field.get_value() == 'data'


class TestToInt(FormskitTestCase):

    def setUp(self):
        super().setUp()
        self.field = Field('name1', convert=ToInt())

    def test_convert(self):
        self.field.set_values(['12'])
        assert self.field.get_value() == 12
