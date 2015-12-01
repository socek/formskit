from datetime import datetime


class FakeConvert(object):

    """Default convertor which does nothing."""

    def _set_field(self, field):
        self.field = field

    def __call__(self, value):
        return self.convert(value)

    def convert(self, value):
        return value

    def convert_back(self, value):
        return value

    def back(self, value):
        return self.convert_back(value)


class ToInt(FakeConvert):

    """Converts to int."""

    def convert(self, value):
        try:
            return int(value)
        except (ValueError, TypeError):
            return None

    def convert_back(self, value):
        if value is None:
            return None
        else:
            return str(value)


class ToDatetime(FakeConvert):

    """Converts to datetime."""
    format = '%Y-%m-%d'

    def convert(self, value):
        try:
            return datetime.strptime(value, self.format)
        except (ValueError, TypeError):
            return None

    def convert_back(self, value):
        if value:
            return value.strftime(self.format)
        else:
            return None


class ToBool(FakeConvert):

    def convert(self, value):
        try:
            return bool(value.strip())
        except (ValueError, TypeError):
            return False

    def convert_back(self, value):
        if value:
            return '1'
        else:
            return ''
