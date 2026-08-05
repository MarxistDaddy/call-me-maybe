import json
from typing import Any
from .validate import FncDefs

def open_json(file: str) -> list[Any]:
    with open(file) as f:
        return json.load(f)


def format_function(fnc_path):
    
    fnc_json = open_json(fnc_path)
    functions = FncDefs(functions_def=fnc_json).functions_def

    function_format =  "\n".join(
        f"{func.name}({', '.join(f'{k}: {v.type}' for k, v in func.parameters.items())})- {func.description}"
    for func in functions
        )

    return (functions, function_format)

def construct_vocab_pins(vocab_json):
    vocab_pins = {}
    for key in vocab_json:
        vocab_pins.setdefault(key[0], {}).update({key: vocab_json[key]})
    
    return vocab_pins
