# Annotated: attaches metadata to a type; get_type_hints: reads the hints of a function
from typing import Annotated, get_type_hints


class FromProvider:
    """Stands for Depends: remembers which function provides the value."""

    def __init__(self, provider):
        print("2. FromProvider created, stores the function (not called)")
        self.provider = provider


def provide_word():
    print("5. provide_word called")
    return "hello"


print("1. defining endpoint")


def endpoint(word: Annotated[str, FromProvider(provide_word)]):
    print("7. endpoint runs, word =", word)
    return f"endpoint got: {word}"


def call_like_a_framework(function):
    """Read the hints, call providers, then call the function."""
    print("3. call_like_a_framework starts, endpoint is only read")
    arguments = {}
    hints = get_type_hints(function, include_extras=True)
    print(f"this is hints: {hints}, and {type(hints)}\n")
    for name, hint in hints.items():
        print(f"this is name:{name}, and hint: {hint}\n")
        for item in getattr(hint, "__metadata__", ()):
            print(f"this is item:{item}\n")
            if isinstance(item, FromProvider):
                print("4. found FromProvider for parameter:", name)
                arguments[name] = item.provider()
                print("6. provider result stored:", arguments[name])
    return function(**arguments)


print("result:", call_like_a_framework(endpoint))
