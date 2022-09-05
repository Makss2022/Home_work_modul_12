from typing import Callable


def input_error(func: Callable):
    def inner(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
            return result
        except ValueError:
            return "Give me the correct phone, please! (no spaces and 10 or 12 digits in the phone number)"
        except KeyError:
            return "Contact  does not exist in the contact book!"
        except IndexError:
            return "Give me name and phone please!"
        except AttributeError:
            return "Сommand entered incorrectly!"
    return inner
