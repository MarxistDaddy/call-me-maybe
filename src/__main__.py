import json
import time
from pathlib import Path
from typing import Any

from pydantic import ValidationError
from rich import print


from llm_sdk import Small_LLM_Model


from .parsing import Parser
from .prompt_validator import Prompts 

def main():
    parse = Parser()
    parse.parsing()

    #print(parse.fnc_def)
    #with open(parse.fnc_def) as f:
    #    f.read()
    #    print(f)
    #print(parse.input)
    #print(parse.output)
    #print(parse.model)

    model = Small_LLM_Model()
    
#    pro = f"""
#        You are a function-calling assistant.
#
#        You must select exactly one function from the list below
#        and return a valid JSON object describing the function call.
#
#        Available functions:
#        [
#  {
#    "name": "fn_add_numbers",
#    "description": "Add two numbers together and return their sum.",
#    "parameters": {
#      "a": {
#        "type": "number"
#      },
#      "b": {
#        "type": "number"
#      }
#    },
#    "returns": {
#      "type": "number"
#    }
#  },
#  {
#    "name": "fn_greet",
#    "description": "Generate a greeting message for a person by name.",
#    "parameters": {
#      "name": {
#        "type": "string"
#      }
#    },
#    "returns": {
#      "type": "string"
#    }
#  },
#  {
#    "name": "fn_reverse_string",
#    "description": "Reverse a string and return the reversed result.",
#    "parameters": {
#      "s": {
#        "type": "string"
#      }
#    },
#    "returns": {
#      "type": "string"
#    }
#  },
#  {
#    "name": "fn_get_square_root",
#    "description": "Calculate the square root of a number.",
#    "parameters": {
#      "a": {
#        "type": "number"
#      }
#    },
#    "returns": {
#      "type": "number"
#    }
#  },
#  {
#    "name": "fn_substitute_string_with_regex",
#    "description": "Replace all occurrences matching a regex pattern in a string.",
#    "parameters": {
#      "source_string": {
#        "type": "string"
#      },
#      "regex": {
#        "type": "string"
#      },
#      "replacement": {
#        "type": "string"
#      }
#    },
#    "returns": {
#      "type": "string"
#    }
#  }
#]%  
#
#        Rules:
#        - You must choose one function from the list.
#        - Do NOT return text.
#        - You must provide all required arguments.
#        - Argument types must match the specification.
#        - Do NOT return explanations.
#        - Return ONLY valid JSON.
#
#        The JSON format must be exactly:
#
#        {{
#        "fn_name": "<function_name>",
#        "arguments": {{
#            "<arg_name>": <value>
#        }}
#        }}
#
#        User request:
#        what is the sum of 40 and 2?
#    """
 
    pro = "what is the capital of france?"

    #print(lst)
    #print(type(lst))
    #print(lst.shape)
    #print(type(lst.shape))

    #logits = model.get_logits_from_input_ids(lst[0].tolist())
    #print(f"logits_size = {len(logits)}")
    #
    #print(modyyel.decode(logits.index(max(logits))))
    
    i = 0
    while(1):
        lst = model.encode(pro)
        logits = model.get_logits_from_input_ids(lst[0].tolist())
        res = model.decode(logits.index(max(logits)))
        print(res, end="")
        pro += res
        i += 1

    #print(f"--> {parse.input}")
    ##open and read the input file, then save it in the json_pr | we have a list
    #with open(parse.input) as f:    
    #    json_prompt = json.load(f) #--> json returns a list
    #    #print(json_prompt[0])

    #prompts_wrapper = Prompts(prompts=json_prompt)
    #prompts = prompts_wrapper.prompts
    ##print(prompts)    


    
    


if __name__ == "__main__":
    main()

