"""Constants used by hahomematic."""
from __future__ import annotations

from datetime import datetime
from enum import Enum, IntEnum, StrEnum
from typing import Final

DEFAULT_CONNECTION_CHECKER_INTERVAL: Final = (
    15  # check if connection is available via rpc ping every:
)
DEFAULT_ENCODING: Final = "UTF-8"
DEFAULT_PING_PONG_MISMATCH_COUNT: Final = 10
DEFAULT_RECONNECT_WAIT: Final = 120  # wait with reconnect after a first ping was successful
DEFAULT_TIMEOUT: Final = 60  # default timeout for a connection
DEFAULT_TLS: Final = False
DEFAULT_VERIFY_TLS: Final = False

# Password can be empty.
# Allowed characters: A-Z, a-z, 0-9, .!$():;#-
# The CCU WebUI also supports ÄäÖöÜüß, but these characters are not supported by the XmlRPC servers
CCU_PASSWORD_PATTERN: Final = r"[A-Za-z0-9.!$():;#-]{0,}"

IDENTIFIER_SEPARATOR: Final = "@"
INIT_DATETIME: Final = datetime.strptime("01.01.1970 00:00:00", "%d.%m.%Y %H:%M:%S")
IP_ANY_V4: Final = "0.0.0.0"
PORT_ANY: Final = 0

PATH_JSON_RPC: Final = "/api/homematic.cgi"

HOMEGEAR_SERIAL = "Homegear_SN0815"

PROGRAM_ADDRESS: Final = "program"
SYSVAR_ADDRESS: Final = "sysvar"

ATTR_ADDRESS: Final = "address"
ATTR_AVAILABLE: Final = "available"
ATTR_CHANNELS: Final = "channels"
ATTR_CHANNEL_NO: Final = "channel_no"
ATTR_DATA: Final = "data"
ATTR_DEVICE_TYPE: Final = "device_type"
ATTR_FIRMWARE: Final = "firmware"
ATTR_ID: Final = "id"
ATTR_INSTANCE_NAME: Final = "instance_name"
ATTR_INTERFACE: Final = "interface"
ATTR_INTERFACE_ID: Final = "interface_id"
ATTR_NAME: Final = "name"
ATTR_PARAMETER: Final = "parameter"
ATTR_PASSWORD: Final = "password"
ATTR_SECONDS_SINCE_LAST_EVENT: Final = "seconds_since_last_event"
ATTR_TLS: Final = "tls"
ATTR_TYPE: Final = "type"
ATTR_USERNAME: Final = "username"
ATTR_VALUE: Final = "value"
ATTR_VERIFY_TLS: Final = "verify_tls"

EVENT_CONFIG_PENDING: Final = "CONFIG_PENDING"
EVENT_ERROR: Final = "ERROR"
EVENT_UPDATE_PENDING: Final = "UPDATE_PENDING"

EVENT_PONG: Final = "PONG"
EVENT_PRESS: Final = "PRESS"
EVENT_PRESS_CONT: Final = "PRESS_CONT"
EVENT_PRESS_LOCK: Final = "PRESS_LOCK"
EVENT_PRESS_LONG: Final = "PRESS_LONG"
EVENT_PRESS_LONG_RELEASE: Final = "PRESS_LONG_RELEASE"
EVENT_PRESS_LONG_START: Final = "PRESS_LONG_START"
EVENT_PRESS_SHORT: Final = "PRESS_SHORT"
EVENT_PRESS_UNLOCK: Final = "PRESS_UNLOCK"
EVENT_SEQUENCE_OK: Final = "SEQUENCE_OK"
EVENT_STICKY_UN_REACH: Final = "STICKY_UNREACH"
EVENT_UN_REACH: Final = "UNREACH"

FILE_CUSTOM_UN_IGNORE_PARAMETERS: Final = "unignore"
FILE_DEVICES: Final = "homematic_devices.json"
FILE_PARAMSETS: Final = "homematic_paramsets.json"

FLAG_VISIBLE: Final = 1
FLAG_INTERAL: Final = 2
FLAG_TRANSFORM: Final = 4  # not used
FLAG_SERVICE: Final = 8
FLAG_STICKY: Final = 10  # This might be wrong. Documentation says 0x10 # not used

