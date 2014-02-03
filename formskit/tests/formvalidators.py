from formskit import Form, Field
from formskit.tests.base import FormskitTestCase
from formskit.formvalidators import FormValidator, MustBeTheSame


class Form1(Form):

    name1 = 'something'
    name2 = 'something2'

    def create_form(self):
        self.add_field(Field(self.name1))
        self.add_field(Field(self.name2))

        self.add_form_validator(
            MustBeTheSame([self.name1, self.name2], 'input'))


class FormValidatorTest(FormskitTestCase):

    def test_base(self):
        validator = FormValidator()
        validator.set_form(self)

        self.assertEqual(self, validator.form)

    def test_MustBeTheSame(self):
        form = Form1()
        form._assign_field_value(form.name1, '1')
        form._assign_field_value(form.name2, '2')

        self.assertFalse(form._validate_fields())
        self.assertEqual(True, form.error)
        self.assertEqual('input must be the same!', form.message)

        form = Form1()
        form._assign_field_value(form.name1, '1')
        form._assign_field_value(form.name2, '1')

        self.assertTrue(form._validate_fields())
        self.assertEqual(False, form.error)
        self.assertEqual(None, form.message)
