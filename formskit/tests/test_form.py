from mock import create_autospec
from unittest import TestCase
from pytest import raises

from formskit.field import Field
from formskit.form import Form


class FormTest(TestCase):

    def test_add_field_object(self):
        field = create_autospec(Field('name'))
        form = Form()
        form.add_field_object(field)

        field.init_form.assert_called_once_with(form)
        assert field is form.fields[field.name]

    def test_add_field(self):
        form = Form()
        form.add_field('myname')

        assert isinstance(form.fields['myname'], Field)

    def test_reset(self):
        field = create_autospec(Field('name'))
        form = Form()
        form.add_field_object(field)

        form.success = False

        form.reset()

        assert form.success is None
        field.reset.assert_called_once_with()


class IsFormSubmittedTest(TestCase):

    def test_name_do_not_match(self):
        form = Form()
        raw_data = {
            Form.form_name_value: [form.name + 'bad'],
        }

        assert form._is_form_submitted(raw_data) is False

    def test_name_match(self):
        form = Form()
        raw_data = {
            Form.form_name_value: [form.name],
        }

        assert form._is_form_submitted(raw_data) is True

    def test_not_form_data(self):
        form = Form()
        raw_data = {}

        assert form._is_form_submitted(raw_data) is False


class ParseRawDataTest(TestCase):

    def setUp(self):
        self.form = Form()
        self.form.add_field('one')

    def test_good_data(self):
        raw_data = {
            'one': ['value']
        }

        self.form._parse_raw_data(raw_data)

        assert self.form.fields['one'].values[0].value == 'value'

    def test_too_many_data(self):
        raw_data = {
            'one': ['value'],
            'two': ['something'],
        }

        with raises(KeyError):
            self.form._parse_raw_data(raw_data)

    def test_too_few_data(self):
        raw_data = {}

        self.form._parse_raw_data(raw_data)

        assert self.form.fields['one'].values == []