HM_ARG_ON_TIME: Final = "on_time"
HM_ARG_VALUE: Final = "value"
HM_ARG_ON: Final = "on"
HM_ARG_OFF: Final = "off"

HM_ADDRESS: Final = "ADDRESS"
HM_AVAILABLE_FIRMWARE: Final = "AVAILABLE_FIRMWARE"
HM_CHILDREN: Final = "CHILDREN"
HM_DEFAULT: Final = "DEFAULT"
HM_FIRMWARE: Final = "FIRMWARE"
HM_FIRMWARE_UPDATABLE: Final = "UPDATABLE"
HM_FIRMWARE_UPDATE_STATE: Final = "FIRMWARE_UPDATE_STATE"
HM_FLAGS: Final = "FLAGS"
HM_MAX: Final = "MAX"
HM_MIN: Final = "MIN"
HM_NAME: Final = "NAME"
HM_OPERATIONS: Final = "OPERATIONS"
HM_PARAMSETS: Final = "PARAMSETS"
HM_PARENT: Final = "PARENT"
HM_PARENT_TYPE: Final = "PARENT_TYPE"
HM_SPECIAL: Final = "SPECIAL"  # Which has the following keys
HM_SUBTYPE: Final = "SUBTYPE"
HM_TYPE: Final = "TYPE"
HM_UNIT: Final = "UNIT"
HM_VALUE_LIST: Final = "VALUE_LIST"

MAX_CACHE_AGE: Final = 60
MAX_JSON_SESSION_AGE: Final = 90

OPERATION_NONE: Final = 0  # not used
OPERATION_READ: Final = 1
OPERATION_WRITE: Final = 2
OPERATION_EVENT: Final = 4

PARAM_CHANNEL_OPERATION_MODE: Final = "CHANNEL_OPERATION_MODE"
PARAM_DEVICE_OPERATION_MODE: Final = "DEVICE_OPERATION_MODE"
PARAM_TEMPERATURE_MAXIMUM: Final = "TEMPERATURE_MAXIMUM"
PARAM_TEMPERATURE_MINIMUM: Final = "TEMPERATURE_MINIMUM"

PARAMSET_KEY_MASTER: Final = "MASTER"
PARAMSET_KEY_VALUES: Final = "VALUES"

PROGRAM_ID: Final = "id"
PROGRAM_ISACTIVE: Final = "isActive"
PROGRAM_ISINTERNAL: Final = "isInternal"
PROGRAM_LASTEXECUTETIME: Final = "lastExecuteTime"
PROGRAM_NAME: Final = "name"

REGA_SCRIPT_FETCH_ALL_DEVICE_DATA: Final = "fetch_all_device_data.fn"
REGA_SCRIPT_GET_SERIAL: Final = "get_serial.fn"
REGA_SCRIPT_PATH: Final = "rega_scripts"
REGA_SCRIPT_SET_SYSTEM_VARIABLE: Final = "set_system_variable.fn"
REGA_SCRIPT_SYSTEM_VARIABLES_EXT_MARKER: Final = "get_system_variables_ext_marker.fn"

SYSVAR_HASEXTMARKER: Final = "hasExtMarker"
SYSVAR_ID: Final = "id"
SYSVAR_ISINTERNAL: Final = "isInternal"
SYSVAR_MAX_VALUE: Final = "maxValue"
SYSVAR_MIN_VALUE: Final = "minValue"
SYSVAR_NAME: Final = "name"
SYSVAR_TYPE: Final = "type"
SYSVAR_UNIT: Final = "unit"
SYSVAR_VALUE: Final = "value"
SYSVAR_VALUE_LIST: Final = "valueList"

CONFIGURABLE_CHANNEL: Final[tuple[str, ...]] = (
    "KEY_TRANSCEIVER",
    "MULTI_MODE_INPUT_TRANSMITTER",
)

KEY_CHANNEL_OPERATION_MODE_VISIBILITY: Final[dict[str, tuple[str, ...]]] = {
    "STATE": ("BINARY_BEHAVIOR",),
    EVENT_PRESS_LONG: ("KEY_BEHAVIOR", "SWITCH_BEHAVIOR"),
    EVENT_PRESS_LONG_RELEASE: ("KEY_BEHAVIOR", "SWITCH_BEHAVIOR"),
    EVENT_PRESS_LONG_START: ("KEY_BEHAVIOR", "SWITCH_BEHAVIOR"),
    EVENT_PRESS_SHORT: ("KEY_BEHAVIOR", "SWITCH_BEHAVIOR"),
}

