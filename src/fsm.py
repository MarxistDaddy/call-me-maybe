from .validate import FncDefs


class FSM:
    def __init__(self, fcts) -> None:
        self.state: int = 0
        self.prefix_tree: dict[int, dict[str | None, int]] = {}
        self.functions = fcts
        self.saved_state = 0

    def tr_token(self, string: str) -> str:
        return string.replace(" ", "Ġ")

    def build_state(self):
        start = self.tr_token('{"name": "')
        params = self.tr_token(', "parameters": {')

        # 1. Build common prefix: {"name": "
        for c in start:
            self.prefix_tree.setdefault(self.state, {})[c] = self.state + 1
            self.state += 1

        self.saved_state = self.state

        # 2. Iterate through function definitions | buid the name. parameter, values: fetch then store!
        for fnc in self.functions:
            curr_fnc_state = self.saved_state #save the state!

            # build the name first, after tokenizing it!
            for c in self.tr_token(fnc.name):
                if c in self.prefix_tree.get(curr_fnc_state, {}):
                    curr_fnc_state = self.prefix_tree[curr_fnc_state][c]
                
                else:
                    next_state = self.state + 1
                    self.prefix_tree.setdefault(curr_fnc_state, {})[c] = next_state
                    self.state = next_state
                    curr_fnc_state = self.state


            # Build parameters key branch
            for c in params:
                if c in self.prefix_tree.get(curr_fnc_state, {}):
                    curr_fnc_state = self.prefix_tree[curr_fnc_state][c]
                else:
                    next_state = self.state + 1
                    self.prefix_tree.setdefault(curr_fnc_state, {})[c] = next_state
                    self.state = next_state
                    curr_fnc_state = self.state

            num_params = len(fnc.parameters)
            
            # 3. Build parameter keys and type constraints
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

                exit_states = self.build_type_state(curr_fnc_state, param_obj)
                is_last_param = index == num_params

                # 4. Handle parameter comma vs closing object braces
                if is_last_param:
                    # Collapse all valid exit states into a single unified "}}" tail
                    brace_1 = self.state + 1
                    for exit_s in exit_states:
                        self.prefix_tree.setdefault(exit_s, {})["}"] = brace_1
                    
                    brace_2 = brace_1 + 1
                    self.prefix_tree.setdefault(brace_1, {})["}"] = brace_2
                    self.state = brace_2
                else:
                    next_s = self.state + 1
                    for exit_s in exit_states:
                        self.prefix_tree.setdefault(exit_s, {})[","] = next_s
                    self.state = next_s
                    curr_fnc_state = self.state

        for k in self.prefix_tree:
            print(f"{k}: {self.prefix_tree[k]}")

    def build_type_state(self, curr_state: int, param_obj) -> list[int]:
        if hasattr(param_obj, "type"):
            param_type = param_obj.type
        elif isinstance(param_obj, dict):
            param_type = param_obj.get("type", "string")
        else:
            param_type = "string"

        if param_type == "integer":
            return self.build_int_state(curr_state)
        elif param_type == "number":
            return self.build_number_state(curr_state)
        else:
            return self.build_string_state(curr_state)

    def build_int_state(self, curr_state: int) -> list[int]:
        digits = [str(i) for i in range(10)]

        minus_state = self.state + 1
        digit_s = self.state + 2
        self.state = digit_s

        self.prefix_tree.setdefault(curr_state, {})["-"] = minus_state

        for d in digits:
            self.prefix_tree.setdefault(curr_state, {})[d] = digit_s
            self.prefix_tree.setdefault(minus_state, {})[d] = digit_s
            self.prefix_tree.setdefault(digit_s, {})[d] = digit_s

        return [digit_s]

    def build_number_state(self, curr_state: int) -> list[int]:
        digits = [str(i) for i in range(10)]

        s_minus = self.state + 1
        s_int = self.state + 2
        s_dot = self.state + 3
        s_frac = self.state + 4
        s_e = self.state + 5
        s_esign = self.state + 6
        s_exp = self.state + 7
        self.state = s_exp

        # 1. Negative sign
        self.prefix_tree.setdefault(curr_state, {})["-"] = s_minus

        # 2. Integer part
        for d in digits:
            self.prefix_tree.setdefault(curr_state, {})[d] = s_int
            self.prefix_tree.setdefault(s_minus, {})[d] = s_int
            self.prefix_tree.setdefault(s_int, {})[d] = s_int

        exit_states = [s_int]

        # 3. Fractional part
        self.prefix_tree.setdefault(s_int, {})["."] = s_dot
        for d in digits:
            self.prefix_tree.setdefault(s_dot, {})[d] = s_frac
            self.prefix_tree.setdefault(s_frac, {})[d] = s_frac

        exit_states.append(s_frac)

        # 4. Exponent part
        for e_char in ["e", "E"]:
            self.prefix_tree.setdefault(s_int, {})[e_char] = s_e
            self.prefix_tree.setdefault(s_frac, {})[e_char] = s_e

        self.prefix_tree.setdefault(s_e, {})["+"] = s_esign
        self.prefix_tree.setdefault(s_e, {})["-"] = s_esign

        for d in digits:
            self.prefix_tree.setdefault(s_e, {})[d] = s_exp
            self.prefix_tree.setdefault(s_esign, {})[d] = s_exp
            self.prefix_tree.setdefault(s_exp, {})[d] = s_exp

        exit_states.append(s_exp)

        return exit_states

    def build_string_state(self, curr_state: int) -> list[int]:
        open_q_state = self.state + 1
        escape_state = self.state + 2
        close_q_state = self.state + 3
        self.state = close_q_state

        self.prefix_tree.setdefault(curr_state, {})['"'] = open_q_state

        normal_chars = [chr(i) for i in range(32, 127) if chr(i) not in ('"', '\\')]
        for c in normal_chars:
            self.prefix_tree.setdefault(open_q_state, {})[c] = open_q_state

        self.prefix_tree.setdefault(open_q_state, {})['Ġ'] = open_q_state
        self.prefix_tree.setdefault(open_q_state, {})['\\'] = escape_state

        valid_escapes = ['"', '\\', '/', 'b', 'f', 'n', 'r', 't']
        for c in valid_escapes:
            self.prefix_tree.setdefault(escape_state, {})[c] = open_q_state

        self.prefix_tree.setdefault(open_q_state, {})['"'] = close_q_state

        return [close_q_state]
