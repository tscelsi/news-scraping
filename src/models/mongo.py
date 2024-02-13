from bson import ObjectId as _ObjectId
from pydantic.functional_validators import AfterValidator, BeforeValidator
from typing_extensions import Annotated


def convert_to_object_id(value: str | _ObjectId) -> str:
    if not _ObjectId.is_valid(value):
        raise ValueError("Invalid ObjectId")
    return _ObjectId(value)


def convert_from_object_id(value: _ObjectId) -> str:
    return str(value)


PyObjectId = Annotated[
    str, BeforeValidator(convert_from_object_id), AfterValidator(convert_to_object_id)
]
