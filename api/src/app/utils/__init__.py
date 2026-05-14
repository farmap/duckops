from distutils.util import strtobool
import uuid


def process_boolean_str(value):
    if type(value) is bool:
        return value

    if value is None:
        return False

    if value == "":
        return None

    return bool(strtobool(value))


def generate_uuid4(short=False):

    if short:
        # this doesn't guarantee uniqueness.
        # we will check in revision records anyway to see if ID unique, if not regenerate
        # Might reduce uniqueness because of slicing
        return uuid.uuid4().hex[:8]
    return uuid.uuid4()
