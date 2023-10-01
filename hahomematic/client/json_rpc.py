"""Implementation of an async json-rpc client."""
from __future__ import annotations

from datetime import datetime
from json import JSONDecodeError
import logging
import os
from pathlib import Path
import re
from ssl import SSLError
from typing import Any, Final

from aiohttp import (
    ClientConnectorCertificateError,
    ClientConnectorError,
    ClientError,
    ClientResponse,
    ClientSession,
)
import orjson

from hahomematic import central as hmcu, config
from hahomematic.const import (
    CONF_PASSWORD,
    CONF_USERNAME,
    DEFAULT_ENCODING,
    PATH_JSON_RPC,
    REGA_SCRIPT_FETCH_ALL_DEVICE_DATA,
    REGA_SCRIPT_GET_SERIAL,
    REGA_SCRIPT_PATH,
    REGA_SCRIPT_SET_SYSTEM_VARIABLE,
    REGA_SCRIPT_SYSTEM_VARIABLES_EXT_MARKER,
    HmSysvarType,
    ProgramData,
    SystemInformation,
    SystemVariableData,
)
from hahomematic.exceptions import AuthFailure, ClientException
from hahomematic.support import get_tls_context, parse_sys_var, reduce_args

_LOGGER: Final = logging.getLogger(__name__)

_CHANNEL_IDS: Final = "channelIds"
_HAS_EXT_MARKER: Final = "hasExtMarker"
_ID: Final = "id"
_IS_ACTIVE: Final = "isActive"
_IS_INTERNAL: Final = "isInternal"
_LAST_EXECUTE_TIME: Final = "lastExecuteTime"
_MAX_VALUE: Final = "maxValue"
_MIN_VALUE: Final = "minValue"
_NAME: Final = "name"
_INTERFACE: Final = "interface"
_P_ERROR: Final = "error"
_P_MESSAGE: Final = "message"
_P_RESULT: Final = "result"
_SESSION_ID: Final = "_session_id_"
_SERIAL: Final = "serial"
_TYPE: Final = "type"
_UNIT: Final = "unit"
_VALUE: Final = "value"
_VALUE_LIST: Final = "valueList"


