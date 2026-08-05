from typing import Any


class FSM:
    def __init__(self,
            fncs: list[Any],
            vocab_pins: dict[str, dict[str, int]],
            all_vocab: dict[str, int]
        ) -> None:
        self.state: int = 0
        self.prefix_tree: dict[int, dict[str | None, int]] = {}
        self.functions = fncs
        self.vocab_pins = vocab_pins
        self.all_vocab = all_vocab
        self.saved_state: int = 0
        self.current_state: int = 0
        self.cache: dict[int, list[int]] = {}

    def tr_token(self, string: str) -> str:
        """Converts spaces to 'Ġ' tokens for tokenizer compatibility."""
        return string.replace(" ", "Ġ")

    def build_state(self) -> None:
        start = self.tr_token('{"name": "')
        params = self.tr_token('", "parameters": {')

        # 1. Build common JSON opening prefix: {"name": "
        for c in start:
            self.prefix_tree.setdefault(self.state, {})[c] = self.state + 1
            self.state += 1

        self.saved_state = self.state

        # 2. Process each function schema definition
        for fnc in self.functions:
            curr_fnc_state = self.saved_state

            # Build shared prefix tree for function names
            for c in self.tr_token(fnc.name):
                if c in self.prefix_tree.get(curr_fnc_state, {}):
                    curr_fnc_state = self.prefix_tree[curr_fnc_state][c]
                else:
                    next_state = self.state + 1
                    self.prefix_tree.setdefault(curr_fnc_state, {})[c] = next_state
                    self.state = next_state
                    curr_fnc_state = self.state

            # Build shared parameter opening prefix: ", "parameters": {
            for c in params:
                if c in self.prefix_tree.get(curr_fnc_state, {}):
                    curr_fnc_state = self.prefix_tree[curr_fnc_state][c]
                else:
                    next_state = self.state + 1
                    self.prefix_tree.setdefault(curr_fnc_state, {})[c] = next_state
                    self.state = next_state
                    curr_fnc_state = self.state

            num_params = len(fnc.parameters)

            for index, (key, param_obj) in enumerate(fnc.parameters.items(), 1):
                prefix = f' "{key}": ' if index > 1 else f'"{key}": '

                for c in self.tr_token(prefix):
                    if c in self.prefix_tree.get(curr_fnc_state, {}):
                        curr_fnc_state = self.prefix_tree[curr_fnc_state][c]
                    else:
                        next_state = self.state + 1
                        self.prefix_tree.setdefault(curr_fnc_state, {})[c] = next_state
                        self.state = next_state
                        curr_fnc_state = self.state

                exit_states = self.build_type_state(param_obj)
                
                if index == num_params:
                    self.prefix_tree.setdefault(self.state, {}).update(
                        {"}", self.state + 1}
                    )
                    self.state += 1
                    self.prefix_tree.update({self.state: {"}", -1}})
                    break
                else:
                    self.prefix_tree.setdefault(self.state, {}).update(
                        {",": self.state + 1}
                    )
                    self.state += 1
                    self.prefix_tree.update({self.state: {"Ġ": self.state += 1}})
                    self.state += 1



        # Print full transition matrix
        #for k in sorted(self.prefix_tree.keys()):
        #    print(f"{k}: {self.prefix_tree[k]}")

    def build_type_state(self, param_obj: Any) -> list[int]:
        if hasattr(param_obj, "type"):
            param_type = param_obj.type
        elif isinstance(param_obj, dict):
            param_type = param_obj.get("type", "string")
        else:
            param_type = "string"

        if param_type == "integer":
            return self.build_int_state()
        elif param_type == "number":
            return self.build_number_state()
        else:
            return self.build_string_state()

    def build_string_state(self) -> list[int]:
        entry_s = self.state

        # State -> opening quote
        self.prefix_tree.setdefault(entry_s, {})['"'] = entry_s + 1
        self.state += 1

        # State -> loop on contents (None wildcard) and exit on terminating quote
        self.prefix_tree.setdefault(self.state, {})[None] = self.state
        self.prefix_tree[self.state]['"'] = self.state + 1
        self.state += 1

        return [self.state]

    def build_number_state(self) -> list[int]:
        base_s = self.state

        # Initial sign / leading digit transitions
        f_nums = "-0123456789"
        for c in f_nums:
            if c == "-":
                self.prefix_tree.setdefault(base_s, {})[c] = base_s + 1
            elif c == "0":
                self.prefix_tree.setdefault(base_s, {})[c] = base_s + 2
            else:
                self.prefix_tree.setdefault(base_s, {})[c] = base_s + 3

        # Transitions following negative sign '-'
        for c in "0123456789":
            if c == "0":
                self.prefix_tree.setdefault(base_s + 1, {})[c] = base_s + 2
            else:
                self.prefix_tree.setdefault(base_s + 1, {})[c] = base_s + 3

        # Allow decimal point after leading zero '0'
        self.prefix_tree.setdefault(base_s + 2, {})["."] = base_s + 4

        # Allow extra digits or decimal point after leading non-zero digit
        self.prefix_tree.setdefault(base_s + 3, {})["."] = base_s + 4
        for c in "0123456789":
            self.prefix_tree.setdefault(base_s + 3, {})[c] = base_s + 3

        # First fractional digit mandatory after decimal point
        for c in "0123456789":
            self.prefix_tree.setdefault(base_s + 4, {})[c] = base_s + 5

        # Subsequent optional fractional digits
        for c in "0123456789":
            self.prefix_tree.setdefault(base_s + 5, {})[c] = base_s + 5

        self.state += 5

        # base_s + 4 is included so single-digit decimals (e.g. 1.5) exit correctly
        return [base_s + 2, base_s + 3, base_s + 4, base_s + 5]

    def build_int_state(self) -> list[int]:
        base_s = self.state

        f_nums = "-0123456789"
        for c in f_nums:
            if c == "-":
                self.prefix_tree.setdefault(base_s, {})[c] = base_s + 1
            elif c == "0":
                self.prefix_tree.setdefault(base_s, {})[c] = base_s + 2
            else:
                self.prefix_tree.setdefault(base_s, {})[c] = base_s + 3

        for c in "0123456789":
            if c == "0":
                self.prefix_tree.setdefault(base_s + 1, {})[c] = base_s + 2
            else:
                self.prefix_tree.setdefault(base_s + 1, {})[c] = base_s + 3

        for c in "0123456789":
            self.prefix_tree.setdefault(base_s + 3, {})[c] = base_s + 3

        self.state += 3

        return [base_s + 2, base_s + 3]


    def allowed_token(self, state: int):
        allowed_tokens: list[int] = []
        
        if self.cache.get(state, None) is not None:
            return self.cache[state]    #get the value of state!
        for key in self.prefix_tree[state]:
            if key is None:
                for token, token_id in self.all_vocab.items():
                    allowed_tokens.append(token)
                break

            for token in self.vocab_pins[key]:
                tmp_state = state
                flag = True
                for c in token: #for every character in token
                    if c in self.prefix_tree[tmp_state]:
                        tmp_state = self.prefix_tree[tmp_state][c]
                        if tmp_state == -1:
                            break
                    else:
                        flag = False
                        break
                if flag:
                    allowed_tokens.append(self.vocab_pins[key][token])

        self.cache[state] = allowed_tokens
        return allowed_tokens


    def mask_logits(self, logits, allowed_tokes):
        masked = [float("-inf")] * len(logits)

        for token_id in allowed_tokens:
            masked[token_id] = logits[token_id]

        return masked


    def transition(self, token_str) -> None:
        for c in self.tr_token(token_str):
            if self.current_state == -1:
                break
            
            edges = self.prefix_tree[self.current_state]
            for c in edges:
                self.current_state = edges[c]
            
            elif None in edges:
                self.current_state = edges[None]

