from copy import copy

from formskit.errors import BadValue
from formskit.formvalidators import FormValidationError


class Form(object):

    form_name_value = 'form_name'

    def __init__(self, parent=None):
        self.fields = {}
        self.field_patterns = {}
        self.formValidators = []
        self.error = False
        self.message = None
        self.data = None
        self.parent = parent
        self.create_form()

    @property
    def name(self):
        return self.__class__.__name__

    def add_field(self, field):
        self.field_patterns[field.name] = field
        field.init_form(self)

    def add_form_validator(self, validator):
        validator.set_form(self)
        self.formValidators.append(validator)

    def gather_data_from_fields(self):
        data = {}
        for name, fields in self.fields.items():
            data[name] = []
            if not fields[0].ignore:
                for field in fields:
                    data[name].append(field.value)
        return data

    def _is_this_form_submited(self, data):
        return self.form_name_value in data and \
            data[self.form_name_value] == [self.name, ]

    def _assign_field_value(self, name, value, index=None):
        if not name in self.fields:
            self.fields[name] = []
        if index is None:
            index = len(self.fields[name])
        try:
            field = self.fields[name][index]
        except IndexError:
            field = copy(self.field_patterns[name])
            self.fields[name].append(field)
        field.value = value

    def _assign_missing_values(self):
        field_names = []
        for name, value in self.field_patterns.items():
            if not value.ignore:
                field_names.append(name)

        for name in field_names:
            if name not in self.fields:
                self._assign_field_value(name, None)

    def _gather_forms_data(self, data):
        data = dict(data)
        data.pop(self.form_name_value, None)

        field_names = list(self.field_patterns)

        for name, value in data.items():
            if name in field_names:
                index = -1
                for small_value in value:
                    index += 1
                    self._assign_field_value(name, small_value, index)
            else:
                raise BadValue(name)

        self._assign_missing_values()

    def _validate_fields(self):
        def validate_fields():
            validation = True
            for name, fields in self.fields.items():
                if not fields[0].ignore:
                    for field in fields:
                        validation &= field.validate()
            return validation

        def validate_global_validators():
            try:
                for formValidator in self.formValidators:
                    formValidator()
            except FormValidationError as er:
                self.message = er.message
                self.error = True
                return False
            return True
        #----------------------------------------------------------------------
        validation = validate_fields()
        if validation:
            validation = validate_global_validators()
        return validation

    def _validate_and_submit(self):
        data = self.gather_data_from_fields()
        if self._validate_fields():
            if self.overal_validation(data):
                self.data = data
                self.submit(data)
                return True
            else:
                self.error = True
        return False

    def __call__(self, data, initial_data={}):
        self.fields = {}
        self._gather_forms_data(initial_data)
        if self._is_this_form_submited(data):
            self._gather_forms_data(data)
            return self._validate_and_submit()

    def update(self, obj, names=None, method='obj', ignore_missing=False):
        def getattr_obj(obj, name):
            return getattr(obj, name)

        def getattr_dict(obj, name):
            return obj[name]

        def getattr_obj_default_none(obj, name):
            return getattr(obj, name, None)

        def get_method(method):
            getattr_funs = {
                'obj': getattr_obj,
                'dict': getattr_dict,
                'obj_default_none': getattr_obj_default_none,
            }
            if type(method) == str:
                return getattr_funs[method]
            else:
                return method

        def make_names(names):
            if names is None:
                return list(self.field_patterns)
            else:
                return names

        def set_form_field(name, obj, get):
            if not self.field_patterns[name].ignore \
                    and self.field_patterns[name].value in [None, '']:
                data = get(obj, name)
                if name in self.fields:
                    self.fields[name][0].value = data
                else:
                    self._assign_field_value(name, data)

        get = get_method(method)
        names = make_names(names)
        if ignore_missing:
            for name in names:
                try:
                    set_form_field(name, obj, get)
                except (AttributeError, KeyError):
                    continue
        else:
            for name in names:
                set_form_field(name, obj, get)

    def overal_validation(self, data):
        return True  # pragma: no cover

    def create_form(self):
        pass  # pragma: no cover

    def submit(self, data):
        pass  # pragma: no cover

    def get_label(self, name):
        return self.field_patterns[name].label

    def get_error(self, name, index=0):
        if name in self.fields:
            fields = self.fields[name]
            if len(fields) > index:
                return fields[index].error
        return False

    def get_message(self, name, index=0):
        if name in self.fields:
            fields = self.fields[name]
            if len(fields) > index:
                return fields[index].message
        return None

    def get_value(self, name, index=0):
        if name in self.fields:
            fields = self.fields[name]
            if len(fields) > index:
                return fields[index].value
        return None