CLICK_EVENTS: Final[tuple[str, ...]] = (
    EVENT_PRESS,
    EVENT_PRESS_CONT,
    EVENT_PRESS_LOCK,
    EVENT_PRESS_LONG,
    EVENT_PRESS_LONG_RELEASE,
    EVENT_PRESS_LONG_START,
    EVENT_PRESS_SHORT,
    EVENT_PRESS_UNLOCK,
)

DEVICE_ERROR_EVENTS: Final[tuple[str, ...]] = ("ERROR", "SENSOR_ERROR")

IMPULSE_EVENTS: Final[tuple[str, ...]] = (EVENT_SEQUENCE_OK,)

BUTTON_ACTIONS: Final[tuple[str, ...]] = ("RESET_MOTION", "RESET_PRESENCE")

FIX_UNIT_REPLACE: Final[dict[str, str]] = {
    '"': "",
    "100%": "%",
    "% rF": "%",
    "degree": "°C",
    "Lux": "lx",
    "m3": "m³",
}

FIX_UNIT_BY_PARAM: Final[dict[str, str]] = {
    "ACTUAL_TEMPERATURE": "°C",
    "CURRENT_ILLUMINATION": "lx",
    "HUMIDITY": "%",
    "ILLUMINATION": "lx",
    "LEVEL": "%",
    "MASS_CONCENTRATION_PM_10_24H_AVERAGE": "µg/m³",
    "MASS_CONCENTRATION_PM_1_24H_AVERAGE": "µg/m³",
    "MASS_CONCENTRATION_PM_2_5_24H_AVERAGE": "µg/m³",
    "OPERATING_VOLTAGE": "V",
    "RSSI_DEVICE": "dBm",
    "RSSI_PEER": "dBm",
    "SUNSHINEDURATION": "min",
    "WIND_DIRECTION": "°",
    "WIND_DIRECTION_RANGE": "°",
}

IF_BIDCOS_RF_NAME: Final = "BidCos-RF"
IF_BIDCOS_RF_PORT: Final = 2001
IF_BIDCOS_RF_TLS_PORT: Final = 42001
IF_BIDCOS_WIRED_NAME: Final = "BidCos-Wired"
IF_BIDCOS_WIRED_PORT: Final = 2000
IF_BIDCOS_WIRED_TLS_PORT: Final = 42000
IF_HMIP_RF_NAME: Final = "HmIP-RF"
IF_HMIP_RF_PORT: Final = 2010
IF_HMIP_RF_TLS_PORT: Final = 42010
IF_VIRTUAL_DEVICES_NAME: Final = "VirtualDevices"
IF_VIRTUAL_DEVICES_PATH: Final = "/groups"
IF_VIRTUAL_DEVICES_PORT: Final = 9292
IF_VIRTUAL_DEVICES_TLS_PORT: Final = 49292

IF_NAMES: Final[tuple[str, ...]] = (
    IF_BIDCOS_RF_NAME,
    IF_BIDCOS_WIRED_NAME,
    IF_HMIP_RF_NAME,
    IF_VIRTUAL_DEVICES_NAME,
)
IF_PRIMARY: Final[tuple[str, ...]] = (IF_HMIP_RF_NAME, IF_BIDCOS_RF_NAME)

NO_CACHE_ENTRY: Final = "NO_CACHE_ENTRY"

RELEVANT_INIT_PARAMETERS: Final[tuple[str, ...]] = (
    EVENT_CONFIG_PENDING,
    EVENT_STICKY_UN_REACH,
    EVENT_UN_REACH,
)

# virtual remotes device_types
HM_VIRTUAL_REMOTE_TYPES: Final[tuple[str, ...]] = (
    "HM-RCV-50",
    "HMW-RCV-50",
    "HmIP-RCV-50",
)

HM_VIRTUAL_REMOTE_ADDRESSES: Final[tuple[str, ...]] = (
    "BidCoS-RF",
    "HMW-RCV-50",
    "HmIP-RCV-1",
)

