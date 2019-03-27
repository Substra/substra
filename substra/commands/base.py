"""The base command."""


class Base(object):
    """A base command."""

    def __init__(self, options, *args, **kwargs):
        self.options = options
        self.args = args
        self.kwargs = kwargs

    def run(self):
        raise NotImplementedError('You must implement the run() method yourself!')

    def handle_exception(self, exception):
        verbose = self.options.get('--verbose', False)
        if verbose:
            raise exception
        print(str(exception))
