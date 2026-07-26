from pydantic import BaseModel

class PromptItem(BaseModel):
    prompt: str


class PromptsList(BaseModel):
    prompts: list[PromptItem]


#class ParamterType(BaseModel):
#    type: str
#
#
#class FcnDef(BaseModel):
#    name: str
#    description: str
#    parameters: dict[str, ParamterType]
#
#
#class FncDefs(BaseModel):
#    func_list: list[FncDef]


#isnt this wrong? type!!
class ReturnType(BaseModel):
    type: str


class FncItem(BaseModel):
    name: str
    description: str
    parameters: dict[str, ReturnType]
    returns: ReturnType


class FncDefs(BaseModel):
    functions_def: list[FncItem]



