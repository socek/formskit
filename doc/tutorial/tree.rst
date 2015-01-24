=============
2.4 Tree Form
=============

2.4.1 About Tree Form
=====================

Tree form is a way to make subforms. For example, when you need to have name and
surname for many people. You should just make 1 form for the name and surname,
and another form for the rest.

2.4.2 First tree form
=====================

.. code-block:: python

    from formskit.tree_form import TreeForm


    class PeopleForm(TreeForm):

        def create_form(self):
            self.add_field('name')
            self.add_field('surname')


    class MainForm(TreeForm):

        def create_form(self):
            self.add_field('something')
            self.add_sub_form(PeopleForm())

    form = MainForm()
    form.validate({
        'form_name': [form.get_name()],
        form.fields['something'].get_name(): ['value'],
        form.get_or_create_sub_form('PeopleForm', 0).fields['name'].get_name(): [
            'name1'],
        form.get_or_create_sub_form('PeopleForm', 0).fields['surname'].get_name(): [
            'surname1'],
        form.get_or_create_sub_form('PeopleForm', 1).fields['name'].get_name(): [
            'name2'],
        form.get_or_create_sub_form('PeopleForm', 1).fields['surname'].get_name(): [
            'surname2'],
    })

    form.get_data_dict(True)
    >> {
        'something': 'value',
        'PeopleForm': {
            0: {
                'name': 'name1',
                'surname': 'surname1'
            },
            1: {
                'name': 'name2',
                'surname': 'surname2'
            }
        }
    }

2.4.3 Naming of fields
======================

As you can see, generating names for the form fields is a little bit tricky.
When we have only ``name=surname`` method to send values, we need to make some
magic. The "name" is not only name of the field, but a whole address for the
field (which subform to put this value). Technicly it is just json encode with
base64 (after generating the name, you can decode it and see for yourself).
All the name in your HTML should be generated this way.

.. note::

    Some people consider ``addressing by name`` as insecure.

2.4.4 What is technicly different?
==================================

When you use TreeForm you can not use Form as a subform. Also, you need to use
TreeField instead of Field. All the rest (Validator, FormValidator and Convert)
should work as for Form.
