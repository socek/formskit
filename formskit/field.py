class Field(object):

    def __init__(self, name, validators=None, label=None, ignore=False):
        self.name = name
        self.label = label
        self.ignore = ignore
        self.form = None
        self.init_validators(validators)
        self.reset()

    def init_validators(self, validators=None):
        self.validators = validators or []
        for validator in self.validators:
            validator.init_field(self)

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
        self.message = None
        self.error = False

    def validate(self):
        for validator in self.validators:
            for value in self.values:
                self.error |= not validator.validate_value(value)
        return not self.error


class FieldValue(object):

    def __init__(self, field, value):
        self.field = field
        self.value = value
        self.error = False
        self.message = None
