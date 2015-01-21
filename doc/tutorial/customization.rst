=================
2.3 Customization
=================

Sometime you need to do some customization. This chapter will try to help with
this task.

2.3.1 Form validators
=====================

Field validation is made in two steps:

- validate field
- validate every value

Validating field is made to make validation of situations like "no value found"
or how many values needs to be at the field. Second step is just to validate
every value which was provided for field.

.. code-block:: python

    from formskit import Form
    from formskit.validators import FieldValidator

    class MyValidator(FieldValidator):
        message = 'my message'
        def validate_field(self):
            print('field:', len(self.field.values))
            return len(self.field.values) > 0
        def validate_value(self):
            print('value:', self.value)
            return self.value.startswith('val')

    form = Form()
    form.add_field('myfield', validators=[MyValidator()])
    form.validate({
        'form_name': [form.get_name()],
        'myfield': ['val_1', 'val_2'],
    })
    # field: 2
    # value: val_1
    # value: val_2
    >> True

    form.validate({
        'form_name': [form.get_name()],
        'myfield': ['val_1', 'bad'],
    })
    # field: 2
    # value: val_1
    # value: bad
    >> False

    form.get_report()
    >> {
        'fields': {
            'myfield': {
                'messages': [],
                'success': False,
                'values': [
                    {'messages': [],
                     'success': True,
                     'value': 'val_1'},
                    {'messages': ['my message'],
                     'success': False,
                     'value': 'bad'}
                ]
            }
        },
        'messages': [],
        'success': False
    }

2.3.2 Form validators
=====================

.. code-block:: python

    class MustMatch(FormValidator):
        """Will fail if first values of provided field names are not the same."""

        message = 'input must be the same!'

        def __init__(self, names):
            self.names = names

        def validate(self):
            values = []
            for name in self.names:
                field = self.form.fields[name]
                try:
                    values.append(field.values[0].value)
                except IndexError:
                    return False
            first = values.pop(0)
            for value in values:
                if first != value:
                    return False
            return True

2.3.3 Inner validation
======================

.. code-block:: python

    def _validate(self):
        # Why this method was implemented in this way?
        # Goal was to run validation on fields and if it succeeded, then form
        # can run form validators.
        # But sub_forms should always run validation.
        self.success = True
        self.success &= (
            self._validate_fields()
            and self._validate_form_validators()
        )
        return self.success

2.3.4 Converters
================

.. code-block:: python

    class ToInt(FakeConvert):
        """Converts to int."""

        def convert(self, value):
            return int(value)

        def convert_back(self, value):
            return str(value)
