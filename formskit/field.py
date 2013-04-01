from formskit.validators import ValidationError


class Field(object):

    def __init__(self, name, validators=[], label=None, ignore=False):
        self.name = name
        self.label = label
        self.validators = validators
        self.ignore = ignore
        self.value = None
        self.form = None
        self.message = None
        self.error = False

    def initForm(self, form):
        self.form = form

    def validate(self):
        try:
            for validator in self.validators:
                validator(self.value)
            self.message = None
            self.error = False
            return True
        except ValidationError, ex:
            self.message = ex.message
            self.error = True
            return False

class Button(Field):
    def __init__(self, name, label):
        super(Button, self).__init__(name, label=label, ignore=True)
