class FakeConvert(object):

    def _set_field(self, field):
        self.field = field

    def __call__(self, value):
        return self.convert(value)

    def convert(self, value):
        return value


class ToInt(FakeConvert):

    def convert(self, value):
        return int(value)
