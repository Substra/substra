class Base(object):
    def __init__(self, options):
        self.options = options

    def run(self):
        raise NotImplementedError('You must implement the run() method yourself!')
