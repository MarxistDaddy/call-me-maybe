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

MAX_STEPS = 512  # safety cap so a desynced FSM can't loop forever


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
    print(vocab_path)
    vocab_json = open_json(model.get_path_to_vocab_file())
    vocab_pins = construct_vocab_pins(vocab_json)

    print(valid_functions)
    fsm = FSM(valid_functions, vocab_pins, vocab_json)
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
        fsm.current_state = 0
        output = ""
        pre_p = f"{p.prompt}<|im_end|>\n<|im_start|>assistant\n"

        p_encoded: list[int] = model.encode(pre_p)[0].tolist()
        full_prompt: list[int] = s_prompt_encoded + p_encoded

        print(f"Prompt: {p.prompt!r}")
        print("Generating: ", end="", flush=True)

        steps = 0
        while True:
            steps += 1
            if steps > MAX_STEPS:
                print(
                    f"\n[warn] hit MAX_STEPS for prompt: {p.prompt!r}, "
                    f"partial output: {output!r}"
                )
                break

            logits = model.get_logits_from_input_ids(full_prompt)
            allowed_tokens = fsm.allowed_token(fsm.current_state)

            # An empty allowed_tokens list means the FSM has no legal move
            # from the current state - every following step will decode
            # against an all -inf logit vector and argmax will just return
            # index 0 every time. That's the "looks infinite" case: it isn't
            # actually looping, it's stuck. Surface it immediately instead
            # of silently grinding to MAX_STEPS.
            if not allowed_tokens:
                print(
                    f"\n[warn] no allowed tokens at state {fsm.current_state} "
                    f"(step {steps}) - FSM is stuck, breaking early. "
                    f"partial output: {output!r}"
                )
                break

            masked = fsm.mask_logits(logits, allowed_tokens)
            next_token = int(numpy.argmax(masked))

            full_prompt.append(next_token)
            decoded_token = model.decode([next_token])
            output += decoded_token

            # Requirement: print output as it is generated, token by token.
            # Uses builtins.print (not rich's) so characters like '[' in a
            # decoded token aren't misread as rich markup.
            builtins.print(decoded_token, end="", flush=True)

            fsm.transition(decoded_token)
            if fsm.current_state == -1:
                fsm.current_state = 0
                break

        print()  # close the streamed line before the summary
        print("Answer:")
        up = p.prompt

        # Always normalize backslashes before parsing, rather than trying to
        # guess from the first occurrence whether escaping is needed - that
        # approach breaks on IndexError (trailing backslash) and on mixed
        # escaped/unescaped sequences.
        output = output.replace("\\", "\\\\")

        try:
            json_format = json.loads(output)
        except json.JSONDecodeError:
            print(f"[skip] malformed output for prompt: {p.prompt!r} -> {output!r}")
            continue

        json_format = {"prompt": up, **json_format}
        print(
            json.dumps(json_format, indent=4, ensure_ascii=False), end="\n\n"
        )
        result.append(json_format)

        # Write incrementally so a crash mid-run doesn't lose everything
        # gathered so far.
        with open(parse.output, "w") as file:
            json.dump(result, file, indent=4)

    end: float = time.time()
    minutes = int((end - start) // 60)
    seconds = int((end - start) % 60)

    print(f"Call_Me_maybe took: {minutes}m/{seconds}s")


if __name__ == "__main__":
    main()
