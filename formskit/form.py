from base64 import urlsafe_b64decode
from copy import deepcopy
from json import loads
import binascii

from .field import Field


class Form(object):

    form_name_value = 'form_name'

    def get_name(self):
        return self.__class__.__name__

    def __init__(self):
        self.fields = {}
        self.form_validators = []
        self.raw_data = None
        self.parent = None
        self.childs = {}
        self.create_form()
        self.reset()
        self.index = None

    def add_field_object(self, field):
        self.fields[field.name] = field
        field.init_form(self)

    def add_field(self, *args, **kwargs):
        field = Field(*args, **kwargs)
        self.add_field_object(field)
        return field

    def __call__(self, raw_data):
        self.reset()
        if self._is_form_submitted(raw_data):
            self._parse_raw_data(raw_data)
            if self._validate():
                self.submit()
        else:
            return None

    def _is_form_submitted(self, raw_data):
        return (
            self.form_name_value in raw_data
            and raw_data[self.form_name_value] == [self.get_name(), ]
        )

    def _parse_raw_data(self, raw_data):
        for name, values in raw_data.items():
            if name == self.form_name_value:
                continue

            field = self._get_field(name)
            field.set_values(values)

    def _get_field(self, name):
        data = self._decode_name(name)
        name = data['name']

        form = self._get_sub_form(data['parents'][1:])
        return form.fields[name]

    def _decode_name(self, name):
        try:
            json = urlsafe_b64decode(name).decode('utf8')
            return loads(json)
        except binascii.Error:
            raise WrongValueName(name)

    def _get_sub_form(self, parents):
        if parents == []:
            return self
        form_name = parents[0]['name']
        index = parents[0]['index']
        sub_form = self.get_or_create_sub_form(form_name, index)
        return sub_form._get_sub_form(parents[1:])

    def reset(self):
        self.success = None
        for field in self.fields.values():
            field.reset()
        for name in self.childs:
            self.childs[name] = {0: self.childs[name][0]}
            self.childs[name][0].reset()

    def _validate(self):
        self.success = (
            self._validate_fields()
            # TODO: implement form validators
            # and self._validate_form_validators()
            and self._validate_form()
            and self._validate_sub_forms()
        )
        return self.success

    def _validate_form(self):
        return True

    def _validate_fields(self):
        success = True
        for field in self.fields.values():
            success &= field.validate()
        return success

    def _validate_sub_forms(self):
        success = True
        for sub_forms in self.childs.values():
            for sub_form in sub_forms.values():
                success &= sub_form._validate_fields()
        return success

    def create_form(self):
        pass

    def _get_parents(self):
        if self.parent is None:
            return [self._get_form_info()]
        else:
            parents = self.parent._get_parents()
            parents.append(self._get_form_info())
            return parents

    def _get_form_info(self):
        return {
            'name': self.get_name(),
            'index': self.index}

    def add_sub_form(self, form):
        form._set_parent(self, 0)
        self.childs[form.get_name()] = {0: form}

    def _set_parent(self, parent, index):
        self.parent = parent
        self.index = index

    def get_or_create_sub_form(self, name, index):
        try:
            return self.get_sub_form(name, index)
        except KeyError:
            form = self._clone_sub_form(name)
            self.childs[name][index] = form
            form.index = index
            return form

    def get_sub_form(self, name, index):
        return self.childs[name][index]

    def _clone_sub_form(self, name):
        form = self.childs[name][0]
        return deepcopy(form)

    # TODO: implement form validators

    # def add_form_validator(self, validator):
    #     validator.set_form(self)
    #     self.form_validators.append(validator)

    # def _validateFields(self):
    #     def validateFields():
    #         validation = True
    #         for name, fields in self.fields.items():
    #             if not fields[0].ignore:
    #                 for field in fields:
    #                     validation &= field.validate()
    #         return validation

    #     def validateGlobalValidators():
    #         try:
    #             for formValidator in self.formValidators:
    #                 formValidator()
    #         except FormValidationError as er:
    #             self.message = er.message
    #             self.error = True
    #             return False
    #         return True
    # ---------------------------------------------------
    #     validation = validateFields()
    #     if validation:
    #         validation = validateGlobalValidators()
    #     return validation


class WrongValueName(Exception):

    def __init__(self, name):
        self.name = name
