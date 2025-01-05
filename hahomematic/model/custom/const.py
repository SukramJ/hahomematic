"""Constants used by hahomematic custom data points."""

from __future__ import annotations

from enum import Enum, StrEnum


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


class CDPD(StrEnum):
    """Enum for custom data point definitions."""

    ALLOW_UNDEFINED_GENERIC_DPS = "allow_undefined_generic_dps"
    DEFAULT_DPS = "default_dps"
    INCLUDE_DEFAULT_DPS = "include_default_dps"
    DEVICE_GROUP = "device_group"
    DEVICE_DEFINITIONS = "device_definitions"
    ADDITIONAL_DPS = "additional_dps"
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
    HEATING_VALVE_TYPE = "heating_valve_type"
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
    MIN_MAX_VALUE_NOT_RELEVANT_FOR_MANU_MODE = "min_max_value_not_relevant_for_manu_mode"
    ON_TIME_UNIT = "on_time_unit"
    ON_TIME_VALUE = "on_time_value"
    OPEN = "open"
    OPERATING_VOLTAGE = "operating_voltage"
    OPERATION_MODE = "channel_operation_mode"
    OPTICAL_ALARM_ACTIVE = "optical_alarm_active"
    OPTICAL_ALARM_SELECTION = "optical_alarm_selection"
    OPTIMUM_START_STOP = "optimum_start_stop"
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
    TEMPERATURE_OFFSET = "temperature_offset"
    VALVE_STATE = "valve_state"
    VOLTAGE = "voltage"
