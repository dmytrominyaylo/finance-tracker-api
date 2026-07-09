from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class BasePydanticModel(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        str_strip_whitespace=True,
        alias_generator=to_camel,
    )