class JsonRpcAioHttpClient:
    """Connection to CCU JSON-RPC Server."""

    def __init__(
        self,
        username: str,
        password: str,
        device_url: str,
        connection_state: hmcu.CentralConnectionState,
        client_session: ClientSession | None = None,
        tls: bool = False,
        verify_tls: bool = False,
    ) -> None:
        """Session setup."""
        self._client_session: Final = client_session
        self._connection_state: Final = connection_state
        self._username: Final = username
        self._password: Final = password
        self._tls: Final = tls
        self._tls_context: Final = get_tls_context(verify_tls) if tls else None
        self._url: Final = f"{device_url}{PATH_JSON_RPC}"
        self._script_cache: Final[dict[str, str]] = {}
        self._last_session_id_refresh: datetime | None = None
        self._session_id: str | None = None

    @property
    def is_activated(self) -> bool:
        """If session exists, then it is activated."""
        return self._session_id is not None

    async def _login_or_renew(self) -> bool:
        """Renew JSON-RPC session or perform login."""
        if not self.is_activated:
            self._session_id = await self._do_login()
            self._last_session_id_refresh = datetime.now()
            return self._session_id is not None
        if self._session_id:
            self._session_id = await self._do_renew_login(self._session_id)
        return self._session_id is not None

    async def _do_renew_login(self, session_id: str) -> str | None:
        """Renew JSON-RPC session or perform login."""
        if self._updated_within_seconds:
            return session_id
        method = "Session.renew"
        response = await self._do_post(
            session_id=session_id,
            method=method,
            extra_params={_SESSION_ID: session_id},
        )

        if response[_P_RESULT] and response[_P_RESULT] is True:
            self._last_session_id_refresh = datetime.now()
            _LOGGER.debug("DO_RENEW_LOGIN: Method: %s [%s]", method, session_id)
            return session_id

        return await self._do_login()

    @property
    def _updated_within_seconds(self) -> bool:
        """Check if session id has been updated within 90 seconds."""
        if self._last_session_id_refresh is None:
            return False
        delta = datetime.now() - self._last_session_id_refresh
        if delta.seconds < config.JSON_SESSION_AGE:
            return True
        return False

    async def _do_login(self) -> str | None:
        """Login to CCU and return session."""
        if not self._has_credentials:
            _LOGGER.warning("DO_LOGIN failed: No credentials set")
            return None

        session_id: str | None = None

        params = {
            CONF_USERNAME: self._username,
            CONF_PASSWORD: self._password,
        }
        method = "Session.login"
        response = await self._do_post(
            session_id=False,
            method=method,
            extra_params=params,
            use_default_params=False,
        )

        _LOGGER.debug("DO_LOGIN: Method: %s [%s]", method, session_id)

        if result := response[_P_RESULT]:
            session_id = result

        return session_id

    async def _post(
        self,
        method: str,
        extra_params: dict[str, str] | None = None,
        use_default_params: bool = True,
        keep_session: bool = True,
    ) -> dict[str, Any] | Any:
        """Reusable JSON-RPC POST function."""
        if keep_session:
            await self._login_or_renew()
            session_id = self._session_id
        else:
            session_id = await self._do_login()

        if not session_id:
            raise ClientException("Error while logging in")

        response = await self._do_post(
            session_id=session_id,
            method=method,
            extra_params=extra_params,
            use_default_params=use_default_params,
        )

        if extra_params:
            _LOGGER.debug("POST method: %s [%s]", method, extra_params)
        else:
            _LOGGER.debug("POST method: %s", method)

        if not keep_session:
            await self._do_logout(session_id=session_id)

        return response

    async def _post_script(
        self,
        script_name: str,
        extra_params: dict[str, str] | None = None,
        keep_session: bool = True,
    ) -> dict[str, Any] | Any:
        """Reusable JSON-RPC POST_SCRIPT function."""
        if keep_session:
            await self._login_or_renew()
            session_id = self._session_id
        else:
            session_id = await self._do_login()

        if not session_id:
            raise ClientException("Error while logging in")

        if (script := self._get_script(script_name=script_name)) is None:
            raise ClientException(f"Script file for {script_name} does not exist")

        if extra_params:
            for variable, value in extra_params.items():
                script = script.replace(f"##{variable}##", value)

        method = "ReGa.runScript"
        response = await self._do_post(
            session_id=session_id,
            method=method,
            extra_params={"script": script},
        )

        _LOGGER.debug("POST_SCRIPT: Method: %s [%s]", method, script_name)
        try:
            if not response[_P_ERROR]:
                response[_P_RESULT] = orjson.loads(response[_P_RESULT])
        finally:
            if not keep_session:
                await self._do_logout(session_id=session_id)

        return response

    def _get_script(self, script_name: str) -> str | None:
        """Return a script from the script cache. Load if required."""
        if script_name in self._script_cache:
            return self._script_cache[script_name]

        script_file = os.path.join(Path(__file__).resolve().parent, REGA_SCRIPT_PATH, script_name)
        if script := Path(script_file).read_text(encoding=DEFAULT_ENCODING):
            self._script_cache[script_name] = script
            return script
        return None

    async def _do_post(
        self,
        session_id: bool | str,
        method: str,
        extra_params: dict[str, str] | None = None,
        use_default_params: bool = True,
    ) -> dict[str, Any] | Any:
        """Reusable JSON-RPC POST function."""
        if not self._client_session:
            raise ClientException("ClientSession not initialized")
        if not self._has_credentials:
            raise ClientException("No credentials set")

        params = _get_params(session_id, extra_params, use_default_params)

        try:
            payload = orjson.dumps({"method": method, "params": params, "jsonrpc": "1.1", "id": 0})

            headers = {
                "Content-Type": "application/json",
                "Content-Length": str(len(payload)),
            }

            if (
                response := await self._client_session.post(
                    self._url,
                    data=payload,
                    headers=headers,
                    timeout=config.TIMEOUT,
                    ssl=self._tls_context,
                )
            ) is None:
                raise ClientException("POST method failed with no response")

            if response.status == 200:
                json_response = await self._get_json_reponse(response=response)

                if error := json_response[_P_ERROR]:
                    error_message = error[_P_MESSAGE]
                    message = f"POST method '{method}' failed: {error_message}"
                    _LOGGER.debug(message)
                    if error_message.startswith("access denied"):
                        raise AuthFailure(message)
                    raise ClientException(message)

                return json_response

            message = f"Status: {response.status}"
            json_response = await self._get_json_reponse(response=response)
            if error := json_response[_P_ERROR]:
                error_message = error[_P_MESSAGE]
                message = f"{message}: {error_message}"
            raise ClientException(message)
        except (AuthFailure, ClientException):
            await self.logout()
            raise
        except ClientConnectorCertificateError as cccerr:
            self.clear_session()
            message = f"ClientConnectorCertificateError[{cccerr}]"
            if self._tls is False and cccerr.ssl is True:
                message = (
                    f"{message}. Possible reason: 'Automatic forwarding to HTTPS' is enabled in backend, "
                    f"but this integration is not configured to use TLS"
                )
            raise ClientException(message) from cccerr
        except (ClientConnectorError, ClientError) as cce:
            self.clear_session()
            raise ClientException(cce) from cce
        except SSLError as sslerr:
            self.clear_session()
            raise ClientException(sslerr) from sslerr
        except (OSError, TypeError, Exception) as ex:
            self.clear_session()
            raise ClientException(ex) from ex

    async def _get_json_reponse(self, response: ClientResponse) -> dict[str, Any] | Any:
        """Return the json object from response."""
        try:
            return await response.json(encoding="utf-8")
        except ValueError as ver:
            _LOGGER.debug(
                "DO_POST: ValueError [%s] Unable to parse JSON. Trying workaround",
                reduce_args(args=ver.args),
            )
            # Workaround for bug in CCU
            return orjson.loads((await response.json(encoding="utf-8")).replace("\\", ""))

    async def logout(self) -> None:
        """Logout of CCU."""
        iid = "LOGOUT"
        try:
            await self._do_logout(self._session_id)
            self._connection_state.remove_issue(issuer=self, iid=iid)
        except ClientException as clex:
            self._handle_exception_log(iid=iid, exception=clex)

    async def _do_logout(self, session_id: str | None) -> None:
        """Logout of CCU."""
        if not session_id:
            _LOGGER.debug("DO_LOGOUT: Not logged in. Not logging out.")
            return

        method = "Session.logout"
        params = {_SESSION_ID: session_id}
        try:
            await self._do_post(
                session_id=session_id,
                method=method,
                extra_params=params,
            )
            _LOGGER.debug("DO_LOGOUT: Method: %s [%s]", method, session_id)
        finally:
            self.clear_session()

    @property
    def _has_credentials(self) -> bool:
        """Return if credentials are available."""
        return self._username is not None and self._username != "" and self._password is not None

    async def execute_program(self, pid: str) -> bool:
        """Execute a program on CCU / Homegear."""
        iid = "EXECUTE_PROGRAM"
        params = {
            _ID: pid,
        }
        try:
            response = await self._post("Program.execute", params)
            _LOGGER.debug("EXECUTE_PROGRAM: Executing a program")

            if json_result := response[_P_RESULT]:
                _LOGGER.debug(
                    "EXECUTE_PROGRAM: Result while executing program: %s",
                    str(json_result),
                )
            self._connection_state.remove_issue(issuer=self, iid=iid)
        except ClientException as clex:
            self._handle_exception_log(iid=iid, exception=clex, level=logging.WARNING)
            return False

        return True

    async def set_system_variable(self, name: str, value: Any) -> bool:
        """Set a system variable on CCU / Homegear."""
        iid = "SET_SYSTEM_VARIABLE"
        params = {
            _NAME: name,
            _VALUE: value,
        }
        try:
            if isinstance(value, bool):
                params[_VALUE] = int(value)
                response = await self._post("SysVar.setBool", params)
            elif isinstance(value, str):
                if re.findall("<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});", value):
                    _LOGGER.warning(
                        "SET_SYSTEM_VARIABLE failed: "
                        "Value (%s) contains html tags. This is not allowed",
                        value,
                    )
                    return False
                response = await self._post_script(
                    script_name=REGA_SCRIPT_SET_SYSTEM_VARIABLE, extra_params=params
                )
            else:
                response = await self._post("SysVar.setFloat", params)

            _LOGGER.debug("SET_SYSTEM_VARIABLE: Setting System variable")
            if json_result := response[_P_RESULT]:
                _LOGGER.debug(
                    "SET_SYSTEM_VARIABLE: Result while setting variable: %s",
                    str(json_result),
                )
            self._connection_state.remove_issue(issuer=self, iid=iid)
        except ClientException as clex:
            self._handle_exception_log(iid=iid, exception=clex, level=logging.WARNING)
            return False

        return True

    def clear_session(self) -> None:
        """Clear the current session."""
        self._session_id = None

    async def delete_system_variable(self, name: str) -> bool:
        """Delete a system variable from CCU / Homegear."""
        iid = "DELETE_SYSTEM_VARIABLE"
        params = {_NAME: name}
        try:
            response = await self._post(
                "SysVar.deleteSysVarByName",
                params,
            )

            _LOGGER.debug("DELETE_SYSTEM_VARIABLE: Getting System variable")
            if json_result := response[_P_RESULT]:
                deleted = json_result
                _LOGGER.debug("DELETE_SYSTEM_VARIABLE: Deleted: %s", str(deleted))
            self._connection_state.remove_issue(issuer=self, iid=iid)
        except ClientException as clex:
            self._handle_exception_log(iid=iid, exception=clex, level=logging.WARNING)
            return False

        return True

    async def get_system_variable(self, name: str) -> Any:
        """Get single system variable from CCU / Homegear."""
        iid = "GET_SYSTEM_VARIABLE"
        var = None

        try:
            params = {_NAME: name}
            response = await self._post(
                "SysVar.getValueByName",
                params,
            )

            _LOGGER.debug("GET_SYSTEM_VARIABLE: Getting System variable")
            if json_result := response[_P_RESULT]:
                # This does not yet support strings
                try:
                    var = float(json_result)
                except Exception:
                    var = json_result == "true"
            self._connection_state.remove_issue(issuer=self, iid=iid)
        except ClientException as clex:
            self._handle_exception_log(iid=iid, exception=clex, level=logging.WARNING)
            return None

        return var

    async def get_all_system_variables(self, include_internal: bool) -> list[SystemVariableData]:
        """Get all system variables from CCU / Homegear."""
        iid = "GET_ALL_SYSTEM_VARIABLES"
        variables: list[SystemVariableData] = []
        try:
            response = await self._post(
                "SysVar.getAll",
            )

            _LOGGER.debug("GET_ALL_SYSTEM_VARIABLES: Getting all system variables")
            if json_result := response[_P_RESULT]:
                ext_markers = await self._get_system_variables_ext_markers()
                for var in json_result:
                    is_internal = var[_IS_INTERNAL]
                    if include_internal is False and is_internal is True:
                        continue
                    var_id = var[_ID]
                    name = var[_NAME]
                    org_data_type = var[_TYPE]
                    raw_value = var[_VALUE]
                    if org_data_type == HmSysvarType.NUMBER:
                        data_type = (
                            HmSysvarType.HM_FLOAT if "." in raw_value else HmSysvarType.HM_INTEGER
                        )
                    else:
                        data_type = org_data_type
                    extended_sysvar = ext_markers.get(var_id, False)
                    unit = var[_UNIT]
                    value_list: list[str] | None = None
                    if val_list := var.get(_VALUE_LIST):
                        value_list = val_list.split(";")
                    try:
                        value = parse_sys_var(data_type=data_type, raw_value=raw_value)
                        max_value = None
                        if raw_max_value := var.get(_MAX_VALUE):
                            max_value = parse_sys_var(data_type=data_type, raw_value=raw_max_value)
                        min_value = None
                        if raw_min_value := var.get(_MIN_VALUE):
                            min_value = parse_sys_var(data_type=data_type, raw_value=raw_min_value)
                        variables.append(
                            SystemVariableData(
                                name=name,
                                data_type=data_type,
                                unit=unit,
                                value=value,
                                value_list=value_list,
                                max_value=max_value,
                                min_value=min_value,
                                extended_sysvar=extended_sysvar,
                            )
                        )
                    except ValueError as verr:
                        _LOGGER.warning(
                            "GET_ALL_SYSTEM_VARIABLES failed: "
                            "ValueError [%s] Failed to parse SysVar %s ",
                            reduce_args(args=verr.args),
                            name,
                        )
            self._connection_state.remove_issue(issuer=self, iid=iid)
        except ClientException as clex:
            self._handle_exception_log(iid=iid, exception=clex)

        return variables

    async def _get_system_variables_ext_markers(self) -> dict[str, Any]:
        """Get all system variables from CCU / Homegear."""
        iid = "GET_SYSTEM_VARIABLES_EXT_MARKERS"
        ext_markers: dict[str, Any] = {}

        try:
            response = await self._post_script(script_name=REGA_SCRIPT_SYSTEM_VARIABLES_EXT_MARKER)

            _LOGGER.debug("GET_SYSTEM_VARIABLES_EXT_MARKERS: Getting system variables ext markers")
            if json_result := response[_P_RESULT]:
                for data in json_result:
                    ext_markers[data[_ID]] = data[_HAS_EXT_MARKER]
            self._connection_state.remove_issue(issuer=self, iid=iid)
        except JSONDecodeError as jderr:
            self._handle_exception_log(
                iid=iid,
                exception=jderr,
                extra_msg="This leads to a missing assignment of extended system variables.",
            )
        return ext_markers

    async def get_all_channel_ids_room(self) -> dict[str, set[str]]:
        """Get all channel_ids per room from CCU / Homegear."""
        iid = "GET_ALL_CHANNEL_IDS_PER_ROOM"
        channel_ids_room: dict[str, set[str]] = {}

        try:
            response = await self._post(
                "Room.getAll",
            )

            _LOGGER.debug("GET_ALL_CHANNEL_IDS_PER_ROOM: Getting all rooms")
            if json_result := response[_P_RESULT]:
                for room in json_result:
                    room_id = room[_ID]
                    room_name = room[_NAME]
                    if room_id not in channel_ids_room:
                        channel_ids_room[room_id] = set()
                    channel_ids_room[room_id].add(room_name)
                    for channel_id in room[_CHANNEL_IDS]:
                        if channel_id not in channel_ids_room:
                            channel_ids_room[channel_id] = set()
                        channel_ids_room[channel_id].add(room_name)
            self._connection_state.remove_issue(issuer=self, iid=iid)
        except ClientException as clex:
            self._handle_exception_log(iid=iid, exception=clex, multiple_logs=False)
            return {}

        return channel_ids_room

    async def get_all_channel_ids_function(self) -> dict[str, set[str]]:
        """Get all channel_ids per function from CCU / Homegear."""
        iid = "GET_ALL_CHANNEL_IDS_PER_FUNCTION"
        channel_ids_function: dict[str, set[str]] = {}

        try:
            response = await self._post(
                "Subsection.getAll",
            )

            _LOGGER.debug("GET_ALL_CHANNEL_IDS_PER_FUNCTION: Getting all functions")
            if json_result := response[_P_RESULT]:
                for function in json_result:
                    function_id = function[_ID]
                    function_name = function[_NAME]
                    if function_id not in channel_ids_function:
                        channel_ids_function[function_id] = set()
                    channel_ids_function[function_id].add(function_name)
                    for channel_id in function[_CHANNEL_IDS]:
                        if channel_id not in channel_ids_function:
                            channel_ids_function[channel_id] = set()
                        channel_ids_function[channel_id].add(function_name)
            self._connection_state.remove_issue(issuer=self, iid=iid)
        except ClientException as clex:
            self._handle_exception_log(iid=iid, exception=clex, multiple_logs=False)
            return {}

        return channel_ids_function

    async def get_device_details(self) -> list[dict[str, Any]]:
        """Get the device details of the backend."""
        iid = "GET_DEVICE_DETAILS"
        device_details: list[dict[str, Any]] = []

        try:
            response = await self._post(
                method="Device.listAllDetail",
            )

            _LOGGER.debug("GET_DEVICE_DETAILS: Getting the device details")
            if json_result := response[_P_RESULT]:
                device_details = json_result
            self._connection_state.remove_issue(issuer=self, iid=iid)
        except ClientException as clex:
            self._handle_exception_log(iid=iid, exception=clex, multiple_logs=False)
            return []

        return device_details

    async def get_all_device_data(self, interface: str) -> dict[str, Any]:
        """Get the all device data of the backend."""
        iid = f"GET_ALL_DEVICE_DATA for {interface}"
        all_device_data: dict[str, dict[str, dict[str, Any]]] = {}
        params = {
            _INTERFACE: interface,
        }
        try:
            response = await self._post_script(
                script_name=REGA_SCRIPT_FETCH_ALL_DEVICE_DATA, extra_params=params
            )

            _LOGGER.debug(
                "GET_ALL_DEVICE_DATA: Getting all device data for interface %s", interface
            )
            if json_result := response[_P_RESULT]:
                all_device_data = json_result
            self._connection_state.remove_issue(issuer=self, iid=iid)
        except ClientException as clex:
            self._handle_exception_log(
                iid=iid,
                exception=clex,
            )
        except JSONDecodeError as jderr:
            self._handle_exception_log(
                iid=iid,
                exception=jderr,
                extra_msg=f"Using fallback. This leeds to a higher DutyCycle during Integration startup for interface {interface}",
                multiple_logs=False,
                level=logging.WARNING,
            )

        return all_device_data

    async def get_all_programs(self, include_internal: bool) -> list[ProgramData]:
        """Get the all programs of the backend."""
        iid = "GET_ALL_PROGRAMS"
        all_programs: list[ProgramData] = []

        try:
            response = await self._post(
                method="Program.getAll",
            )

            _LOGGER.debug("GET_ALL_PROGRAMS: Getting all programs")
            if json_result := response[_P_RESULT]:
                for prog in json_result:
                    is_internal = prog[_IS_INTERNAL]
                    if include_internal is False and is_internal is True:
                        continue
                    pid = prog[_ID]
                    name = prog[_NAME]
                    is_active = prog[_IS_ACTIVE]
                    last_execute_time = prog[_LAST_EXECUTE_TIME]

                    all_programs.append(
                        ProgramData(
                            pid=pid,
                            name=name,
                            is_active=is_active,
                            is_internal=is_internal,
                            last_execute_time=last_execute_time,
                        )
                    )
            self._connection_state.remove_issue(issuer=self, iid=iid)
        except ClientException as clex:
            self._handle_exception_log(iid=iid, exception=clex)
            return []

        return all_programs

    async def get_system_information(self) -> SystemInformation:
        """Get system information of the backend."""
        iid = "GET_SYSTEM_INFORMATION"
        try:
            if (auth_enabled := await self._get_auth_enabled()) is not None and (
                system_information := SystemInformation(
                    auth_enabled=auth_enabled,
                    available_interfaces=await self._get_available_interfaces(),
                    https_redirect_enabled=await self._get_https_redirect_enabled(),
                    serial=await self._get_serial(),
                )
            ):
                self._connection_state.remove_issue(issuer=self, iid=iid)
                return system_information
        except ClientException as clex:
            self._handle_exception_log(iid=iid, exception=clex, multiple_logs=False)
            raise
        return SystemInformation()

    async def _get_auth_enabled(self) -> bool | None:
        """Get the auth_enabled flag of the backend."""
        _LOGGER.debug("GET_AUTH_ENABLED: Getting the flag auth_enabled")

        response = await self._post(method="CCU.getAuthEnabled")
        if (json_result := response[_P_RESULT]) is not None:
            return bool(json_result)
        return None

    async def _get_available_interfaces(self) -> list[str]:
        """Get all available interfaces from CCU / Homegear."""
        _LOGGER.debug("GET_AVAILABLE_INTERFACES: Getting all available interfaces")

        interfaces: list[str] = []
        response = await self._post(
            "Interface.listInterfaces",
        )

        if json_result := response[_P_RESULT]:
            for interface in json_result:
                interfaces.append(interface[_NAME])
        return interfaces

    async def _get_https_redirect_enabled(self) -> bool | None:
        """Get the auth_enabled flag of the backend."""
        _LOGGER.debug("GET_HTTPS_REDIRECT_ENABLED: Getting the flag https_redirect_enabled")

        response = await self._post(method="CCU.getHttpsRedirectEnabled")
        if (json_result := response[_P_RESULT]) is not None:
            return bool(json_result)
        return None

    async def _get_serial(self) -> str | None:
        """Get the serial of the backend."""
        _LOGGER.debug("GET_SERIAL: Getting the backend serial")
        try:
            response = await self._post_script(script_name=REGA_SCRIPT_GET_SERIAL)

            if json_result := response[_P_RESULT]:
                serial: str = json_result[_SERIAL]
                if len(serial) > 10:
                    serial = serial[-10:]
                return serial
        except JSONDecodeError as jderr:
            raise ClientException(jderr) from jderr
        return None

    def _handle_exception_log(
        self,
        iid: str,
        exception: Exception,
        level: int = logging.ERROR,
        extra_msg: str = "",
        multiple_logs: bool = True,
    ) -> None:
        """Handle Exception and derivates logging."""
        self._connection_state.handle_exception_log(
            issuer=self,
            iid=iid,
            exception=exception,
            logger=_LOGGER,
            level=level,
            extra_msg=extra_msg,
            multiple_logs=multiple_logs,
        )


def _get_params(
    session_id: bool | str,
    extra_params: dict[str, Any] | None,
    use_default_params: bool,
) -> dict[str, Any]:
    """Add additional params to default prams."""
    params: dict[str, Any] = {_SESSION_ID: session_id} if use_default_params else {}
    if extra_params:
        params.update(extra_params)
    return params
