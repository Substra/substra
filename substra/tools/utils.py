import importlib
import importlib.util
import inspect
import logging
import os
import sys
import time

from substratools import exceptions

logger = logging.getLogger(__name__)

MAPPING_LOG_LEVEL = {
    "debug": logging.DEBUG,
    "info": logging.INFO,
    "warning": logging.WARNING,
    "error": logging.ERROR,
    "critical": logging.CRITICAL,
}


def configure_logging(path=None, log_level="info"):
    level = MAPPING_LOG_LEVEL[log_level]

    formatter = logging.Formatter(fmt="%(asctime)s %(levelname)-6s %(name)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S")

    h = logging.StreamHandler()
    h.setLevel(level)
    h.setFormatter(formatter)

    root = logging.getLogger("substratools")
    root.setLevel(level)
    root.addHandler(h)

    if path and level == logging.DEBUG:
        fh = logging.FileHandler(path)
        fh.setLevel(level)
        fh.setFormatter(formatter)

        root.addHandler(h)


def get_logger(name, path=None, log_level="info"):
    new_logger = logging.getLogger(f"substratools.{name}")
    configure_logging(path, log_level)
    return new_logger


class Timer(object):
    """This decorator prints the execution time for the decorated function."""

    def __init__(self, module_logger):
        self.module_logger = module_logger

    def __call__(self, func):
        def wrapper(*args, **kwargs):
            start = time.time()
            result = func(*args, **kwargs)
            end = time.time()
            self.module_logger.info("{} ran in {}s".format(func.__qualname__, round(end - start, 2)))
            return result

        return wrapper


def import_module(module_name, code):
    if module_name in sys.modules:
        logging.warning("Module {} will be overwritten".format(module_name))
    spec = importlib.util.spec_from_loader(module_name, loader=None, origin=module_name)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    exec(code, module.__dict__)


def import_module_from_path(path, module_name):
    assert os.path.exists(path), "path '{}' not found".format(path)
    spec = importlib.util.spec_from_file_location(module_name, path)
    assert spec, "could not load spec from path '{}'".format(path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# TODO: 'load_interface_from_module' is too complex, consider refactoring
def load_interface_from_module(module_name, interface_class, interface_signature=None, path=None):  # noqa: C901
    if path:
        module = import_module_from_path(path, module_name)
        logger.info(f"Module '{module_name}' loaded from path '{path}'")
    else:
        try:
            module = importlib.import_module(module_name)
            logger.info(f"Module '{module_name}' imported dynamically; module={module}")
        except ImportError:
            # XXX don't use ModuleNotFoundError for python3.5 compatibility
            raise

    # check if module empty
    if not inspect.getmembers(module, lambda m: inspect.isclass(m) or inspect.isfunction(m)):
        raise exceptions.EmptyInterfaceError(
            f"Module '{module_name}' seems empty: no method/class found in members: '{dir(module)}'"
        )

    # find interface class
    for _, obj in inspect.getmembers(module, inspect.isclass):
        if issubclass(obj, interface_class):
            return obj()  # return interface instance

    # backward compatibility; accept methods at module level directly
    if interface_signature is None:
        class_name = interface_class.__name__
        elements = str(dir(module))
        logger.info(f"Class '{class_name}' not found from: '{elements}'")
        raise exceptions.InvalidInterfaceError("Expecting {} subclass in {}".format(class_name, module_name))

    missing_functions = interface_signature.copy()
    for name, obj in inspect.getmembers(module):
        if not inspect.isfunction(obj):
            continue
        try:
            missing_functions.remove(name)
        except KeyError:
            pass

    if missing_functions:
        message = "Method(s) {} not implemented".format(", ".join(["'{}'".format(m) for m in missing_functions]))
        raise exceptions.InvalidInterfaceError(message)
    return module
