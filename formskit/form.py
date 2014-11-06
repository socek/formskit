from .field import Field


class Form(object):

    form_name_value = 'form_name'

    @property
    def name(self):
        return self.__class__.__name__

    def __init__(self):
        self.fields = {}
        self.form_validators = []
        self.raw_data = None
        self.create_form()
        self.reset()

    def add_field_object(self, field):
        self.fields[field.name] = field
        field.init_form(self)

    def add_field(self, *args, **kwargs):
        self.add_field_object(Field(*args, **kwargs))

    def __call__(self, raw_data):
        self._reset()
        if self._is_form_submitted(raw_data):
            self._parse_raw_data(raw_data)
            if self._validate():
                self.submit()
        else:
            return None

    def _is_form_submitted(self, raw_data):
        return (
            self.form_name_value in raw_data
            and raw_data[self.form_name_value] == [self.name, ]
        )

    def _parse_raw_data(self, raw_data):
        for name, values in raw_data.items():
            field = self.fields[name]
            field.set_values(values)

    def reset(self):
        self.success = None
        for field in self.fields.values():
            field.reset()

    def _validate(self):
        return (
            self._validate_fields()
            # TODO: implement form validators
            # and self._validate_form_validators()
            and self._validate_form()
        )

    def _validate_form(self):
        return True

    def _validate_fields(self):
        success = True
        for field in self.fields.values():
            success &= field.validate()
        return success

    def create_form(self):
        pass

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
    #     #---------------------------------------------------
    #     validation = validateFields()
    #     if validation:
    #         validation = validateGlobalValidators()
    #     return validation
