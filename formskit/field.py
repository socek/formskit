class Field(object):

    def __init__(self, name, validators=None, label=None, ignore=False):
        self.name = name
        self.label = label
        self.ignore = ignore
        self.form = None
        self.init_validators(validators)
        self.reset()

    def init_validators(self, validators=None):
        self.field_validators = []
        self.value_validators = []
        validators = validators or []
        for validator in validators:
            validator.init_field(self)
            if validator._type == 'value':
                self.value_validators.append(validator)
            else:
                self.field_validators.append(validator)

    def init_form(self, form):
        self.form = form

    def set_values(self, values):
        if self.ignore:
            return
        for value in values:
            self.values.append(
                FieldValue(
                    self,
                    value
                )
            )

    def reset(self):
        self.values = []
        self.messages = []
        self.error = False

    def validate(self):
        for validator in self.field_validators:
            validator.make()
        if self.error:
            return False
        for validator in self.value_validators:
            for value in self.values:
                validator.make(value)
        return not self.error

    def set_error(self, message):
        self.error = True
        self.messages.append(message)


class FieldValue(object):

    def __init__(self, field, value):
        self.field = field
        self.value = value
        self.error = False
        self.message = None

    def set_error(self, message):
        self.error = True
        self.field.error = True
        self.message = message
