from json import loads
from base64 import urlsafe_b64decode
from pytest import raises

from formskit.tests.base import FormskitTestCase
from formskit import Field
from formskit.validators import NotEmpty, IsDigit
from formskit.form import Form
from formskit.field import FieldValue


class FieldTest(FormskitTestCase):

    def test_init_form(self):
        form = 123
        field = Field(None, None, None)
        field.init_form(form)

        self.assertEqual(form, field.form)

    def test_validate(self):
        not_empty = NotEmpty()
        field = Field('name', [not_empty])

        self.assertEqual(False, field.validate())
        self.assertEqual(field, not_empty.field)

        field.reset()
        field.set_values(['green'])

        self.assertEqual(True, field.validate())

    def test_two_validators(self):
        field = Field('name', [NotEmpty(), IsDigit()])

        field.validate()
        self.assertEqual(False, field.validate())

        field.reset()
        field.set_values(['green'])

        self.assertEqual(False, field.validate())

        field.reset()
        field.set_values(['15'])

        self.assertEqual(True, field.validate())

    def test_set_values(self):
        field = Field('name')

        field.set_values(['value'])

        field_value = field.values[0]
        assert 'value' == field_value.value

    def test_set_values_on_ignore(self):
        field = Field('name', ignore=True)

        field.set_values(['value'])

        assert 0 == len(field.values)

    def test_reset(self):
        field = Field('name')
        field.set_values(['val'])
        field.messages = ['msg']
        field.error = True

        field.reset()

        assert field.values == []
        assert field.messages == []
        assert field.error is False

    def test_set_error(self):
        field = Field('name')

        field.set_error('msg')

        assert field.error is True
        assert field.messages[0].text == 'msg'

    def test_get_name(self):
        form = Form()
        field = form.add_field('name1')

        raw = field.get_name()

        json = urlsafe_b64decode(raw).decode()
        data = loads(json)

        assert data == {
            'name': 'name1',
            'parents': [{'name': 'Form', 'index': None}],
        }

    def test_get_name_tree(self):
        form = Form()
        form2 = Form()
        field = form2.add_field('name1')
        form.add_sub_form(form2)

        raw = field.get_name()

        json = urlsafe_b64decode(raw).decode()
        data = loads(json)

        assert data == {
            'name': 'name1',
            'parents': [
                {'name': 'Form', 'index': None},
                {'name': 'Form', 'index': 0}],
        }

    def test_get_name_tree_with_index(self):
        form = Form()
        form2 = Form()
        form2.add_field('name1')
        form.add_sub_form(form2)

        field = form.get_or_create_sub_form('Form', 2).fields['name1']

        raw = field.get_name()

        json = urlsafe_b64decode(raw).decode()
        data = loads(json)

        assert data == {
            'name': 'name1',
            'parents': [
                {'name': 'Form', 'index': None},
                {'name': 'Form', 'index': 2},
            ],
        }

    def test_index_error(self):
        form = Form()
        form.add_field('name')

        with raises(IndexError):
            form.get_value('name')

    def test_defaul(self):
        form = Form()
        form.add_field('name')

        assert form.get_value('name', default='elf') == 'elf'


class GetValueErrorTests(FormskitTestCase):

    def setUp(self):
        super().setUp()
        self.field = Field('name')

    def test_index_error(self):
        with raises(IndexError):
            self.field.get_value_error()

    def test_defaul(self):
        assert self.field.get_value_error(default='elf') == 'elf'

    def test_normal(self):
        self.field.values.append(FieldValue(self.field, 'val'))
        self.field.values[0].message = 'my error'

        assert self.field.get_value_error() == 'my error'
