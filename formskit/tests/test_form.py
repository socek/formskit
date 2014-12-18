from mock import create_autospec
from unittest import TestCase
from pytest import raises

from formskit.field import Field
from formskit.form import Form, TreeForm, WrongValueName
from formskit.validators import NotEmpty, IsDigit
from formskit.field_convert import ToInt
from formskit.formvalidators import FormValidator


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

    def test_parse_test_data(self):
        form = Form()
        form.add_field('name')
        form.add_field('second')

        form.parse_dict({
            'name': ['n1'],
            'second': 'n2',
        })

        assert form.get_value('name') == 'n1'
        assert form.get_value('second') == 'n2'


class TreeFormTest(TestCase):

    def test_reset(self):
        field = create_autospec(Field('name'))
        form = TreeForm()
        form.add_field_object(field)
        form2 = create_autospec(TreeForm())
        form2_name = form2.get_name.return_value
        form.add_sub_form(form2)
        form.get_or_create_sub_form(form2_name, 3)

        form.success = False

        form.reset()

        assert form.success is None
        field.reset.assert_called_once_with()
        assert len(form.childs[form2_name]) == 1
        form2.reset.assert_called_once_with()

    def test_parse_test_data(self):
        form = TreeForm()
        form.add_field('name')
        form.add_field('second')
        form2 = TreeForm()
        form2.add_field('surname')
        form.add_sub_form(form2)

        form.parse_dict({
            'name': ['n1'],
            'second': 'n2',
            'TreeForm': [{
                'surname': ['s1']
            }]
        })

        assert form.get_value('name') == 'n1'
        assert form.get_value('second') == 'n2'

    def test_error_decoding_name(self):
        form = TreeForm()
        form.add_field('one')
        name = form.fields['one'].get_name()
        raw_data = {
            name.replace(b'x', b'y'): ['value'],
        }

        with raises(WrongValueName):
            form._parse_raw_data(raw_data)


class TestGetAndSet(TestCase):

    def setUp(self):
        super().setUp()
        self.form = Form()
        self.form.add_field('name')

    def test_set_once(self):
        self.form.set_value('name', 'value')

        assert self.form.get_value('name') == 'value'
        assert self.form.get_values('name') == ['value']

    def test_set_once_with(self):
        self.form.set_value('name', 'value', 1)
        self.form.set_value('name', 'value2', 1)
        self.form.set_value('name', 'value3', 1)

        assert self.form.get_value('name', 0) == 'value'
        assert self.form.get_value('name', 1) == 'value3'
        assert self.form.get_values('name') == ['value', 'value3']

    def test_set_many(self):
        self.form.set_values('name', ['one', 'two'])

        assert self.form.get_value('name', 0) == 'one'
        assert self.form.get_value('name', 1) == 'two'
        assert self.form.get_values('name') == ['one', 'two']

    def test_set_many_with_converter(self):
        self.form.add_field('name2', convert=ToInt())
        self.form.set_values('name2', ['2', '3'])

        assert self.form.get_value('name2', 0) == 2
        assert self.form.get_value('name2', 1) == 3
        assert self.form.get_values('name2') == [2, 3]

    def test_ignore(self):
        self.form.fields['name'].ignore = True

        self.form.set_value('name', 'one')
        self.form.set_values('name', ['one', 'two'])

        assert self.form.get_values('name') == []

    def test_force(self):
        self.form.fields['name'].ignore = True

        self.form.set_value('name', 'one', force=True)

        assert self.form.get_values('name') == ['one']

    def test_force_many(self):
        self.form.fields['name'].ignore = True

        self.form.set_values('name', ['one', 'two'], force=True)

        assert self.form.get_values('name') == ['one', 'two']


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
        self.form = TreeForm()
        self.field = self.form.add_field('one')

        self.subform = TreeForm()
        self.subform.add_field('two', validators=[NotEmpty()])
        self.form.add_sub_form(self.subform)

    def _get_raw_data(self, value='value3'):
        raw_data = {
            self.form.form_name_value: [self.form.get_name(), ],
            self.form.fields['one'].get_name(): ['value1'],

        }
        name = (
            self.form.get_or_create_sub_form('TreeForm', 2)
            .fields['two'].get_name()
        )
        raw_data[name] = ['value2.1', 'value2.2']
        name = (
            self.form.get_or_create_sub_form('TreeForm', 3)
            .fields['two'].get_name()
        )
        raw_data[name] = [value]

        return raw_data

    def test_parse_tree(self):
        raw_data = self._get_raw_data()

        self.form(raw_data)

        assert self.form.fields['one'].values[0].value == 'value1'

        field = self.form.get_sub_form('TreeForm', 2).fields['two']
        assert field.values[0].value == 'value2.1'
        assert field.values[1].value == 'value2.2'

        field = self.form.get_sub_form('TreeForm', 3).fields['two']
        assert field.values[0].value == 'value3'

    def test_validation(self):
        raw_data = self._get_raw_data('')

        self.form(raw_data)

        assert self.form.success is False

        field = self.form.get_sub_form('TreeForm', 2).fields['two']
        assert field.error is False

        field = self.form.get_sub_form('TreeForm', 3).fields['two']
        assert field.error is True


