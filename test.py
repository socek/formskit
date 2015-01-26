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

print(form.get_data_dict(True))
{
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
