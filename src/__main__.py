import builtins
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
from src.display import Display


def main():
    parse = Parser()
    parse.parsing()

    model = Small_LLM_Model()
    input_json = open_json(parse.input)
    valid_prompts = PromptsList(prompts=input_json).prompts

    valid_functions, function_format = format_function(parse.fnc_def)

    is_dir = parse.output.rfind("/")
    if is_dir != -1:
        directory = parse.output[:is_dir]
        if len(directory) > 0:
            Path(directory).mkdir(parents=True, exist_ok=True)

    vocab_path = model.get_path_to_vocab_file()
    vocab_json = open_json(model.get_path_to_vocab_file())
    vocab_pins = construct_vocab_pins(vocab_json)

    fsm = FSM(valid_functions, vocab_pins, vocab_json)
    fsm.build_state()

    super_prompt = (
        "<|im_start|>system\n"
        "You are a function-calling assistant.\n"
        "1. Pick the ONE function whose purpose matches the user's "
        "request. Ignore numbers/words that don't fit that purpose.\n"
        "2. Extract ONLY exact values explicitly present in the request "
        "for that function's parameters. Never invent, calculate, or "
        "guess.\n"
        "functions:"
        f"{valid_functions}"
        "<|im_end|>"
        "<|im_start|>user\n"
    )

    s_prompt_encoded: list[int] = model.encode(super_prompt)[0].tolist()
    
    Display()

    start: float = time.time()
    result = []
    
    for p in valid_prompts:
        fsm.current_state = 0
        output = ""
        pre_p = f"{p.prompt}<|im_end|>\n<|im_start|>assistant\n"

        p_encoded: list[int] = model.encode(pre_p)[0].tolist()
        full_prompt: list[int] = s_prompt_encoded + p_encoded

        while True:
            logits = model.get_logits_from_input_ids(full_prompt)
            allowed_tokens = fsm.allowed_token(fsm.current_state)
            if not allowed_tokens:
                break

            masked = fsm.mask_logits(logits, allowed_tokens)
            next_token = int(numpy.argmax(masked))

            full_prompt.append(next_token)
            decoded_token = model.decode([next_token])
            output += decoded_token
            builtins.print(decoded_token, end="", flush=True)
            fsm.transition(decoded_token)
            if fsm.current_state == -1:
                fsm.current_state = 0
                break

        print("\nAnswer:")
        up = p.prompt
        output = output.replace("\\", "\\\\")

        try:
            json_format = json.loads(output)
        except json.JSONDecodeError:
            print(f"[skip] malformed output for prompt: {p.prompt!r} -> {output!r}")
            continue
        
        json_format = {"prompt": up, **json_format}
        result.append(json_format)
        
        with open(parse.output, "w") as file:
            json.dump(result, file, indent=4)

    end: float = time.time()
    minutes = int((end - start) // 60)
    seconds = int((end - start) % 60)
    print(f'Call_Me_maybe took: {minutes}m/{seconds}s')


if __name__ == "__main__":
    main()
