from .field import Field
from .formvalidators import FormValidationError
from .messages import Message


class Form(object):

    form_name_value = 'form_name'
    message_class = Message

    def get_name(self):
        return self.__class__.__name__

    def __init__(self):
        self._init_before_create()
        self.create_form()
        self.reset()

    def _init_before_create(self):
        self.fields = {}
        self.form_validators = []
        self.raw_data = None
        self.index = None

    def add_field_object(self, field):
        self.fields[field.name] = field
        field.init_form(self)

    def add_field(self, *args, **kwargs):
        field = Field(*args, **kwargs)
        self.add_field_object(field)
        return field

    def __call__(self, raw_data):
        if self._is_form_submitted(raw_data):
            self._parse_raw_data(raw_data)
            if self._validate():
                self.submit()
                return True
            else:
                return False
        else:
            return None

    def _is_form_submitted(self, raw_data):
        return raw_data.get(self.form_name_value, None) == [self.get_name(), ]

    def _parse_raw_data(self, raw_data):
        for name, values in raw_data.items():
            if name == self.form_name_value:
                continue
            field = self._get_field(name)
            field.set_values(values)

    def _get_field(self, name):
        try:
            return self.fields[name]
        except KeyError:
            raise WrongValueName(name)

    def reset(self):
        self.success = None
        self.messages = []
        for field in self.fields.values():
            field.reset()

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

    def _validate_fields(self):
        success = True
        for field in self.fields.values():
            success &= field.validate()
        return success

    def create_form(self):
        pass

    def _validate_form_validators(self):
        success = True
        for validator in self.form_validators:
            try:
                validator()
            except FormValidationError as er:
                message = self._get_message_object()
                message.init(er.message, form=self)
                self.messages.append(message)
                success = False
        return success

    def add_form_validator(self, validator):
        validator.set_form(self)
        self.form_validators.append(validator)

    def get_values(self, name):
        return self.fields[name].get_values()

    def get_value(self, name, index=0, default=NotImplemented):
        return self.fields[name].get_value(index, default)

    def set_values(self, name, values, force=False):
        self.fields[name].set_values(values, force=force)

    def set_value(self, name, value, index=0, force=False):
        self.fields[name].set_value(value, index, force=force)

    def submit(self):
        pass

    def get_data_dict(self, minified=False):
        tree = {}
        for name, field in self.fields.items():
            tree[name] = field.get_values()
            if minified and len(tree[name]) == 1:
                tree[name] = tree[name][0]
            elif minified and len(tree[name]) == 0:
                del tree[name]
        return tree

    def parse_dict(self, data):
        for name, values in data.items():
            if name in self.fields:
                field = self.fields[name]
                if hasattr(values, '__iter__') and type(values) is not str:
                    field.set_values(values)
                else:
                    field.set_value(values)
            else:
                self._parse_sub_form(name, values)

    def get_report(self):
        def convert(messages):
            data = []
            for message in messages:
                data.append(message())
            return data

        report = {
            'success': self.success,
            'messages': convert(self.messages),
            'fields': {},
        }
        for name, field in self.fields.items():
            values = []
            for value in field.values:
                values.append({
                    'value': value.value,
                    'success': not value.error,
                    'messages': convert(value.messages),
                })
            report['fields'][name] = {
                'success': not field.error,
                'messages': convert(field.messages),
                'values': values,
            }
        return report

    def _get_message_object(self, *args, **kwargs):
        return self.message_class(*args, **kwargs)


class WrongValueName(Exception):

    def __init__(self, name):
        self.name = name
