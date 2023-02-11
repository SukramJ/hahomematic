"""Constants used by hahomematic custom entities."""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Final

from hahomematic.backport import StrEnum


class HmEntityDefinition(StrEnum):
    """Enum for entity definitions."""

    IP_COVER = "IPCover"
    IP_DIMMER = "IPDimmer"
    IP_GARAGE = "IPGarage"
    IP_SWITCH = "IPSwitch"
    IP_FIXED_COLOR_LIGHT = "IPFixedColorLight"
    IP_SIMPLE_FIXED_COLOR_LIGHT = "IPSimpleFixedColorLight"
    IP_LOCK = "IPLock"
    IP_THERMOSTAT = "IPThermostat"
    IP_THERMOSTAT_GROUP = "IPThermostatGroup"
    IP_SIREN = "IPSiren"
    RF_COVER = "RfCover"
    RF_DIMMER = "RfDimmer"
    RF_DIMMER_COLOR = "RfDimmer_Color"
    RF_DIMMER_COLOR_TEMP = "RfDimmer_Color_Temp"
    RF_DIMMER_WITH_VIRT_CHANNEL = "RfDimmerWithVirtChannel"
    RF_LOCK = "RfLock"
    RF_THERMOSTAT = "RfThermostat"
    RF_THERMOSTAT_GROUP = "RfThermostatGroup"
    RF_SIREN = "RfSiren"
    RF_SWITCH = "RfSwitch"
    SIMPLE_RF_THERMOSTAT = "SimpleRfThermostat"


FIELD_ACTIVE_PROFILE: Final = "active_profile"
FIELD_AUTO_MODE: Final = "auto_mode"
FIELD_BOOST_MODE: Final = "boost_mode"
FIELD_CHANNEL_COLOR: Final = "channel_color"
FIELD_CHANNEL_LEVEL: Final = "channel_level"
FIELD_CHANNEL_LEVEL_2: Final = "channel_level_2"
FIELD_CHANNEL_OPERATION_MODE: Final = "channel_operation_mode"
FIELD_CHANNEL_STATE: Final = "channel_state"
FIELD_COLOR: Final = "color"
FIELD_COLOR_LEVEL: Final = "color_temp"
FIELD_COMFORT_MODE: Final = "comfort_mode"
FIELD_CONTROL_MODE: Final = "control_mode"
FIELD_CURRENT: Final = "current"
FIELD_DIRECTION: Final = "direction"
FIELD_DOOR_COMMAND: Final = "door_command"
FIELD_DOOR_STATE: Final = "door_state"
FIELD_DURATION_UNIT: Final = "duration_unit"
FIELD_DURATION: Final = "duration"
FIELD_DUTY_CYCLE: Final = "duty_cycle"
FIELD_DUTYCYCLE: Final = "dutycycle"
FIELD_ERROR: Final = "error"
FIELD_ENERGY_COUNTER: Final = "energy_counter"
FIELD_FREQUENCY: Final = "frequency"
FIELD_HEATING_COOLING: Final = "heating_cooling"
FIELD_HUMIDITY: Final = "humidity"
FIELD_INHIBIT: Final = "inhibit"
FIELD_LEVEL: Final = "level"
FIELD_LEVEL_2: Final = "level_2"
FIELD_LOCK_STATE: Final = "lock_state"
FIELD_LOCK_TARGET_LEVEL: Final = "lock_target_level"
FIELD_LOW_BAT: Final = "low_bat"
FIELD_LOWBAT: Final = "lowbat"
FIELD_LOWERING_MODE: Final = "lowering_mode"
FIELD_MANU_MODE: Final = "manu_mode"
FIELD_ON_TIME_VALUE: Final = "on_time_value"
FIELD_ON_TIME_UNIT: Final = "on_time_unit"
FIELD_OPERATING_VOLTAGE: Final = "operating_voltage"
FIELD_OPEN: Final = "open"
FIELD_PARTY_MODE: Final = "party_mode"
FIELD_PROGRAM: Final = "program"
FIELD_POWER: Final = "power"
FIELD_RAMP_TIME_VALUE: Final = "ramp_time_value"
FIELD_RAMP_TIME_UNIT: Final = "ramp_time_unit"
FIELD_RSSI_DEVICE: Final = "rssi_device"
FIELD_RSSI_PEER: Final = "rssi_peer"
FIELD_SABOTAGE: Final = "sabotage"
FIELD_SECTION: Final = "section"
FIELD_SET_POINT_MODE: Final = "set_point_mode"
FIELD_SETPOINT: Final = "setpoint"
FIELD_STATE: Final = "state"
FIELD_STOP: Final = "stop"
FIELD_SWITCH_MAIN: Final = "switch_main"
FIELD_SWITCH_V1: Final = "vswitch_1"
FIELD_SWITCH_V2: Final = "vswitch_2"
FIELD_TEMPERATURE: Final = "temperature"
FIELD_TEMPERATURE_MAXIMUM: Final = "temperature_maximum"
FIELD_TEMPERATURE_MINIMUM: Final = "temperature_minimum"
FIELD_VALVE_STATE: Final = "valve_state"
FIELD_VOLTAGE: Final = "voltage"
FIELD_ACOUSTIC_ALARM_ACTIVE: Final = "acoustic_alarm_active"
FIELD_ACOUSTIC_ALARM_SELECTION: Final = "acoustic_alarm_selection"
FIELD_OPTICAL_ALARM_ACTIVE: Final = "optical_alarm_active"
FIELD_OPTICAL_ALARM_SELECTION: Final = "optical_alarm_selection"


@dataclass
class CustomConfig:
    """Data for custom entity creation."""

    func: Callable
    channels: tuple[int, ...]
    extended: ExtendedConfig | None = None


@dataclass
class ExtendedConfig:
    """Extended data for custom entity creation."""

    fixed_channels: dict[int, dict[str, str]] | None = None
    additional_entities: dict[int | tuple[int, ...], tuple[str, ...]] | None = None

    @property
    def required_parameters(self) -> tuple[str, ...]:
        """Return vol.Required parameters from extended config."""
        required_parameters: list[str] = []
        if fixed_channels := self.fixed_channels:
            for mapping in fixed_channels.values():
                required_parameters.extend(mapping.values())

        if additional_entities := self.additional_entities:
            for parameters in additional_entities.values():
                required_parameters.extend(parameters)

        return tuple(required_parameters)