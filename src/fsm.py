from src.validate.py import FncDefs

class FSM:
    def __init__(self) -> None:
        self.state: int = 0
        self.prefix_tree: dict[int, dict[str | None, int]] = {}

    def build_state(self):
        start = self.tr('{"name": "')
        param = self.tr('{"parameters": {')
        
        for c in start:
            print(c)


    def tr(self, string: str) -> str:
        return string.replace(" ", "Ġ")
        

x = FSM()
x.build_state()
