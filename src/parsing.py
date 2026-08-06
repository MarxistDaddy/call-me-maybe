import argparse


class Parser:
    def __init__(self):
        self.fnc_def: str = ""        
        self.input: str = ""        
        self.output: str = ""        
        self.model: str = ""        


    def parsing(self):
        
        p = argparse.ArgumentParser(usage=
            "uv main.py --functions_definition <function_def> "
            "--input <input>"
            "--output <output>"
            "--model <model>"
        )

        p.add_argument("-f", "--functions_definition",
            default="./data/input/functions_definition.json"
        )

        p.add_argument(
            "-i", "--input",
            default="data/input/function_calling_tests.json"
        )

        p.add_argument(
            "-o", "--output",
            default="./data/output/output.json"
        )

        p.add_argument(
            "-m", "--model",
            default="Qwen/Qwen3-0.6b"
        )

        args = p.parse_args()

        self.fnc_def = args.functions_definition
        self.input = args.input
        self.output = args.output
        self.model = args.model

        #print(self.fnc_def, type(self.fnc_def).__name__)
        #print(self.input, type(self.input).__name__)
        #print(self.output, type(self.output).__name__)
        #print(self.model, type(self.model).__name__)


#x = Parser()
#x.parsing()


