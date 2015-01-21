======================
2.2 Translation system
======================

2.2.1 Simple translation
========================

From prevoiuse chapters, you could see that .get_report is returning simple
texts, not whole error text For example, NotEmpty validator returns only
'NotEmpty' text. It is because no translation system is implemented, so the
system only returns validator name. To use translation system you need to make
a subclass of Translation, and put it into your Form.

.. code-block:: python

    from formskit import Form
    from formskit.validators import NotEmpty
    from formskit.translation import Translation

    class Translated(Translation):
        _translations = {
            'NotEmpty': 'This field ca not be empty.',
        }
        def translate(self):
            return self._translations[self.text]

    class MyForm(Form):
        translation_class = Translated
        def create_form(self):
            self.add_field('myfield', validators=[NotEmpty()])

    form = MyForm()
    form.validate({
        'form_name': [form.get_name()],
        'myfield': [],
    })
    form.get_report()
    >> {
        'success': False,
            'fields': {
                'myfield': {
                    'success': False,
                    'messages': ['This field ca not be empty.'],
                    'values': []
                }
            },
            'messages': []
        }

2.2.2 Formatting and arguments
==============================

Every translation has arguments. It is different for 3 fazes:

* Field Value Error
    * ``.field`` (Field)
    * ``.value`` (FieldValue)
* Field Error
    * ``.field`` (Field)
* Form Error
    * ``.form`` (Form)

Example:

.. code-block:: python

    from formskit import Form
    from formskit.validators import NotEmpty
    from formskit.translation import Translation

    class Translated(Translation):
        _translations = {
            'NotEmpty': 'This field ca not be empty: {field.name}.',
        }
        def translate(self):
            return self._translations[self.text]

    class MyForm(Form):
        translation_class = Translated
        def create_form(self):
            self.add_field('myfield', validators=[NotEmpty()])

    form = MyForm()
    form.validate({
        'form_name': [form.get_name()],
        'myfield': [],
    })
    form.get_report()
        >> {
            'success': False,
                'fields': {
                    'myfield': {
                        'success': False,
                        'messages': ['This field ca not be empty: myfield.'],
                        'values': []
                    }
                },
                'messages': []
            }
