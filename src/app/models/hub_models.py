from pydantic import BaseModel, BeforeValidator, field_validator, Field
from typing import Optional, Any, Annotated, cast, Union
from pydantic_core.core_schema import ValidationInfo
from app.models.config import AppConfig

cfg: AppConfig = AppConfig()  # type: ignore


def map_signed(percent: Any) -> tuple[int, int]:
    """
    Map the speeds
    This gets handled by pydantic validator

    Converts percentage (-100 to 100) into Signed 8-bit Integers.
    Tuple[int[percentage], int[scaled]]
    """

    if type(percent) is not int:
        return percent

    # 1. Handle STOP
    if percent == 0:
        return (0, 0)
    # 2. Clamp Input
    percent = max(-100, min(100, percent))
    # 3. Scale with cfg.DEADZONE
    # We need to map 1..100% to 25..127 (approx)
    usable_range = 127 - cfg.DEADZONE
    if percent > 0:
        # Positive (Forward)
        val = cfg.DEADZONE + (percent / 100.0 * usable_range)
        return (percent, int(val))
    else:
        # Negative (Backward)
        # We calculate positive magnitude first, then flip to negative
        mag: float | int = cfg.DEADZONE + (abs(percent) / 100.0 * usable_range)
        val: int = -int(mag)
        # Convert negative number to unsigned byte (Two's Complement)
        # e.g. -100 becomes 156 (0x9C)
        return (percent, val & 0xFF)


class MotorSpeed(BaseModel):
    # tuple[percentage, scaled]
    speed_a: Annotated[
        Optional[Union[tuple[int, int], int]], BeforeValidator(func=map_signed)
    ] = Field(union_mode="left_to_right")
    speed_b: Annotated[
        Optional[Union[tuple[int, int], int]], BeforeValidator(func=map_signed)
    ] = Field(union_mode="left_to_right")
    speed_c: Annotated[
        Optional[Union[tuple[int, int], int]], BeforeValidator(func=map_signed)
    ] = Field(union_mode="left_to_right")
    speed_d: Annotated[
        Optional[Union[tuple[int, int], int]], BeforeValidator(func=map_signed)
    ] = Field(union_mode="left_to_right")
    # speed_a: Annotated[Optional[Union[tuple[int, int]], int], BeforeValidator(func=map_signed)] =  Field(union_mode='left_to_right')
    # speed_b: Annotated[Optional[Union[tuple[int, int]], int], BeforeValidator(func=map_signed)] =  Field(union_mode='left_to_right')
    # speed_c: Annotated[Optional[Union[tuple[int, int]], int], BeforeValidator(func=map_signed)] =  Field(union_mode='left_to_right')
    # speed_d: Annotated[Optional[Union[tuple[int, int]], int], BeforeValidator(func=map_signed)] =  Field(union_mode='left_to_right')

    # @field_validator("f1", "f2", mode="before")
    # @classmethod
    # def capitalize(cls, value: str) -> str:
    #     return value.capitalize()
