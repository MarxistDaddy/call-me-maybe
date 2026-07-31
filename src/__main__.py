import json
import time
from pathlib import Path
from typing import Any

from pydantic import ValidationError
from rich import print

from llm_sdk import Small_LLM_Model

from .parsing import Parser
from .validate import PromptsList, FncDefs
from .fsm import FSM


def main():
    parse = Parser()
    parse.parsing()

    #print("--> ", parse.fnc_def)
    #print(parse.input)
    #print(parse.output)
    #print(parse.model)
    
    #with open(parse.fnc_def) as f:
    #    f.read()
    #    print(f)
    #print(parse.input)
    #print(parse.output)
    #print(parse.model)

    model = Small_LLM_Model()

    #i = 0
    #while i < 10:
    #    lst = model.encode(pro)
    #    logits = model.get_logits_from_input_ids(lst[0].tolist())
    #    res = model.decode(logits.index(max(logits)))
    #    print(res, end="")
    #    pro += res
    #    i += 1


    print(f"--> calling's path: '{parse.input}")
    #open and read the input file, then save it in the json_pr | we have a list
    with open(parse.input) as f:    
        input_json = json.load(f) #--> json returns a list
        #print(input_json)

    prompts = PromptsList(prompts=input_json).prompts
    #print(prompts)

    #print(f"--> calling's path: '{parse.fnc_def}")
    with open(parse.fnc_def) as f:
        f_json = json.load(f)
        #print(f_json)
   
    functions = FncDefs(functions_def=f_json).functions_def
    print(functions)

    functions_format = "\n".join(
        f"{func.name}({', '.join(f'{k}: {v.type}' for k, v in func.parameters.items())})-{func.description}"
    for func in functions
        )

    #print(functions_format)

    super_prompt = """
        <|im_start|>system
        You are a strict data extraction assistant. Your ONLY task is to extract exact parameter values from the user's input and map them to a valid function signature.
        
        Available Functions:
        {functions_format}
        
        STRICT OPERATIONAL RULES:
        1. EXPLICIT MATCHING: Extract ONLY numbers, strings, or booleans explicitly written in the user's text.
        2. NO HALLUCINATIONS: Do NOT invent, calculate, convert, or infer missing values.
        3. NO PLACEHOLDERS: Do NOT use default or placeholder values.
        4. EXACT MAP: Map raw literal values directly from the user prompt into parameter slots.
        <|im_end|>
        <|im_start|>user
        {user_prompt}<|im_end|>
        <|im_start|>assistant
    """

    vocab = model.get_path_to_vocab_file()
    #print(vocab)
    with open(vocab) as f:
        vocab_dict = json.load(f)
        #print(vocab_dict)
        #print("=============")

    #id_ = vocab_dict["fn_add_numbers"]
    #print(id_)
    #print(model.decode(id_))

    def return_pins(v):
        vocab_pins = {}
        for key in v:
            vocab_pins.setdefault(key[0], {}).update({key: v[key]})
            
        #print(vocab_pins["p"])

    return_pins(vocab_dict)
    
    fsm = FSM(functions)
    fsm.build_state()    
     
    
    
if __name__ == "__main__":
    main()

