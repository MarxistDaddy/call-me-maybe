import json
import time
from pathlib import Path
from typing import Any

from pydantic import ValidationError
from rich import print
import numpy

from llm_sdk import Small_LLM_Model

from .parsing import Parser
from .validate import PromptsList, FncDefs
from src.fsm import FSM

from src.utils import open_json, format_function, construct_vocab_pins


def main():
    parse = Parser()
    parse.parsing()
    
    model = Small_LLM_Model()

    input_json = open_json(parse.input)
    valid_prompts = PromptsList(prompts=input_json).prompts
    
    valid_functions, function_format = format_function(parse.fnc_def)
    #print(valid_functions, function_format)

    is_dir = parse.output.rfind("/")
    if is_dir != -1:
        directory = parse.output[:is_dir]
        if len(directory) > 0:
            Path(directory).mkdir(parents=True, exist_ok=True)

    vocab_path = model.get_path_to_vocab_file()
    print(vocab_path)
    vocab_json = open_json(model.get_path_to_vocab_file())
    vocab_pins = construct_vocab_pins(vocab_json)
    

    
    print(valid_functions)
    fsm = FSM(valid_functions, vocab_pins, vocab_json)
    print(fsm.functions[0], fsm.vocab_pins['x'], fsm.all_vocab['porn'])
    fsm.build_state()    
    
    super_prompt = (
        "<|im_start|>system\n"
        "You are a strict data extraction assistant. Your ONLY job "
        "is to extract the exact values from the user's request to "
        "pass as parameters.\n"
        "Rules:\n"
        "1. Extract ONLY the numbers or strings explicitly present in the "
        "text.\n"
        "2. DO NOT invent, calculate, or guess any missing values.\n"
        "3. DO NOT use placeholder numbers.\n Map the exact digits found in "
        "the prompt to the required parameter.\n"
        "functions definition:"
        f"{valid_functions}"
        "<|im_end|>"
        "<|im_start|>user\n"
    )

    s_prompt_encoded: list[int] = model.encode(super_prompt)[0].tolist()
    
    start: float = time.time()
    result = []
    
    print("params length:   ", len(valid_prompts))
    for p in valid_prompts:
        fsm.current_state = 0 #--> IDK

        output = ""
        pre_p = f"{p.prompt}<|im_end|>\n<|im_start|>assistant\n"
        
        p_encoded: list[int] = model.encode(pre_p)[0].tolist()
        full_prompt: list[int] = s_prompt_encoded + p_encoded
        #print("prompt:", p.prompt)

        logits: list[float] = model.get_logits_from_input_ids(full_prompt)
        best_token_id = max(range(len(logits)), key=lambda i: logits[i])
        decoded_text = model.decode([best_token_id])
        
        #print(f"Index {best_token_id} maps to text: {decoded_text!r}")
        
        print(model.decode([best_token_id]))


        while True:
            logits = model.get_logits_from_input_ids(full_prompt)
            allowed_tokens = fsm.allowed_token(fsm.current_state)
            masked = fsm.mask_logits(logits, allowed_tokens)
            next_token = int(numpy.argmax(masked)) #get the arg_max
            
            full_prompt.append(next_token) #check this later

            decoded_token = model.decode([next_token])
            output += decoded_token
            fsm.transition(decoded_token)
            if fsm.current_state == -1:
                fsm.current_state = 0
                break

        print("Answer:")
        up = p.prompt
        idx = output.find("\\")
        if idx != -1 and output[idx + 1] != "\\":
            output = output.replace("\\", "\\\\")
        json_format = json.loads(output)
        json_format = {"prompt": up, **json_format}
        print(
            json.dumps(json_format, indent=4, ensure_ascii=False), end="\n\n"
        )
        result.append(json_format)

    with open(parse.output, "w") as file:
        json.dump(result, file, indent=4)


    end: float = time.time()
    minutes = int((end - start) // 60)
    seconds = int((end - start) % 60)
    
    print(f"Call_Me_maybe took: {minutes}m/{seconds}s")

if __name__ == "__main__":
    main()












