"""Constants used by hahomematic custom entities."""

from __future__ import annotations

from enum import Enum, IntEnum, StrEnum
from typing import Final

CLIMATE_ENTRY_RANGE: Final = range(1, 13)
CLIMATE_TIME_RANGE: Final = range(1441)
HM_PRESET_MODE_PREFIX: Final = "week_program_"


class ClimateProfile(StrEnum):
    """Enum for climate profiles."""

    P1 = "P1"
    P2 = "P2"
    P3 = "P3"
    P4 = "P4"
    P5 = "P5"
    P6 = "P6"


class ClimateEntryType(StrEnum):
    """Enum for climate item type."""

    ENDTIME = "ENDTIME"
    TEMPERATURE = "TEMPERATURE"


class ClimateWeekday(StrEnum):
    """Enum for climate week days."""

    MONDAY = "MONDAY"
    TUESDAY = "TUESDAY"
    WEDNESDAY = "WEDNESDAY"
    THURSDAY = "THURSDAY"
    FRIDAY = "FRIDAY"
    SATURDAY = "SATURDAY"
    SUNDAY = "SUNDAY"


SCHEDULE_DICT = dict[
    ClimateProfile, dict[ClimateWeekday, dict[int, dict[ClimateEntryType, int | float]]]
]
PROFILE_DICT = dict[ClimateWeekday, dict[int, dict[ClimateEntryType, int | float]]]
WEEKDAY_DICT = dict[int, dict[ClimateEntryType, int | float]]


class DeviceProfile(StrEnum):
    """Enum for device profiles."""

    IP_BUTTON_LOCK = "IPButtonLock"
    IP_COVER = "IPCover"
    IP_DIMMER = "IPDimmer"
    IP_DRG_DALI = "IPDRGDALI"
    IP_FIXED_COLOR_LIGHT = "IPFixedColorLight"
    IP_GARAGE = "IPGarage"
    IP_HDM = "IPHdm"
    IP_LOCK = "IPLock"
    IP_RGBW_LIGHT = "IPRGBW"
    IP_SIMPLE_FIXED_COLOR_LIGHT = "IPSimpleFixedColorLight"
    IP_SIMPLE_FIXED_COLOR_LIGHT_WIRED = "IPSimpleFixedColorLightWired"
    IP_SIREN = "IPSiren"
    IP_SIREN_SMOKE = "IPSirenSmoke"
    IP_SWITCH = "IPSwitch"
    IP_THERMOSTAT = "IPThermostat"
    IP_THERMOSTAT_GROUP = "IPThermostatGroup"
    RF_BUTTON_LOCK = "RFButtonLock"
    RF_COVER = "RfCover"
    RF_DIMMER = "RfDimmer"
    RF_DIMMER_COLOR = "RfDimmer_Color"
    RF_DIMMER_COLOR_FIXED = "RfDimmer_Color_Fixed"
    RF_DIMMER_COLOR_TEMP = "RfDimmer_Color_Temp"
    RF_DIMMER_WITH_VIRT_CHANNEL = "RfDimmerWithVirtChannel"
    RF_LOCK = "RfLock"
    RF_SIREN = "RfSiren"
    RF_SWITCH = "RfSwitch"
    RF_THERMOSTAT = "RfThermostat"
    RF_THERMOSTAT_GROUP = "RfThermostatGroup"
    SIMPLE_RF_THERMOSTAT = "SimpleRfThermostat"


class ED(StrEnum):
    """Enum for entity definitions."""

    ALLOW_UNDEFINED_GENERIC_ENTITIES = "allow_undefined_generic_entities"
    DEFAULT_ENTITIES = "default_entities"
    INCLUDE_DEFAULT_ENTITIES = "include_default_entities"
    DEVICE_GROUP = "device_group"
    DEVICE_DEFINITIONS = "device_definitions"
    ADDITIONAL_ENTITIES = "additional_entities"
    FIELDS = "fields"
    REPEATABLE_FIELDS = "repeatable_fields"
    VISIBLE_REPEATABLE_FIELDS = "visible_repeatable_fields"
    PRIMARY_CHANNEL = "primary_channel"
    SECONDARY_CHANNELS = "secondary_channels"
    VISIBLE_FIELDS = "visible_fields"