# dict with binary_sensor relevant value lists and the corresponding TRUE value
BINARY_SENSOR_TRUE_VALUE_DICT_FOR_VALUE_LIST: Final[dict[tuple[str, ...], str]] = {
    ("CLOSED", "OPEN"): "OPEN",
    ("DRY", "RAIN"): "RAIN",
    ("STABLE", "NOT_STABLE"): "NOT_STABLE",
}

PG_BIDCOS_RF: Final = "BidCos-RF"
PG_BIDCOS_WIRED: Final = "BidCos-Wired"
PG_HMIP_RF: Final = "HmIP-RF"
PG_HMIP_WIRED: Final = "HmIP-Wired"
PG_UNKNOWN: Final = "unknown"
PG_VIRTUAL_DEVICES: Final = "VirtualDevices"


class HmBackend(StrEnum):
    """Enum with supported hahomematic backends."""

    CCU = "CCU"
    HOMEGEAR = "Homegear"
    PYDEVCCU = "PyDevCCU"


class HmCallSource(StrEnum):
    """Enum with sources for calls."""

    HA_INIT: Final = "ha_init"
    HM_INIT: Final = "hm_init"
    MANUAL_OR_SCHEDULED: Final = "manual_or_scheduled"


class HmDataOperationResult(IntEnum):
    """Enum with data operation results."""

    LOAD_FAIL: Final = 0
    LOAD_SUCCESS: Final = 1
    SAVE_FAIL: Final = 10
    SAVE_SUCCESS: Final = 11
    NO_LOAD: Final = 20
    NO_SAVE: Final = 21


class HmDeviceFirmwareState(StrEnum):
    """Enum with homematic device firmware states."""

    UP_TO_DATE: Final = "UP_TO_DATE"
    LIVE_UP_TO_DATE: Final = "LIVE_UP_TO_DATE"
    NEW_FIRMWARE_AVAILABLE: Final = "NEW_FIRMWARE_AVAILABLE"
    LIVE_NEW_FIRMWARE_AVAILABLE: Final = "LIVE_NEW_FIRMWARE_AVAILABLE"
    DELIVER_FIRMWARE_IMAGE: Final = "DELIVER_FIRMWARE_IMAGE"
    LIVE_DELIVER_FIRMWARE_IMAGE: Final = "LIVE_DELIVER_FIRMWARE_IMAGE"
    READY_FOR_UPDATE: Final = "READY_FOR_UPDATE"
    DO_UPDATE_PENDING: Final = "DO_UPDATE_PENDING"
    PERFORMING_UPDATE: Final = "PERFORMING_UPDATE"


class HmEntityUsage(StrEnum):
    """Enum with information about usage in Home Assistant."""

    CE_PRIMARY: Final = "ce_primary"
    CE_SECONDARY: Final = "ce_secondary"
    CE_VISIBLE: Final = "ce_visible"
    ENTITY: Final = "entity"
    EVENT: Final = "event"
    NO_CREATE: Final = "entity_no_create"


class HmEventType(StrEnum):
    """Enum with hahomematic event types."""

    DEVICE_AVAILABILITY: Final = "homematic.device_availability"
    DEVICE_ERROR: Final = "homematic.device_error"
    IMPULSE: Final = "homematic.impulse"
    INTERFACE: Final = "homematic.interface"
    KEYPRESS: Final = "homematic.keypress"


class HmForcedDeviceAvailability(StrEnum):
    """Enum with hahomematic event types."""

    FORCE_FALSE: Final = "forced_not_available"
    FORCE_TRUE: Final = "forced_available"
    NOT_SET: Final = "not_set"


class HmManufacturer(StrEnum):
    """Enum with hahomematic system events."""

    EQ3 = "eQ-3"
    HB = "Homebrew"
    MOEHLENHOFF = "Möhlenhoff"


