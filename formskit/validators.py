# encoding: utf8
import re
from decimal import Decimal, InvalidOperation


class FieldValidator(object):

    _type = 'field'

    def __init__(self):
        self.message = self.__class__.__name__

    def init_field(self, field):
        self.field = field

    def set_error(self):
        self.field.set_error(self.message)

    def make(self):
        result = self.validate()
        if result is False:
            self.set_error()


class FieldValueValidator(FieldValidator):

    _type = 'value'

    def set_error(self):
        self.field_value.set_error(self.message)

    def make(self, field_value):
        self.field_value = field_value
        self.value = field_value.value
        super().make()


class NeedToHaveValue(FieldValidator):

    def validate(self):
        return len(self.field.values) > 0


class NotEmpty(FieldValueValidator):

    def validate(self):
        if self.value is None:
            return False
        elif type(self.value) == str and self.value.strip() == '':
            return False
        elif type(self.value) == bytes and self.value.strip() == b'':
            return False
        elif type(self.value) in [list, dict, tuple] and len(self.value) == 0:
            return False
        return True


class IsDigit(FieldValueValidator):

    regex = re.compile('^-{0,1}[0-9]+$')

    def validate(self):
        return re.search(self.regex, self.value) is not None


class IsDecimal(FieldValueValidator):

    def validate(self):
        try:
            Decimal(self.value)
            return True
        except InvalidOperation:
            return False


class Email(FieldValueValidator):

    regex = re.compile(
        "^.+\\@(\\[?)[a-zA-Z0-9\\-\\.]+\\.([a-zA-Z]{2,3}|[0-9]{1,3})(\\]?)$")

    def validate(self):
        if len(self.value) > 7:
            return re.match(self.regex, self.value) is not None
        return False
