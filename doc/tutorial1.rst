=================
2.1 Base Tutorial
=================

2.1.1 First Form
================

Formskit was designed to make forms as simple as possible.

.. code-block:: python

    from formskit import Form
    form = Form()
    form.add_field('myfield')

So now we have first form. To validate data, we just need to put it in this
object. Form is designed to use dict with key as field names and list of values,
because there can be many values for one field.

.. code-block:: python

    form({'form_name': [form.get_name()], 'myfield':['value']})
    >> True

Form call will return ``True`` if form is successfully validated, ``False`` if
not or ``None`` if the form is not submited at all. You can notice extra
parametr ``form_name``, which indicates that we want to submit this specyfic
form. Name is generated from class name, so if you want to make more forms you
need to inherit from Form class.

To get all the validated data, just user .get_data_dict method.

.. code-block:: python

    form.get_data_dict()
    >> {'myfield': ['value']}
    form.get_data_dict(True)
    >> {'myfield': 'value'}

``True`` in the argument list enables minifing, to if there is only 1 value,
then there will be no list.

2.1.2 Field Validators
======================

To add validators, just append it to the ``.add_field`` method. In the next
example we will add IsDigit validator which will fail if the inputed text is
not made only from digits.

.. code-block:: python

    from formskit import Form
    from formskit.validators import IsDigit
    form = Form()
    form.add_field('myfield', validators=[IsDigit()])
    form({'form_name': [form.get_name()], 'myfield':['123']})
    >> True
    form({'form_name': [form.get_name()], 'myfield':['123.1']})
    >> False
    form.get_report()
    >> {
        'success': False,
        'fields': {
            'myfield': {
                'success': False,
                'messages': [],
                'values': [
                    {
                        'value': 'value',
                        'success': False,
                        'messages': [
                            'IsDigit'
                        ]
                    }
                ]
            }
        },
        'messages': []}

Report dict may seem a little blurry. But it was made with simple rules.
``success`` value is set to ``False``, when validating is failed at that moment,
and every above ``success``. ``messages`` value is list of messages raised by
validation. ``fields`` are dict of fields in the form, where key is field name.
Every field has a ``success``, ``messages`` and ``values`` keys. There can be
many values for one field, so every validation is made per field (for
validation like ``NotEmpty``) and per value.

.. todo::

    make link to list of validators.

2.1.3 Form Validators
=====================

To be able to validate form as a whole, not just fields, you can use Form
Validators.

.. code-block:: python

    from formskit import Form
    from formskit.formvalidators import MustMatch

    form = Form()
    form.add_field('password1')
    form.add_field('password2')
    form.add_form_validator(MustMatch(['password1', 'password2']))
    form({
        'form_name': [form.get_name()],
        'password1':['password'],
        'password2': ['password']
    })
    >> True
    form({
        'form_name': [form.get_name()],
        'password1':['password'],
        'password2': ['password2']
    })
    >> False

.. todo::

    make link to list of validators.

2.1.4 Getting the data
======================

Getting data is very simple. Using ``get_data_dict`` you can get all data in the
dict object.

.. code-block:: python

    from formskit import Form
    form = Form()
    form.add_field('myfield')
    form.add_field('second_field')
    form.add_field('this_will_be_empty')
    form({
        'form_name': [form.get_name()],
        'myfield':['123.1'],
        'second_field': ['something', 'something2']
    })
    form.get_data_dict()
    >>  {
        'second_field': ['something', 'something2'],
        'myfield': ['123.1'],
        'this_will_be_empty': []
    }

Form has a 3 fields named ``myfield``, ``second_field`` and
``this_will_be_empty``. After submitting, we can retrive all the data. All
fields will be keys in the dict with list of all the values. If we past ``True`` to
the method, then the data will be minified (empty values will not be shown,
single values will not be in form of a list).

.. code-block:: python

    form.get_data_dict(True)
    >> {
        'second_field': ['something', 'something2'],
        'myfield': '123.1'
    }

2.1.5 Converting
================

Form values are always strings, but sometimes you know that some values will be
converted, so convert feature is here to help you.

.. code-block:: python

    from formskit import Form
    from formskit.field_convert import ToInt
    form = Form()
    form.add_field('myfield', convert=ToInt())
    form({
        'form_name': [form.get_name()],
        'myfield':['123'],
    })
    form.get_data_dict(True)
    >> {'myfield': 123}

2.1.6 Defaults
==============

When you want to set default values, you can do this by using `parse_dict`.

.. code-block:: python

    from formskit import Form
    form = Form()
    form.add_field('myfield')
    form.add_field('myfield2')
    form.add_field('myfield3')
    form.parse_dict({
        'myfield': 'one',
        'myfield2': ['two', 'three'],
    })
    form.get_data_dict()
    >> {
        'myfield': ['one'],
        'myfield2': ['two', 'three'],
        'myfield3': []
    }

As you can see, `parse_dict` can detect if we put the data in list or not. Now
we can submit a form.

.. code-block:: python

    form({
        'form_name': [form.get_name()],
        'myfield2': ['456'],
    })
    form.get_data_dict()
    >> {
        'myfield': ['one'],
        'myfield2': ['456'],
        'myfield3': []
    }

New values will make field to reset (so old default values will be removed).
Thats why `myfield2` do not have 'three' value.


2.1.7 Field Ignoring
====================
