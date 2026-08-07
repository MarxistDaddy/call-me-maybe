Call Me Maybe

This project has been created as part of the 42 curriculum by hamaarab.

Description

Call Me Maybe is an introduction to function calling and structured text generation in Large Language Models (LLMs). The primary objective is to build an execution pipeline that translates natural language requests into precise, typed function calls formatted as valid JSON.

Small models (such as Qwen/Qwen3-0.6B) often fail to maintain proper JSON syntax or schema alignment when relying purely on prompt engineering. To solve this, this project implements a constrained decoding engine from scratch using a Finite State Machine (FSM). By dynamically masking model logits at every step of generation, the system guarantees 100% syntactically and semantically valid JSON outputs without relying on high-level orchestration libraries.

Instructions
Prerequisites
Python 3.10 or higher
uv package manager
Installation

Clone the repository and synchronize the environment dependencies:

bash
uv sync
Execution

Run the default pipeline reading from data/input/ and writing to data/output/:

bash
uv run python -m src

Or specify custom paths explicitly:

bash
uv run python -m src \
  --functions_definition data/input/functions_definition.json \
  --input data/input/function_calling_tests.json \
  --output data/output/function_calling_results.json
Algorithm Explanation

The core mechanism relies on token-level logit masking via a Finite State Machine (FSM).

┌─────────────────┐      ┌──────────────────┐      ┌─────────────────┐      ┌──────────────────┐
│ Prompt Input    │ ───► │ LLM Forward Pass │ ───► │ Raw Logits      │ ───► │  FSM State Check │
└─────────────────┘      └──────────────────┘      └─────────────────┘      └─────────┬────────┘
                                                                                      │
┌─────────────────┐      ┌──────────────────┐      ┌─────────────────┐                │
│ Append Token    │ ◄─── │ Token Selection  │ ◄─── │ Masked Logits   │ ◄──────────────┘
│ & Update FSM    │      │ (Greedy / Argmax)│      │ (-inf on Error) │
└─────────────────┘      └──────────────────┘      └─────────────────┘
State Tracking: An internal FSM maintains the active context of the output structure (e.g., START_OBJECT, EXPECT_KEY_PROMPT, EXPECT_FUNCTION_NAME, EXPECT_PARAMETER_VALUE, END_OBJECT).
Schema Mapping: Function definitions loaded from functions_definition.json define the permissible state transitions (e.g., allowed parameter names, allowed numeric digits vs. string quotes).
Logit Interception: At step 
𝑡
t, get_logits_from_input_ids() yields raw logits over the entire vocabulary.
Masking: The engine iterates over candidate tokens. Any token string that violates the current state's valid transitions has its logit set to 
−
∞
−∞.
Selection: The next token is chosen strictly from valid candidates, ensuring every token maintains syntactic validity and schema compliance.
Testing Strategy
Type Safety & Style: Enforced strict type annotations validated with mypy and compliant with flake8.
Unit Testing: Verified state transitions and logit masking against edge cases using pytest (e.g., nested special characters, empty parameters, trailing whitespace).
Schema Robustness: Tested against custom function definition sets with complex multi-parameter configurations.
Example Usage

Input (function_calling_tests.json):

json
[
  { "prompt": "What is the sum of 40 and 2?" }
]

Function definitions (functions_definition.json):

json
[
  {
    "name": "fn_add_numbers",
    "description": "Add two numbers together.",
    "parameters": {
      "a": { "type": "number" },
      "b": { "type": "number" }
    },
    "returns": { "type": "number" }
  }
]
