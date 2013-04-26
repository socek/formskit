from formskit import Form, Field, Button
from formskit.errors import BadValue, ValueNotPresent
from formskit.tests.base import FormskitTestCase
from formskit.validators import NotEmpty


class SampleObject(object):

    def __init__(self, name1='value1', name2='value2'):
        self.name1 = name1
        self.name2 = name2

class SampleObject2(object):

    def __init__(self, name1='value1'):
        self.name1 = name1


class Form1(Form):

    submitTest = False
    overal = False
    name1 = 'name1'

    def submit(self, data):
        self._test_data = data
        self.submitTest = True

    def overalValidation(self, data):
        return self.overal

    def createForm(self):
        self.addField(Field(self.name1))


class Form2(Form):
    name1 = 'name1'
    name2 = 'name2'

    def createForm(self):
        self.addField(Field(self.name1, [NotEmpty]))
        self.addField(Field(self.name2, [NotEmpty]))
        self.addField(Button('button', label=u'Zaloguj'))


class Form3(Form):
    name1 = 'name1'
    name2 = 'name2'

    def createForm(self):
        self.addField(Field(self.name1))
        self.addField(Field(self.name2, [NotEmpty()]))
        self.addField(Button('button', label=u'Zaloguj'))


class FormTest(FormskitTestCase):

    def test_name(self):
        self.assertEqual(Form1().name, 'Form1')

    def test_addField(self):
        name = 'rosomak'
        field = Field(name)
        form = Form1()
        form.addField(field)

        self.assertTrue(form.fields.has_key(name))
        self.assertEqual(field, form.fields[name])
        self.assertEqual(form, field.form)

    def test_gatherDataFromFields(self):
        name1 = 'rosomak'
        value1 = 'wolverine'
        name2 = 'stefan'
        value2 = 'robin'

        field1 = Field(name1)
        field1.value = value1

        field2 = Field(name2)
        field2.value = value2
        form = Form1()
        form.addField(field1)
        form.addField(field2)

        data = form.gatherDataFromFields()
        self.assertTrue(data.has_key(name1))
        self.assertTrue(data.has_key(name2))
        self.assertEqual(value1, data[name1])
        self.assertEqual(value2, data[name2])

    def test_createForm(self):
        form = Form2()

        self.assertTrue(form.fields.has_key(form.name1))
        self.assertTrue(form.fields.has_key(form.name2))

    def test_isThisFormSubmited(self):
        form = Form2()

        self.assertFalse(form._isThisFormSubmited({}))
        self.assertFalse(form._isThisFormSubmited({'form_name': 'Formasd2'}))
        self.assertTrue(form._isThisFormSubmited({'form_name': 'Form2'}))

    def test_gatherFormsData(self):
        form = Form1()

        name1 = 'name1'
        name2 = 'name2'

        field1 = Field(name1)
        field2 = Field(name2)
        form.addField(field1)
        form.addField(field2)

        value1 = 'value1'
        value2 = 'value2'

        data = {
            'form_name': 'Form1',
            name1: value1,
        }

        self.assertRaises(ValueNotPresent, form._gatherFormsData, data)

        data[name2] = value2

        form._gatherFormsData(data)

        self.assertEqual(value1, form.fields[name1].value)
        self.assertEqual(value2, form.fields[name2].value)

        data['name3'] = 'value3'
        self.assertRaises(BadValue, form._gatherFormsData, data)

    def test_validateFields(self):
        form = Form3()
        form.fields[form.name1].value = ''
        form.fields[form.name2].value = ''

        self.assertFalse(form._validateFields())
        self.assertFalse(form.fields['name1'].error)
        self.assertTrue(form.fields['name2'].error)
        self.assertNone(form.fields['name1'].message)
        self.assertEqual(NotEmpty.message, form.fields['name2'].message)

        form.fields[form.name1].value = 'asasdsd'
        self.assertFalse(form._validateFields())
        self.assertFalse(form.fields['name1'].error)
        self.assertTrue(form.fields['name2'].error)
        self.assertNone(form.fields['name1'].message)
        self.assertEqual(NotEmpty.message, form.fields['name2'].message)

        form.fields[form.name2].value = 'asd'
        self.assertTrue(form._validateFields())
        self.assertFalse(form.fields['name1'].error)
        self.assertFalse(form.fields['name2'].error)
        self.assertNone(form.fields['name1'].message)
        self.assertNone(form.fields['name2'].message)

    def test_validate_and_submit(self):
        form = Form1()
        form.overal = False

        self.assertFalse(form._validate_and_submit())
        self.assertFalse(form.submitTest)

        form = Form1()
        form.overal = True
        self.assertTrue(form._validate_and_submit())
        self.assertTrue(form.submitTest)
        self.assertEqual({form.name1: None}, form._test_data)

    def test_call(self):
        form = Form1()

        value1 = 'value1'

        data = {
            form.form_name_value: 'bad name',
            form.name1: value1,
        }

        self.assertNone(form(data))

        data[form.form_name_value] = form.name
        self.assertFalse(form(data))
        self.assertFalse(form.submitTest)

        form.overal = True
        self.assertTrue(form(data))
        self.assertTrue(form.submitTest)
        self.assertEqual({form.name1: value1}, form._test_data)

    def test_ignore(self):
        good_name = 'name1'
        good_value = 'value1'
        button_name = 'button1'
        form = Form1()
        form.overal = True
        form.addField(Button(button_name, 'label'))
        form.addField(Field(good_name))

        data = {
            form.form_name_value: form.name,
            good_name: good_value,
        }

        self.assertTrue(form(data))
        self.assertEqual(good_value, form[good_name].value)
        self.assertEqual(good_value, form._test_data[good_name])
        self.assertFalse(button_name in form._test_data)

    def test_update(self):
        s1 = SampleObject()
        form = Form3()
        form.update(s1)

        self.assertEqual(s1.name1, form['name1'].value)
        self.assertEqual(s1.name2, form['name2'].value)

        s2 = SampleObject('value1_2', 'value2_2')
        form.update(s2)

        self.assertEqual(s2.name1, form['name1'].value)
        self.assertEqual(s2.name2, form['name2'].value)

        s3 = SampleObject('value1_3', 'value2_3')
        form.update(s3, ['name1'])

        self.assertEqual(s3.name1, form['name1'].value)
        self.assertEqual(s2.name2, form['name2'].value)

        s4 = {
            'name1' : 'value1_4',
            'name2' : 'value2_4',
        }

        form.update(s4, method='dict')

        self.assertEqual(s4['name1'], form['name1'].value)
        self.assertEqual(s4['name2'], form['name2'].value)

        s5 = SampleObject2('value1_5')
        self.assertRaises(AttributeError, form.update, s5)

        s6 = SampleObject2('value1_6')
        form.update(s6, method='obj_default_none')
        self.assertEqual(s6.name1, form['name1'].value)
        self.assertEqual(None, form['name2'].value)

        s7 = SampleObject2('value1_7')
        def method(obj, name):
            return name
        form.update(s7, method=method)
        self.assertEqual('name1', form['name1'].value)
        self.assertEqual('name2', form['name2'].value)

        s8 = SampleObject2('value1_8')
        form.update(s8, ignore_missing=True)
        self.assertEqual(s8.name1, form['name1'].value)
        self.assertEqual('name2', form['name2'].value)
