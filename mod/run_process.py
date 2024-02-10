import logging
import pkgutil
import multiprocessing


logger = logging.getLogger(__name__)

def load(package_name):
    package = __import__(package_name, fromlist=[''])
    sub_modules = []

    for loader, module_name, is_pkg in pkgutil.walk_packages(package.__path__):
        if not is_pkg:
            sub_module = __import__(f"{package_name}.{module_name}", fromlist=[''])
            sub_modules.append(sub_module)

    return sub_modules


def run():
    modules = load('process')
    for module in modules:
        if hasattr(module, 'main'):
            p = multiprocessing.Process(target=module.main)
            p.start()
        else:
            logger.warning(f"The module {module.__name__} does not have a main method.")
