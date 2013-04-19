from formskit.errors import BadValue, ValueNotPresent
from formskit.formvalidators import FormValidationError

class Form(object):

    form_name_value = 'form_name'

    def __init__(self):
        self.fields = {}
        self.formValidators = []
        self.createForm()
        self.error = False
        self.message = None

    @property
    def name(self):
        return self.__class__.__name__

    def addField(self, field):
        self.fields[field.name] = field
        field.initForm(self)

    def addFormValidator(self, validator):
        validator.setForm(self)
        self.formValidators.append(validator)

    def gatherDataFromFields(self):
        data = {}
        for name, field in self.fields.items():
            if not field.ignore:
                data[name] = field.value
        return data

    def _isThisFormSubmited(self, data):
        return self.form_name_value in data and data[self.form_name_value] == self.name

    def _gatherFormsData(self, data):
        data = dict(data)
        data.pop(self.form_name_value)

        for name in self.fields:
            if not name in data and not self.fields[name].ignore:
                raise ValueNotPresent(name)

        for name, value in data.items():
            try:
                self.fields[name].value = value
            except KeyError:
                raise BadValue(name)

    def _validateFields(self):
        def validateFields():
            validation = True
            for name, field in self.fields.items():
                if not field.ignore:
                    validation &= field.validate()
            return validation
        def validateGlobalValidators():
            try:
                for formValidator in self.formValidators:
                    formValidator()
            except FormValidationError, er:
                self.message = er.message
                self.error = True
                return False
            return True
        #-----------------------------------------------------------------------
        validation = validateFields()
        if validation:
            validation = validateGlobalValidators()
        return validation

    def _validate_and_submit(self):
        if self._validateFields():
            data = self.gatherDataFromFields()
            if self.overalValidation(data):
                self.submit(data)
                return True
            else:
                self.error = True
        return False

    def __call__(self, data):
        if self._isThisFormSubmited(data):
            self._gatherFormsData(data)
            return self._validate_and_submit()

    def __getitem__(self, name):
        return self.fields[name]

    def overalValidation(self, data):
        return True

    def createForm(self):
        pass

    def submit(self, data):
        pass
