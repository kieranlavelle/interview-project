import orjson
from pydantic import BaseModel


class BaseSchema(BaseModel):
    class Config:
        def orjson_dumps(v, *, default):
            # orjson.dumps returns bytes, to match standard json.dumps we need to decode
            return orjson.dumps(v, default=default).decode()

        arbitrary_types_allowed = True
        json_dumps = orjson_dumps
        allow_population_by_field_name = True


class ErrorResponse(BaseSchema):
    error: str
