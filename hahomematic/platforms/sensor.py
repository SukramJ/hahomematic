"""
Module for entities implemented using the
sensor platform (https://www.home-assistant.io/integrations/sensor/).
"""
from __future__ import annotations

import logging
from typing import Any

import hahomematic.central_unit as hm_central
from hahomematic.config import EXTENDED_SYSVARS
from hahomematic.const import HmPlatform
import hahomematic.device as hm_device
from hahomematic.entity import GenericEntity, GenericSystemVariable
from hahomematic.helpers import SystemVariableData

_LOGGER = logging.getLogger(__name__)


class HmSensor(GenericEntity[Any]):
    """
    Implementation of a sensor.
    This is a default platform that gets automatically generated.
    """

    def __init__(
        self,
        device: hm_device.HmDevice,
        unique_id: str,
        channel_address: str,
        paramset_key: str,
        parameter: str,
        parameter_data: dict[str, Any],
    ):
        super().__init__(
            device=device,
            unique_id=unique_id,
            channel_address=channel_address,
            paramset_key=paramset_key,
            parameter=parameter,
            parameter_data=parameter_data,
            platform=HmPlatform.SENSOR,
        )

    @property
    def value(self) -> Any | None:
        """Return the value."""
        if self._value is not None and self._value_list is not None:
            return self._value_list[int(self._value)]
        if convert_func := self._get_converter_func():
            return convert_func(self._value)
        return self._value

    def _get_converter_func(self) -> Any:
        """Return a converter based on sensor."""
        if convert_func := CONVERTERS_BY_DEVICE_PARAM.get(
            (self.device_type, self.parameter)
        ):
            return convert_func
        if convert_func := CONVERTERS_BY_PARAM.get(self.parameter):
            return convert_func


def _convert_float_to_int(value: Any) -> int | None:
    """Convert value to int."""
    if value is not None and isinstance(value, float):
        return int(value)
    return value


def _fix_rssi(value: Any) -> int | None:
    """
    Fix rssi value.
    See https://github.com/danielperna84/hahomematic/blob/devel/docs/rssi_fix.md
    """
    if value is None or not isinstance(value, int):
        return None
    if -127 < value < 0:
        return value
    if 1 < value < 127:
        return value * -1
    if -256 < value < -129:
        return (value * -1) - 256
    if 129 < value < 256:
        return value - 256
    return None


class HmSysvarSensor(GenericSystemVariable):
    """
    Implementation of a sysvar sensor.
    """

    def __init__(self, central: hm_central.CentralUnit, data: SystemVariableData):
        """Initialize the entity."""
        super().__init__(central=central, data=data, platform=HmPlatform.HUB_SENSOR)

    @property
    def value(self) -> Any | None:
        """Return the value."""
        if (
            EXTENDED_SYSVARS
            and self._value is not None
            and self._value_list is not None
        ):
            return self._value_list[int(self._value)]
        return _check_length_and_warn(name=self.ccu_var_name, value=self._value)


CONVERTERS_BY_DEVICE_PARAM: dict[tuple[str, str], Any] = {
    ("HmIP-SCTH230", "CONCENTRATION"): _convert_float_to_int,
}

CONVERTERS_BY_PARAM: dict[str, Any] = {
    "RSSI_PEER": _fix_rssi,
    "RSSI_DEVICE": _fix_rssi,
}


def _check_length_and_warn(name: str, value: Any) -> Any:
    """Check the length of a variable and warn if too long."""
    if isinstance(value, str) and len(value) > 255:
        _LOGGER.warning(
            "Value of sysvar %s exceedes maximum allowed length of 255 chars. Value will be limited to 255 chars.",
            name,
        )
        return value[0:255:1]
    return value
