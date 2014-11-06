from formskit.tests.base import FormskitTestCase
from formskit import Field
from formskit.validators import NotEmpty, IsDigit, NeedToHaveValue


class FieldTest(FormskitTestCase):

    def test_init_form(self):
        form = 123
        field = Field(None, None, None)
        field.init_form(form)

        self.assertEqual(form, field.form)

    def test_validate(self):
        needtohavevalue = NeedToHaveValue()
        field = Field('name', [needtohavevalue])

        self.assertEqual(False, field.validate())
        self.assertEqual(field, needtohavevalue.field)

        field.reset()
        field.set_values(['green'])

        self.assertEqual(True, field.validate())

    def test_two_validators(self):
        field = Field('name', [NeedToHaveValue(), NotEmpty(), IsDigit()])

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
        assert field.messages == ['msg']