class HmPlatform(StrEnum):
    """Enum with platforms relevant for Home Assistant."""

    ACTION: Final = "action"
    BINARY_SENSOR: Final = "binary_sensor"
    BUTTON: Final = "button"
    CLIMATE: Final = "climate"
    COVER: Final = "cover"
    EVENT: Final = "event"
    HUB_BINARY_SENSOR: Final = "hub_binary_sensor"
    HUB_BUTTON: Final = "hub_button"
    HUB_NUMBER: Final = "hub_number"
    HUB_SELECT: Final = "hub_select"
    HUB_SENSOR: Final = "hub_sensor"
    HUB_SWITCH: Final = "hub_switch"
    HUB_TEXT: Final = "hub_text"
    LIGHT: Final = "light"
    LOCK: Final = "lock"
    NUMBER: Final = "number"
    SELECT: Final = "select"
    SENSOR: Final = "sensor"
    SIREN: Final = "siren"
    SWITCH: Final = "switch"
    TEXT: Final = "text"
    UPDATE: Final = "update"


class HmProductGroup(StrEnum):
    """Enum with homematic product groups."""

    UNKNOWN: Final = "unknown"
    HMIPW: Final = "HmIP-Wired"
    HMIP: Final = "HmIP-RF"
    HMW: Final = "BidCos-Wired"
    HM: Final = "BidCos-RF"
    VIRTUAL: Final = "VirtualDevices"


class HmInterface(StrEnum):
    """Enum with homematic product groups."""

    HMIP: Final = IF_HMIP_RF_NAME
    HMW: Final = IF_BIDCOS_WIRED_NAME
    HM: Final = IF_BIDCOS_RF_NAME
    VIRTUAL: Final = IF_VIRTUAL_DEVICES_NAME


class HmInterfaceEventType(StrEnum):
    """Enum with hahomematic event types."""

    CALLBACK: Final = "callback"
    PINGPONG: Final = "pingpong"
    PROXY: Final = "proxy"


class HmProxyStatus(Enum):
    """Enum with proxy handling results."""

    INIT_FAILED: Final = 0
    INIT_SUCCESS: Final = 1
    DE_INIT_FAILED: Final = 4
    DE_INIT_SUCCESS: Final = 8
    DE_INIT_SKIPPED: Final = 16


class HmSystemEvent(StrEnum):
    """Enum with hahomematic system events."""

    DELETE_DEVICES = "deleteDevices"
    DEVICES_CREATED = "devicesCreated"
    ERROR = "error"
    HUB_REFRESHED = "hubEntityRefreshed"
    LIST_DEVICES = "listDevices"
    NEW_DEVICES = "newDevices"
    REPLACE_DEVICE = "replaceDevice"
    RE_ADDED_DEVICE = "readdedDevice"
    UPDATE_DEVICE = "updateDevice"


class HmSysvarType(StrEnum):
    """Enum for homematic sysvar types."""

    ALARM = "ALARM"
    HM_FLOAT = "FLOAT"
    HM_INTEGER = "INTEGER"
    LIST = "LIST"
    LOGIC = "LOGIC"
    NUMBER = "NUMBER"
    STRING = "STRING"


class HmType(StrEnum):
    """Enum for homematic parameter types."""

    ACTION = "ACTION"  # Usually buttons, send Boolean to trigger
    BOOL = "BOOL"
    ENUM = "ENUM"
    FLOAT = "FLOAT"
    INTEGER = "INTEGER"
    STRING = "STRING"


AVAILABLE_HM_PLATFORMS: Final[tuple[HmPlatform, ...]] = (
    HmPlatform.BINARY_SENSOR,
    HmPlatform.BUTTON,
    HmPlatform.CLIMATE,
    HmPlatform.COVER,
    HmPlatform.EVENT,
    HmPlatform.LIGHT,
    HmPlatform.LOCK,
    HmPlatform.NUMBER,
    HmPlatform.SELECT,
    HmPlatform.SENSOR,
    HmPlatform.SIREN,
    HmPlatform.SWITCH,
    HmPlatform.TEXT,
    HmPlatform.UPDATE,
)

AVAILABLE_HM_HUB_PLATFORMS: Final[tuple[HmPlatform, ...]] = (
    HmPlatform.HUB_BINARY_SENSOR,
    HmPlatform.HUB_BUTTON,
    HmPlatform.HUB_NUMBER,
    HmPlatform.HUB_SELECT,
    HmPlatform.HUB_SENSOR,
    HmPlatform.HUB_SWITCH,
    HmPlatform.HUB_TEXT,
)

ENTITY_EVENTS: Final = (
    HmEventType.IMPULSE,
    HmEventType.KEYPRESS,
)
