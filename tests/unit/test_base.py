from unittest import TestCase

from substra.commands import Api, Base


class UnFinished(Base):
    pass


class TestBase(TestCase):
    def test_create_command(self):
        unfinished = UnFinished({})
        try:
            unfinished.run()
        except Exception as e:
            self.assertTrue(str(e) == 'You must implement the run() method yourself!')