class GetDataDictTest(TestCase):

    def setUp(self):
        super().setUp()
        self.form = Form()
        self.form.add_field('name1')
        self.form.add_field('name2')

        data = {
            self.form.form_name_value: [self.form.get_name()],
            'name1': ['one'],
            'name2': ['two', 'three'],
        }

        self.form(data)

    def test_dict(self):
        assert self.form.get_data_dict() == {
            'name1': ['one'],
            'name2': ['two', 'three'],
        }

    def test_dict_minified(self):
        assert self.form.get_data_dict(True) == {
            'name1': 'one',
            'name2': ['two', 'three'],
        }


class GetDataDictTreeTest(TestCase):

    def setUp(self):
        super().setUp()
        self.form = TreeForm()
        self.form.add_field('name1')

        subform = TreeForm()
        subform.add_field('name2')

        self.form.add_sub_form(subform)

        data = {
            self.form.form_name_value: [self.form.get_name()],
            self.form.fields['name1'].get_name(): ['one'],
            (
                self.form.get_or_create_sub_form('TreeForm', 0)
                .fields['name2'].get_name()
            ): [
                'two',
                'three'],
            (
                self.form.get_or_create_sub_form('TreeForm', 1)
                .fields['name2'].get_name()
            ): [
                'four'],
            (
                self.form.get_or_create_sub_form('TreeForm', 2)
                .fields['name2'].get_name()
            ): [],
        }

        self.form(data)

    def test_tree(self):
        assert self.form.get_data_dict() == {
            'name1': ['one'],
            'TreeForm': {
                0: {'name2': ['two', 'three']},
                1: {'name2': ['four']},
                2: {'name2': []},
            }
        }

    def test_tree_minified(self):
        assert self.form.get_data_dict(True) == {
            'name1': 'one',
            'TreeForm': {
                0: {'name2': ['two', 'three']},
                1: {'name2': 'four'},
                2: {},
            }
        }


class ExampleFormValidator(FormValidator):

    def __init__(self):
        super().__init__()
        self._validate = True

    def validate(self):
        return self._validate


class GetReportTest(TestCase):

    def setUp(self):
        super().setUp()
        self.form = Form()
        self.form.add_field('name1', validators=[NotEmpty()])
        self.form.add_field('name2', validators=[IsDigit()])
        self.form_validator = ExampleFormValidator()
        self.form.add_form_validator(self.form_validator)

    def run_form(self):
        data = {
            self.form.form_name_value: [self.form.get_name()]
        }
        return self.form(data)

    def test_success(self):
        self.form.parse_dict({
            'name1': ['one'],
        })
        assert self.run_form() is True

        assert self.form.get_report() == {
            'success': True,
            'message': None,
            'fields': {
                'name1': {
                    'success': True,
                    'messages': [],
                    'values': [{
                        'value': 'one',
                        'success': True,
                        'message': None,
                    }]
                },
                'name2': {
                    'success': True,
                    'messages': [],
                    'values': []
                },
            }
        }

    def test_error_at_form_validator(self):
        self.form.parse_dict({
            'name1': ['one'],
        })
        self.form_validator._validate = False
        assert self.run_form() is False

        assert self.form.get_report() == {
            'success': False,
            'message': self.form.message,
            'fields': {
                'name1': {
                    'success': True,
                    'messages': [],
                    'values': [{
                        'value': 'one',
                        'success': True,
                        'message': None,
                    }]
                },
                'name2': {
                    'success': True,
                    'messages': [],
                    'values': []
                },
            }
        }

    def test_error_at_field_validator(self):
        self.form.parse_dict({
        })
        assert self.run_form() is False

        assert self.form.get_report() == {
            'success': False,
            'message': None,
            'fields': {
                'name1': {
                    'success': False,
                    'messages': self.form.fields['name1'].messages,
                    'values': []
                },
                'name2': {
                    'success': True,
                    'messages': [],
                    'values': []
                },
            }
        }

    def test_error_at_field_value_validator(self):
        self.form.parse_dict({
            'name1': ['one'],
            'name2': ['three']
        })
        assert self.run_form() is False

        assert self.form.get_report() == {
            'success': False,
            'message': None,
            'fields': {
                'name1': {
                    'success': True,
                    'messages': [],
                    'values': [{
                        'value': 'one',
                        'success': True,
                        'message': None,
                    }]
                },
                'name2': {
                    'success': False,
                    'messages': [],
                    'values': [{
                        'value': 'three',
                        'success': False,
                        'message': self.form.fields['name2'].values[0].message,
                    }]
                },
            }
        }
