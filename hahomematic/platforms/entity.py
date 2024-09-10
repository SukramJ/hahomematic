"""Functions for entity creation."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable, Mapping
from datetime import datetime
from functools import partial, wraps
from inspect import getfullargspec
import logging
from typing import Any, Final, cast

import voluptuous as vol

from hahomematic import central as hmcu, client as hmcl, support as hms
from hahomematic.async_support import loop_check
from hahomematic.config import WAIT_FOR_CALLBACK
from hahomematic.const import (
    CALLBACK_TYPE,
    DEFAULT_CUSTOM_ID,
    ENTITY_KEY,
    EVENT_ADDRESS,
    EVENT_CHANNEL_NO,
    EVENT_DEVICE_TYPE,
    EVENT_INTERFACE_ID,
    EVENT_PARAMETER,
    EVENT_VALUE,
    INIT_DATETIME,
    KEY_CHANNEL_OPERATION_MODE_VISIBILITY,
    NO_CACHE_ENTRY,
    CallSource,
    DeviceDescription,
    EntityUsage,
    Flag,
    HmPlatform,
    Operations,
    Parameter,
    ParameterData,
    ParameterType,
    ParamsetKey,
)
from hahomematic.exceptions import HaHomematicException
from hahomematic.platforms import device as hmd
from hahomematic.platforms.decorators import config_property, value_property
from hahomematic.platforms.support import (
    EntityNameData,
    GenericParameterType,
    PayloadMixin,
    convert_value,
    generate_channel_unique_id,
)
from hahomematic.support import get_entity_key, reduce_args
import hahomematic.validator as val

_LOGGER: Final = logging.getLogger(__name__)

_CONFIGURABLE_CHANNEL: Final[tuple[str, ...]] = (
    "KEY_TRANSCEIVER",
    "MULTI_MODE_INPUT_TRANSMITTER",
)
_COLLECTOR_ARGUMENT_NAME: Final = "collector"

_FIX_UNIT_REPLACE: Final[Mapping[str, str]] = {
    '"': "",
    "100%": "%",
    "% rF": "%",
    "degree": "°C",
    "Lux": "lx",
    "m3": "m³",
}

_FIX_UNIT_BY_PARAM: Final[Mapping[str, str]] = {
    Parameter.ACTUAL_TEMPERATURE: "°C",
    Parameter.CURRENT_ILLUMINATION: "lx",
    Parameter.HUMIDITY: "%",
    Parameter.ILLUMINATION: "lx",
    Parameter.LEVEL: "%",
    Parameter.MASS_CONCENTRATION_PM_10_24H_AVERAGE: "µg/m³",
    Parameter.MASS_CONCENTRATION_PM_1_24H_AVERAGE: "µg/m³",
    Parameter.MASS_CONCENTRATION_PM_2_5_24H_AVERAGE: "µg/m³",
    Parameter.OPERATING_VOLTAGE: "V",
    Parameter.RSSI_DEVICE: "dBm",
    Parameter.RSSI_PEER: "dBm",
    Parameter.SUNSHINE_DURATION: "min",
    Parameter.WIND_DIRECTION: "°",
    Parameter.WIND_DIRECTION_RANGE: "°",
}

_MULTIPLIER_UNIT: Final[Mapping[str, int]] = {
    "100%": 100,
}

EVENT_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(EVENT_ADDRESS): val.device_address,
        vol.Required(EVENT_CHANNEL_NO): val.channel_no,
        vol.Required(EVENT_DEVICE_TYPE): str,
        vol.Required(EVENT_INTERFACE_ID): str,
        vol.Required(EVENT_PARAMETER): str,
        vol.Optional(EVENT_VALUE): vol.Any(bool, int),
    }
)


class CallbackEntity(ABC):
    """Base class for callback entities."""

    _platform: HmPlatform

    def __init__(self, central: hmcu.CentralUnit, unique_id: str) -> None:
        """Init the callback entity."""
        self._central: Final = central
        self._unique_id: Final = unique_id
        self._entity_updated_callbacks: dict[Callable, str] = {}
        self._device_removed_callbacks: list[Callable] = []
        self._custom_id: str | None = None
        self._modified_at: datetime = INIT_DATETIME
        self._refreshed_at: datetime = INIT_DATETIME

    @value_property
    @abstractmethod
    def available(self) -> bool:
        """Return the availability of the device."""

    @property
    def custom_id(self) -> str | None:
        """Return the custom id."""
        return self._custom_id

    @classmethod
    def default_platform(cls) -> HmPlatform:
        """Return, the platform of the entity."""
        return cls._platform

    @property
    def central(self) -> hmcu.CentralUnit:
        """Return the central unit."""
        return self._central

    @config_property
    @abstractmethod
    def full_name(self) -> str:
        """Return the full name of the entity."""

    @value_property
    def modified_at(self) -> datetime:
        """Return the last update datetime value."""
        return self._modified_at

    @value_property
    def refreshed_at(self) -> datetime:
        """Return the last refresh datetime value."""
        return self._refreshed_at

    @config_property
    @abstractmethod
    def name(self) -> str | None:
        """Return the name of the entity."""

    @property
    @abstractmethod
    def path(self) -> str:
        """Return the path of the entity."""

    @config_property
    def platform(self) -> HmPlatform:
        """Return, the platform of the entity."""
        return self._platform

    @config_property
    def unique_id(self) -> str:
        """Return the unique_id."""
        return self._unique_id

    @config_property
    def usage(self) -> EntityUsage:
        """Return the entity usage."""
        return EntityUsage.ENTITY

    @config_property
    def enabled_default(self) -> bool:
        """Return, if entity should be enabled based on usage attribute."""
        return self.usage in (
            EntityUsage.CE_PRIMARY,
            EntityUsage.CE_VISIBLE,
            EntityUsage.ENTITY,
            EntityUsage.EVENT,
        )

    @property
    def is_registered(self) -> bool:
        """Return if entity is registered externally."""
        return self._custom_id is not None

    def register_internal_entity_updated_callback(self, cb: Callable) -> CALLBACK_TYPE:
        """Register internal entity updated callback."""
        return self.register_entity_updated_callback(cb=cb, custom_id=DEFAULT_CUSTOM_ID)

    def register_entity_updated_callback(self, cb: Callable, custom_id: str) -> CALLBACK_TYPE:
        """Register entity updated callback."""
        if custom_id != DEFAULT_CUSTOM_ID:
            if self._custom_id is not None and self._custom_id != custom_id:
                raise HaHomematicException(
                    f"REGISTER_entity_updated_CALLBACK failed: hm_entity: {self.full_name} is already registered by {self._custom_id}"
                )
            self._custom_id = custom_id

        if callable(cb) and cb not in self._entity_updated_callbacks:
            self._entity_updated_callbacks[cb] = custom_id
            return partial(self._unregister_entity_updated_callback, cb=cb, custom_id=custom_id)
        return None

    def _unregister_entity_updated_callback(self, cb: Callable, custom_id: str) -> None:
        """Unregister entity updated callback."""
        if cb in self._entity_updated_callbacks:
            del self._entity_updated_callbacks[cb]
        if self.custom_id == custom_id:
            self._custom_id = None

    def register_device_removed_callback(self, cb: Callable) -> CALLBACK_TYPE:
        """Register the device removed callback."""
        if callable(cb) and cb not in self._device_removed_callbacks:
            self._device_removed_callbacks.append(cb)
            return partial(self._unregister_device_removed_callback, cb=cb)
        return None

    def _unregister_device_removed_callback(self, cb: Callable) -> None:
        """Unregister the device removed callback."""
        if cb in self._device_removed_callbacks:
            self._device_removed_callbacks.remove(cb)

    @loop_check
    def fire_entity_updated_callback(self, *args: Any, **kwargs: Any) -> None:
        """Do what is needed when the value of the entity has been updated/refreshed."""
        for callback_handler in self._entity_updated_callbacks:
            try:
                callback_handler(entity=self)
            except Exception as ex:
                _LOGGER.warning("FIRE_entity_updated_EVENT failed: %s", reduce_args(args=ex.args))

    @loop_check
    def fire_device_removed_callback(self, *args: Any) -> None:
        """Do what is needed when the entity has been removed."""
        for callback_handler in self._device_removed_callbacks:
            try:
                callback_handler(*args)
            except Exception as ex:
                _LOGGER.warning("FIRE_DEVICE_REMOVED_EVENT failed: %s", reduce_args(args=ex.args))

    def _set_modified_at(self, now: datetime = datetime.now()) -> None:
        """Set last_update to current datetime."""
        self._modified_at = now
        self._set_refreshed_at(now=now)

    def _set_refreshed_at(self, now: datetime = datetime.now()) -> None:
        """Set last_update to current datetime."""
        self._refreshed_at = now

    def __str__(self) -> str:
        """Provide some useful information."""
        return f"path: {self.path}, name: {self.full_name}"


class BaseEntity(CallbackEntity, PayloadMixin):
    """Base class for regular entities."""

    def __init__(
        self,
        device: hmd.HmDevice,
        unique_id: str,
        channel_no: int,
        is_in_multiple_channels: bool,
    ) -> None:
        """Initialize the entity."""
        PayloadMixin.__init__(self)
        super().__init__(central=device.central, unique_id=unique_id)
        self._device: Final[hmd.HmDevice] = device
        self._channel_no: Final = channel_no
        self._channel_address: Final[str] = hms.get_channel_address(
            device_address=device.device_address, channel_no=channel_no
        )
        self._channel_description: Final = self._get_channel_description(
            interface_id=self._device.interface_id, channel_address=self._channel_address
        )
        self._channel_type: Final = self._channel_description["TYPE"]
        self._channel_unique_id: Final = generate_channel_unique_id(
            central=device.central, address=self._channel_address
        )
        self._rooms: Final = self._central.device_details.get_channel_rooms(
            channel_address=self._channel_address
        )
        self._is_in_multiple_channels: Final = is_in_multiple_channels
        self._function: Final = self._central.device_details.get_function_text(
            address=self._channel_address
        )
        self._client: Final[hmcl.Client] = device.client

        self._forced_usage: EntityUsage | None = None
        self._entity_name_data: Final = self._get_entity_name()

    @value_property
    def available(self) -> bool:
        """Return the availability of the device."""
        return self._device.available

    @property
    def base_channel_no(self) -> int | None:
        """Return the base channel no of the entity."""
        return self._device.get_sub_device_channel(channel_no=self._channel_no)

    @property
    def _base_path(self) -> str:
        """Return the base path of the entity."""
        return f"{self._central.name}/{self._device.device_address}/{self._channel_no}/{self._platform}"

    @config_property
    def channel_address(self) -> str:
        """Return the channel_address of the entity."""
        return self._channel_address

    @config_property
    def channel_no(self) -> int:
        """Return the channel_no of the entity."""
        return self._channel_no

    @config_property
    def channel_unique_id(self) -> str:
        """Return the channel_unique_id of the entity."""
        return self._channel_unique_id

    @property
    def device(self) -> hmd.HmDevice:
        """Return the device of the entity."""
        return self._device

    @config_property
    def function(self) -> str | None:
        """Return the function of the entity."""
        return self._function

    @config_property
    def full_name(self) -> str:
        """Return the full name of the entity."""
        return self._entity_name_data.full_name

    @config_property
    def is_in_multiple_channels(self) -> bool:
        """Return the parameter/CE is also in multiple channels."""
        return self._is_in_multiple_channels

    @config_property
    def name(self) -> str | None:
        """Return the name of the entity."""
        return self._entity_name_data.entity_name

    @property
    def name_data(self) -> EntityNameData:
        """Return the entity name data of the entity."""
        return self._entity_name_data

    @config_property
    def room(self) -> str | None:
        """Return the room, if only one exists."""
        if self._rooms and len(self._rooms) == 1:
            return list(self._rooms)[0]
        return None

    @config_property
    def rooms(self) -> set[str]:
        """Return the rooms assigned to an entity."""
        return self._rooms

    @config_property
    def usage(self) -> EntityUsage:
        """Return the entity usage."""
        return self._get_entity_usage()

    def force_usage(self, forced_usage: EntityUsage) -> None:
        """Set the entity usage."""
        self._forced_usage = forced_usage

    @abstractmethod
    async def load_entity_value(self, call_source: CallSource, direct_call: bool = False) -> None:
        """Init the entity data."""

    def _get_channel_description(
        self, interface_id: str, channel_address: str
    ) -> DeviceDescription:
        """Return the description of the channel."""
        return self.central.device_descriptions.get_device_description(
            interface_id=interface_id, address=channel_address
        )

    @abstractmethod
    def _get_entity_name(self) -> EntityNameData:
        """Generate the name for the entity."""

    @abstractmethod
    def _get_entity_usage(self) -> EntityUsage:
        """Generate the usage for the entity."""


class BaseParameterEntity[
    ParameterT: GenericParameterType,
    InputParameterT: GenericParameterType,
](BaseEntity):
    """Base class for stateless entities."""

    def __init__(
        self,
        device: hmd.HmDevice,
        unique_id: str,
        channel_address: str,
        paramset_key: ParamsetKey,
        parameter: str,
        parameter_data: ParameterData,
    ) -> None:
        """Initialize the entity."""
        self._paramset_key: Final = paramset_key
        # required for name in BaseEntity
        self._parameter: Final[str] = parameter

        super().__init__(
            device=device,
            unique_id=unique_id,
            channel_no=hms.get_channel_no(address=channel_address),  # type: ignore[arg-type]
            is_in_multiple_channels=device.central.paramset_descriptions.is_in_multiple_channels(
                channel_address=channel_address, parameter=parameter
            ),
        )
        self._is_un_ignored: Final[bool] = (
            self._central.parameter_visibility.parameter_is_un_ignored(
                device_type=self._device.device_type,
                channel_no=self._channel_no,
                paramset_key=self._paramset_key,
                parameter=self._parameter,
                custom_only=True,
            )
        )
        self._value: ParameterT = None  # type: ignore[assignment]
        self._old_value: ParameterT = None  # type: ignore[assignment]
        self._modified_at: datetime = INIT_DATETIME
        self._refreshed_at: datetime = INIT_DATETIME
        self._state_uncertain: bool = True
        self._is_forced_sensor: bool = False
        self._assign_parameter_data(parameter_data=parameter_data)

    def _assign_parameter_data(self, parameter_data: ParameterData) -> None:
        """Assign parameter data to instance variables."""
        self._type: ParameterType = ParameterType(parameter_data["TYPE"])
        self._values = (
            tuple(parameter_data["VALUE_LIST"]) if parameter_data.get("VALUE_LIST") else None
        )
        self._max: ParameterT = self._convert_value(parameter_data["MAX"])
        self._min: ParameterT = self._convert_value(parameter_data["MIN"])
        self._default: ParameterT = self._convert_value(parameter_data["DEFAULT"])
        flags: int = parameter_data["FLAGS"]
        self._visible: bool = flags & Flag.VISIBLE == Flag.VISIBLE
        self._service: bool = flags & Flag.SERVICE == Flag.SERVICE
        self._operations: int = parameter_data["OPERATIONS"]
        self._special: Mapping[str, Any] | None = parameter_data.get("SPECIAL")
        self._raw_unit: str | None = parameter_data.get("UNIT")
        self._unit: str | None = self._cleanup_unit(raw_unit=self._raw_unit)
        self._multiplier: int = self._get_multiplier(raw_unit=self._raw_unit)

    @config_property
    def default(self) -> ParameterT:
        """Return default value."""
        return self._default

    @config_property
    def hmtype(self) -> ParameterType:
        """Return the HomeMatic type."""
        return self._type

    @config_property
    def is_unit_fixed(self) -> bool:
        """Return if the unit is fixed."""
        return self._raw_unit != self._unit

    @config_property
    def is_un_ignored(self) -> bool:
        """Return if the parameter is un ignored."""
        return self._is_un_ignored

    @config_property
    def entity_key(self) -> ENTITY_KEY:
        """Return entity key value."""
        return get_entity_key(
            channel_address=self._channel_address,
            paramset_key=self._paramset_key,
            parameter=self._parameter,
        )

    @config_property
    def max(self) -> ParameterT:
        """Return max value."""
        return self._max

    @config_property
    def min(self) -> ParameterT:
        """Return min value."""
        return self._min

    @config_property
    def multiplier(self) -> int:
        """Return multiplier value."""
        return self._multiplier

    @config_property
    def parameter(self) -> str:
        """Return parameter name."""
        return self._parameter

    @config_property
    def paramset_key(self) -> ParamsetKey:
        """Return paramset_key name."""
        return self._paramset_key

    @property
    def path(self) -> str:
        """Return the path of the entity."""
        return f"{self._base_path}/{self._parameter}".lower()

    @config_property
    def raw_unit(self) -> str | None:
        """Return raw unit value."""
        return self._raw_unit

    @property
    def is_forced_sensor(self) -> bool:
        """Return, if entity is forced to read only."""
        return self._is_forced_sensor

    @property
    def is_readable(self) -> bool:
        """Return, if entity is readable."""
        return bool(self._operations & Operations.READ)

    @property
    def is_valid(self) -> bool:
        """Return, if the value of the entity is valid based on the refreshed at datetime."""
        return self._refreshed_at > INIT_DATETIME

    @property
    def is_writeable(self) -> bool:
        """Return, if entity is writeable."""
        return False if self._is_forced_sensor else bool(self._operations & Operations.WRITE)

    @value_property
    def modified_at(self) -> datetime:
        """Return the last modified datetime value."""
        return self._modified_at

    @value_property
    def refreshed_at(self) -> datetime:
        """Return the last refreshed datetime value."""
        return self._refreshed_at

    @property
    def unconfirmed_last_value_send(self) -> ParameterT:
        """Return the unconfirmed value send for the entity."""
        return cast(
            ParameterT,
            self._client.last_value_send_cache.get_last_value_send(entity_key=self.entity_key),
        )

    @property
    def old_value(self) -> ParameterT:
        """Return the old value of the entity."""
        return self._old_value

    @config_property
    def platform(self) -> HmPlatform:
        """Return, the platform of the entity."""
        return HmPlatform.SENSOR if self._is_forced_sensor else self._platform

    @property
    def state_uncertain(self) -> bool:
        """Return, if the state is uncertain."""
        return self._state_uncertain

    @value_property
    def value(self) -> ParameterT:
        """Return the value of the entity."""
        return self._value

    @property
    def supports_events(self) -> bool:
        """Return, if entity is supports events."""
        return bool(self._operations & Operations.EVENT)

    @config_property
    def unique_id(self) -> str:
        """Return the unique_id."""
        return (
            f"{self._unique_id}_{HmPlatform.SENSOR}" if self._is_forced_sensor else self._unique_id
        )

    @config_property
    def unit(self) -> str | None:
        """Return unit value."""
        return self._unit

    @config_property
    def values(self) -> tuple[str, ...] | None:
        """Return the values."""
        return self._values

    @property
    def visible(self) -> bool:
        """Return the if entity is visible in ccu."""
        return self._visible

    @property
    def _channel_operation_mode(self) -> str | None:
        """Return the channel operation mode if available."""
        cop: BaseParameterEntity | None = self._device.get_generic_entity(
            channel_address=self._channel_address,
            parameter=Parameter.CHANNEL_OPERATION_MODE,
        )
        if cop and cop.value:
            return str(cop.value)
        return None

    @property
    def _enabled_by_channel_operation_mode(self) -> bool | None:
        """Return, if the entity/event must be enabled."""
        if self._channel_type not in _CONFIGURABLE_CHANNEL:
            return None
        if self._parameter not in KEY_CHANNEL_OPERATION_MODE_VISIBILITY:
            return None
        if (cop := self._channel_operation_mode) is None:
            return None
        return cop in KEY_CHANNEL_OPERATION_MODE_VISIBILITY[self._parameter]

    def force_to_sensor(self) -> None:
        """Change the platform of the entity."""
        if self.platform == HmPlatform.SENSOR:
            _LOGGER.debug(
                "Platform for %s is already %s. Doing nothing", self.full_name, HmPlatform.SENSOR
            )
            return
        if self.platform not in (HmPlatform.NUMBER, HmPlatform.SELECT, HmPlatform.TEXT):
            _LOGGER.debug(
                "Platform %s for %s cannot be changed to %s",
                self.platform,
                self.full_name,
                HmPlatform.SENSOR,
            )
        _LOGGER.debug(
            "Changing the platform of %s to %s (read-only)", self.full_name, HmPlatform.SENSOR
        )
        self._is_forced_sensor = True

    def _cleanup_unit(self, raw_unit: str | None) -> str | None:
        """Replace given unit."""
        if new_unit := _FIX_UNIT_BY_PARAM.get(self._parameter):
            return new_unit
        if not raw_unit:
            return None
        for check, fix in _FIX_UNIT_REPLACE.items():
            if check in raw_unit:
                return fix
        return raw_unit

    def _get_multiplier(self, raw_unit: str | None) -> int:
        """Replace given unit."""
        if not raw_unit:
            return 1
        if multiplier := _MULTIPLIER_UNIT.get(raw_unit):
            return multiplier
        return 1

    @abstractmethod
    async def event(self, value: Any) -> None:
        """Handle event for which this handler has subscribed."""

    async def load_entity_value(self, call_source: CallSource, direct_call: bool = False) -> None:
        """Init the entity data."""
        if direct_call is False and hms.changed_within_seconds(last_change=self._refreshed_at):
            return

        # Check, if entity is readable
        if not self.is_readable:
            return

        self.write_value(
            value=await self._device.value_cache.get_value(
                channel_address=self._channel_address,
                paramset_key=self._paramset_key,
                parameter=self._parameter,
                call_source=call_source,
                direct_call=direct_call,
            )
        )

    def write_value(self, value: Any) -> tuple[ParameterT, ParameterT]:
        """Update value of the entity."""
        old_value = self._value
        if value == NO_CACHE_ENTRY:
            if self.refreshed_at != INIT_DATETIME:
                self._state_uncertain = True
                self.fire_entity_updated_callback()
            return (old_value, None)  # type: ignore[return-value]

        new_value = self._convert_value(value)
        if old_value == new_value:
            self._set_refreshed_at()
        else:
            self._set_modified_at()
            self._old_value = old_value
            self._value = new_value
            self._state_uncertain = False
        self.fire_entity_updated_callback()
        return (old_value, new_value)

    def update_parameter_data(self) -> None:
        """Update parameter data."""
        if parameter_data := self._central.paramset_descriptions.get_parameter_data(
            interface_id=self._device.interface_id,
            channel_address=self._channel_address,
            paramset_key=self._paramset_key,
            parameter=self._parameter,
        ):
            self._assign_parameter_data(parameter_data=parameter_data)

    def _convert_value(self, value: Any) -> ParameterT:
        """Convert to value to ParameterT."""
        if value is None:
            return None  # type: ignore[return-value]
        try:
            if (
                self._type == ParameterType.BOOL
                and self._values is not None
                and value is not None
                and isinstance(value, str)
            ):
                return convert_value(  # type: ignore[no-any-return]
                    value=self._values.index(value),
                    target_type=self._type,
                    value_list=self.values,
                )
            return convert_value(  # type: ignore[no-any-return]
                value=value, target_type=self._type, value_list=self.values
            )
        except (ValueError, TypeError):  # pragma: no cover
            _LOGGER.debug(
                "CONVERT_VALUE: conversion failed for %s, %s, %s, value: [%s]",
                self._device.interface_id,
                self._channel_address,
                self._parameter,
                value,
            )
            return None  # type: ignore[return-value]

    def get_event_data(self, value: Any = None) -> dict[str, Any]:
        """Get the event_data."""
        event_data = {
            EVENT_ADDRESS: self._device.device_address,
            EVENT_CHANNEL_NO: self._channel_no,
            EVENT_DEVICE_TYPE: self._device.device_type,
            EVENT_INTERFACE_ID: self._device.interface_id,
            EVENT_PARAMETER: self._parameter,
        }
        if value is not None:
            event_data[EVENT_VALUE] = value
        return cast(dict[str, Any], EVENT_DATA_SCHEMA(event_data))


class CallParameterCollector:
    """Create a Paramset based on given generic entities."""

    def __init__(self, device: hmd.HmDevice) -> None:
        """Init the generator."""
        self._device: Final = device
        self._client: Final = device.client
        self._paramsets: Final[dict[ParamsetKey, dict[int, dict[str, dict[str, Any]]]]] = {}

    def add_entity(
        self,
        entity: BaseParameterEntity,
        value: Any,
        collector_order: int,
    ) -> None:
        """Add a generic entity."""
        if entity.paramset_key not in self._paramsets:
            self._paramsets[entity.paramset_key] = {}
        if collector_order not in self._paramsets[entity.paramset_key]:
            self._paramsets[entity.paramset_key][collector_order] = {}
        if entity.channel_address not in self._paramsets[entity.paramset_key][collector_order]:
            self._paramsets[entity.paramset_key][collector_order][entity.channel_address] = {}
        self._paramsets[entity.paramset_key][collector_order][entity.channel_address][
            entity.parameter
        ] = value

    async def send_data(
        self, wait_for_callback: int | None, use_command_queue: bool, use_put_paramset: bool
    ) -> bool:
        """Send data to backend."""
        for paramset_key, paramsets in self._paramsets.items():  # pylint: disable=too-many-nested-blocks
            for paramset_no in dict(sorted(paramsets.items())).values():
                for channel_address, paramset in paramset_no.items():
                    if use_put_paramset is False or len(paramset.values()) == 1:
                        for parameter, value in paramset.items():
                            set_value_command = partial(
                                self._client.set_value,
                                channel_address=channel_address,
                                paramset_key=paramset_key,
                                parameter=parameter,
                                value=value,
                                wait_for_callback=wait_for_callback,
                            )
                            if use_command_queue:
                                await self._device.central.command_queue_handler.put(
                                    address=channel_address,
                                    command=set_value_command,
                                )
                            elif not await set_value_command():
                                return False  # pragma: no cover
                    else:
                        put_paramset_command = partial(
                            self._client.put_paramset,
                            channel_address=channel_address,
                            paramset_key=paramset_key,
                            values=paramset,
                            wait_for_callback=wait_for_callback,
                        )
                        if use_command_queue:
                            await self._device.central.command_queue_handler.put(
                                address=channel_address,
                                command=put_paramset_command,
                            )
                        elif not await put_paramset_command():
                            return False  # pragma: no cover
        return True


def bind_collector(
    wait_for_callback: int | None = WAIT_FOR_CALLBACK,
    use_command_queue: bool = False,
    use_put_paramset: bool = True,
) -> Callable:
    """Decorate function to automatically add collector if not set."""

    def decorator_bind_collector[_CallableT: Callable[..., Any]](func: _CallableT) -> _CallableT:
        """Decorate function to automatically add collector if not set."""
        argument_index = getfullargspec(func).args.index(_COLLECTOR_ARGUMENT_NAME)

        @wraps(func)
        async def wrapper_collector(*args: Any, **kwargs: Any) -> Any:
            """Wrap method to add collector."""

            try:
                collector_exists = args[argument_index] is not None
            except IndexError:
                collector_exists = kwargs.get(_COLLECTOR_ARGUMENT_NAME) is not None

            if collector_exists:
                return_value = await func(*args, **kwargs)
            else:
                collector = CallParameterCollector(device=args[0].device)
                kwargs[_COLLECTOR_ARGUMENT_NAME] = collector
                return_value = await func(*args, **kwargs)
                await collector.send_data(
                    wait_for_callback=wait_for_callback,
                    use_command_queue=use_command_queue,
                    use_put_paramset=use_put_paramset,
                )
            return return_value

        return wrapper_collector  # type: ignore[return-value]

    return decorator_bind_collector
