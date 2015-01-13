from formskit.translation import Translation
from formskit.tests.base import FormskitTestCase


class TranslationTests(FormskitTestCase):

    def test_casting(self):
        class InheritedTranslation(Translation):
            pass

        message = Translation()
        message.init('text', 'one', two='two')

        casted = InheritedTranslation(message)

        assert casted.text == 'text'
        assert casted.args == ('one',)
        assert casted.kwargs == {'two': 'two'}

    def test_normaln_translating(self):
        message = Translation()
        message.init('text {0} {two}', 'one', two='two')

        assert message() == 'text one two'

    def test_inherited_translation(self):
        class InheritedTranslation(Translation):

            def translate(self):
                return self.text + 'something'

        message = Translation()
        message.init('text {0} {two}', 'one', two='two')

        casted = InheritedTranslation(message)
        assert casted() == 'text one twosomething'