class Field(Enum):
    """Enum for fields."""

    ACOUSTIC_ALARM_ACTIVE = "acoustic_alarm_active"
    ACOUSTIC_ALARM_SELECTION = "acoustic_alarm_selection"
    ACTIVE_PROFILE = "active_profile"
    AUTO_MODE = "auto_mode"
    BOOST_MODE = "boost_mode"
    BUTTON_LOCK = "button_lock"
    CHANNEL_COLOR = "channel_color"
    CHANNEL_LEVEL = "channel_level"
    CHANNEL_LEVEL_2 = "channel_level_2"
    CHANNEL_OPERATION_MODE = "channel_operation_mode"
    CHANNEL_STATE = "channel_state"
    COLOR = "color"
    COLOR_BEHAVIOUR = "color_behaviour"
    COLOR_LEVEL = "color_temp"
    COLOR_TEMPERATURE = "color_temperature"
    COMBINED_PARAMETER = "combined_parameter"
    COMFORT_MODE = "comfort_mode"
    CONCENTRATION = "concentration"
    CONTROL_MODE = "control_mode"
    CURRENT = "current"
    DEVICE_OPERATION_MODE = "device_operation_mode"
    DIRECTION = "direction"
    DOOR_COMMAND = "door_command"
    DOOR_STATE = "door_state"
    DURATION = "duration"
    DURATION_UNIT = "duration_unit"
    DUTYCYCLE = "dutycycle"
    DUTY_CYCLE = "duty_cycle"
    EFFECT = "effect"
    ENERGY_COUNTER = "energy_counter"
    ERROR = "error"
    FREQUENCY = "frequency"
    HEATING_COOLING = "heating_cooling"
    HUE = "hue"
    HUMIDITY = "humidity"
    INHIBIT = "inhibit"
    LEVEL = "level"
    LEVEL_2 = "level_2"
    LEVEL_COMBINED = "level_combined"
    LOCK_STATE = "lock_state"
    LOCK_TARGET_LEVEL = "lock_target_level"
    LOWBAT = "lowbat"
    LOWERING_MODE = "lowering_mode"
    LOW_BAT = "low_bat"
    MANU_MODE = "manu_mode"
    ON_TIME_UNIT = "on_time_unit"
    ON_TIME_VALUE = "on_time_value"
    OPEN = "open"
    OPERATING_VOLTAGE = "operating_voltage"
    OPTICAL_ALARM_ACTIVE = "optical_alarm_active"
    OPTICAL_ALARM_SELECTION = "optical_alarm_selection"
    PARTY_MODE = "party_mode"
    POWER = "power"
    PROGRAM = "program"
    RAMP_TIME_TO_OFF_UNIT = "ramp_time_to_off_unit"
    RAMP_TIME_TO_OFF_VALUE = "ramp_time_to_off_value"
    RAMP_TIME_UNIT = "ramp_time_unit"
    RAMP_TIME_VALUE = "ramp_time_value"
    RSSI_DEVICE = "rssi_device"
    RSSI_PEER = "rssi_peer"
    SABOTAGE = "sabotage"
    SATURATION = "saturation"
    SECTION = "section"
    SETPOINT = "setpoint"
    SET_POINT_MODE = "set_point_mode"
    SMOKE_DETECTOR_ALARM_STATUS = "smoke_detector_alarm_status"
    SMOKE_DETECTOR_COMMAND = "smoke_detector_command"
    STATE = "state"
    STOP = "stop"
    SWITCH_MAIN = "switch_main"
    SWITCH_V1 = "vswitch_1"
    SWITCH_V2 = "vswitch_2"
    TEMPERATURE = "temperature"
    TEMPERATURE_MAXIMUM = "temperature_maximum"
    TEMPERATURE_MINIMUM = "temperature_minimum"
    VALVE_STATE = "valve_state"
    VOLTAGE = "voltage"


class ClimateStateChangeArg(StrEnum):
    """Enum with climate state change arguments."""

    HVAC_MODE = "hvac_mode"
    PRESET_MODE = "preset_mode"
    TEMPERATURE = "temperature"


class ClimateModeHm(StrEnum):
    """Enum with the HM modes."""

    AUTO = "AUTO-MODE"  # 0
    AWAY = "PARTY-MODE"  # 2
    BOOST = "BOOST-MODE"  # 3
    MANU = "MANU-MODE"  # 1


class ClimateModeHmIP(IntEnum):
    """Enum with the HmIP modes."""

    AUTO = 0
    AWAY = 2
    MANU = 1


class HmHvacAction(StrEnum):
    """Enum with the hvac actions."""

    COOL = "cooling"
    HEAT = "heating"
    IDLE = "idle"
    OFF = "off"


class HmHvacMode(StrEnum):
    """Enum with the hvac modes."""

    AUTO = "auto"
    COOL = "cool"
    HEAT = "heat"
    OFF = "off"


class HmPresetMode(StrEnum):
    """Enum with preset modes."""

    AWAY = "away"
    BOOST = "boost"
    COMFORT = "comfort"
    ECO = "eco"
    NONE = "none"
    WEEK_PROGRAM_1 = "week_program_1"
    WEEK_PROGRAM_2 = "week_program_2"
    WEEK_PROGRAM_3 = "week_program_3"
    WEEK_PROGRAM_4 = "week_program_4"
    WEEK_PROGRAM_5 = "week_program_5"
    WEEK_PROGRAM_6 = "week_program_6"
