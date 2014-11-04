from unittest import TestCase


class FormskitTestCase(TestCase):

    def assertNone(self, obj):
        return self.assertEqual(None, obj)
