from copy import copy

from formskit.errors import BadValue, ValueNotPresent
from formskit.formvalidators import FormValidationError


class Form(object):

    form_name_value = 'form_name'

    def __init__(self):
        self.fields = {}
        self.fieldLists = {}
        self.fieldLists_copyfields = {}
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

    def addFieldList(self, field):
        self.fieldLists_copyfields[field.name] = field
        field.initForm(self)

    def addFormValidator(self, validator):
        validator.setForm(self)
        self.formValidators.append(validator)

    def gatherDataFromFields(self):
        data = {}
        for name, field in self.fields.items():
            if not field.ignore:
                data[name] = field.value
        for name in self.fieldLists_copyfields:
            data[name] = []
            for field in self.fieldLists[name]:
                data[name].append(field.value)
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
            if name in list(self.fields):
                self.fields[name].value = value
            elif name in list(self.fieldLists_copyfields):
                self.fieldLists[name] = []
                for small_value in value:
                    field = copy(self.fieldLists_copyfields[name])
                    self.fieldLists[name].append(field)
                    field.value = small_value
            else:
                raise BadValue(name)

    def _validateFields(self):
        def validateFields():
            validation = True
            for name, field in self.fields.items():
                if not field.ignore:
                    validation &= field.validate()
            for name, fields in self.fieldLists.items():
                for field in fields:
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
        #----------------------------------------------------------------------
        validation = validateFields()
        if validation:
            validation = validateGlobalValidators()
        return validation

    def _validate_and_submit(self):
        data = self.gatherDataFromFields()
        if self._validateFields():
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
        if name in self.fields:
            return self.fields[name]
        elif name in self.fieldLists:
            return self.fieldLists[name]
        else:
            return self.fieldLists_copyfields[name]

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
            if type(method) in [str, unicode]:
                return getattr_funs[method]
            else:
                return method

        def make_names(names):
            if names is None:
                return self.fields.keys()
            else:
                return names

        def set_form_field(name, obj, get):
            if not self[name].ignore and self[name].value in [None, '']:
                self[name].value = get(obj, name)

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

    def overalValidation(self, data):
        return True  # pragma: no cover

    def createForm(self):
        pass  # pragma: no cover

    def submit(self, data):
        pass  # pragma: no cover
