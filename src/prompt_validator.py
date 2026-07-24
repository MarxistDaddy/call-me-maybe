from pydantic import BaseModel

class Prompt(BaseModel):
    prompt: str


class Prompts(BaseModel):
    prompts: list[Prompt]


class ParamterType(BaseModel):
    type: str


class FcnDef(BaseModel):
    name: str
    description: str
    parameters: dict[str, ParamterType]


class FncDefs(BaseModel):
    func_list: list[FncDef]
