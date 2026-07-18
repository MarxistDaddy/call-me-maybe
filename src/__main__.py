from .parsing import Parser
from llm_sdk.llm_sdk import Small_LLM_Model

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
    print(model.encode("hello hh ff"))



if __name__ == "__main__":
    main()

