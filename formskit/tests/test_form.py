from mock import create_autospec
from unittest import TestCase
from pytest import raises

from formskit.field import Field
from formskit.form import Form, WrongValueName
from formskit.validators import NotEmpty


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

    def test_is_validated(self):
        form = Form()

        data = {
            form.form_name_value: [form.get_name(), ],
        }
        assert form(data) is True

    def test_is_not_submited(self):
        form = Form()

        assert form({}) is None

    def test_if_not_validated(self):
        form = Form()
        form.add_field('name', validators=[NotEmpty()])

        data = {
            form.form_name_value: [form.get_name(), ],
        }
        assert form(data) is False


class IsFormSubmittedTest(TestCase):

    def test_name_do_not_match(self):
        form = Form()
        raw_data = {
            Form.form_name_value: [form.get_name() + 'bad'],
        }

        assert form._is_form_submitted(raw_data) is False

    def test_name_match(self):
        form = Form()
        raw_data = {
            Form.form_name_value: [form.get_name()],
        }

        assert form._is_form_submitted(raw_data) is True

    def test_not_form_data(self):
        form = Form()
        raw_data = {}

        assert form._is_form_submitted(raw_data) is False


class ParseRawDataTest(TestCase):

    def setUp(self):
        self.form = Form()
        self.field = self.form.add_field('one')

    def test_good_data(self):
        raw_data = {
            self.form.fields['one'].get_name(): ['value']
        }

        self.form._parse_raw_data(raw_data)

        assert self.form.fields['one'].values[0].value == 'value'

    def test_too_many_data(self):
        raw_data = {
            self.form.fields['one'].get_name(): ['value'],
            'two': ['something'],
        }

        with raises(WrongValueName):
            self.form._parse_raw_data(raw_data)

    def test_too_few_data(self):
        raw_data = {}

        self.form._parse_raw_data(raw_data)

        assert self.form.fields['one'].values == []


class TreeFormsTest(TestCase):

    def setUp(self):
        self.form = Form()
        self.field = self.form.add_field('one')

        self.subform = Form()
        self.subform.add_field('two', validators=[NotEmpty()])
        self.form.add_sub_form(self.subform)

    def _get_raw_data(self, value='value3'):
        raw_data = {
            self.form.form_name_value: [self.form.get_name(), ],
            self.form.fields['one'].get_name(): ['value1'],

        }
        name = (
            self.form.get_or_create_sub_form('Form', 2)
            .fields['two'].get_name()
        )
        raw_data[name] = ['value2.1', 'value2.2']
        name = (
            self.form.get_or_create_sub_form('Form', 3)
            .fields['two'].get_name()
        )
        raw_data[name] = [value]

        return raw_data

    def test_parse_tree(self):
        raw_data = self._get_raw_data()

        self.form(raw_data)

        assert self.form.fields['one'].values[0].value == 'value1'

        field = self.form.get_sub_form('Form', 2).fields['two']
        assert field.values[0].value == 'value2.1'
        assert field.values[1].value == 'value2.2'

        field = self.form.get_sub_form('Form', 3).fields['two']
        assert field.values[0].value == 'value3'

    def test_validation(self):
        raw_data = self._get_raw_data('')

        self.form(raw_data)

        assert self.form.success is False

        field = self.form.get_sub_form('Form', 2).fields['two']
        assert field.error is False

        field = self.form.get_sub_form('Form', 3).fields['two']
        assert field.error is True
