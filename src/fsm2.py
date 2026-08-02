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
        params = self.tr_token('", "parameters": {')

        # 1. Build common prefix: {"name": "
        for c in start:
            self.prefix_tree.setdefault(self.state, {})[c] = self.state + 1
            self.state += 1

        self.saved_state = self.state

        # 2. Iterate through function definitions
        for fnc in self.functions:
            curr_fnc_state = self.saved_state

            # Build the function name
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

    def build_string_state(self, curr_state: int) -> list[int]:
        s_body = self.state + 1
        s_close = self.state + 2

        self.prefix_tree.setdefault(curr_state, {})['"'] = s_body
        self.prefix_tree.setdefault(s_body, {})[None] = s_body
        self.prefix_tree.setdefault(s_body, {})['"'] = s_close

        self.state += 2
        return [s_close]

    def build_number_state(self, curr_state: int) -> list[int]:
        s_neg = self.state + 1
        s_zero = self.state + 2
        s_int = self.state + 3
        s_dot = self.state + 4
        s_frac = self.state + 5

        f_nums = "-0123456789"
        for c in f_nums:
            if c == "-":
                self.prefix_tree.setdefault(curr_state, {})[c] = s_neg
            elif c == "0":
                self.prefix_tree.setdefault(curr_state, {})[c] = s_zero
            else:
                self.prefix_tree.setdefault(curr_state, {})[c] = s_int

        for c in "0123456789":
            if c == "0":
                self.prefix_tree.setdefault(s_neg, {})[c] = s_zero
            else:
                self.prefix_tree.setdefault(s_neg, {})[c] = s_int

        self.prefix_tree.setdefault(s_zero, {})["."] = s_dot

        self.prefix_tree.setdefault(s_int, {})["."] = s_dot
        for c in "0123456789":
            self.prefix_tree.setdefault(s_int, {})[c] = s_int

        for c in "0123456789":
            self.prefix_tree.setdefault(s_dot, {})[c] = s_frac

        for c in "0123456789":
            self.prefix_tree.setdefault(s_frac, {})[c] = s_frac

        self.state += 5
        return [s_zero, s_int, s_frac]

    def build_int_state(self, curr_state: int) -> list[int]:
        s_neg = self.state + 1
        s_zero = self.state + 2
        s_int = self.state + 3

        f_nums = "-0123456789"
        for c in f_nums:
            if c == "-":
                self.prefix_tree.setdefault(curr_state, {})[c] = s_neg
            elif c == "0":
                self.prefix_tree.setdefault(curr_state, {})[c] = s_zero
            else:
                self.prefix_tree.setdefault(curr_state, {})[c] = s_int

        for c in "0123456789":
            if c == "0":
                self.prefix_tree.setdefault(s_neg, {})[c] = s_zero
            else:
                self.prefix_tree.setdefault(s_neg, {})[c] = s_int

        for c in "0123456789":
            self.prefix_tree.setdefault(s_int, {})[c] = s_int

        self.state += 3
        return [s_zero, s_int]
