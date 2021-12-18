"""Test the HaHomematic."""
from typing import Any
from unittest.mock import patch

import pytest


@pytest.mark.asyncio
async def test_central(central, loop) -> None:
    """Test we get the central."""
    assert central
    assert len(central.hm_devices) == 294
    assert len(central.hm_entities) == 2650
