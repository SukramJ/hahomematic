"""
Module for entities implemented using the
switch platform (https://www.home-assistant.io/integrations/switch/).
"""
from __future__ import annotations

import logging
from typing import Any

from hahomematic.const import TYPE_ACTION, HmPlatform
import hahomematic.device as hm_device
from hahomematic.entity import GenericEntity

_LOGGER = logging.getLogger(__name__)


class HmSwitch(GenericEntity[bool]):
    """
    Implementation of a switch.
    This is a default platform that gets automatically generated.
    """

    def __init__(
        self,
        device: hm_device.HmDevice,
        unique_id: str,
        address: str,
        parameter: str,
        parameter_data: dict[str, Any],
    ):
        super().__init__(
            device=device,
            unique_id=unique_id,
            address=address,
            parameter=parameter,
            parameter_data=parameter_data,
            platform=HmPlatform.SWITCH,
        )

    @property
    def state(self) -> bool | None:
        """Get the state of the entity."""
        if self._type == TYPE_ACTION:
            return False
        return self._state

    async def turn_on(self) -> None:
        """Turn the switch on."""
        await self.send_value(True)

    async def turn_off(self) -> None:
        """Turn the switch off."""
        await self.send_value(False)

    async def set_state(self, value: bool) -> None:
        """Set the state of the entity."""
        if self._type == TYPE_ACTION:
            await self.send_value(True)
        else:
            await self.send_value(value)
