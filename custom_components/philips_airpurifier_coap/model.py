"""Type definitions for Philips AirPurifier integration."""
from __future__ import annotations

from typing import Any, Callable, TypedDict
from xmlrpc.client import boolean

from homeassistant.helpers.typing import StateType


DeviceStatus = dict[str, Any]


class _SensorDescription(TypedDict):
    """Mandatory attributes for a sensor description."""

    label: str


class SensorDescription(_SensorDescription, total=False):
    """Sensor description class."""

    device_class: str
    icon: str
    unit: str
    state_class: str
    value: Callable[[Any, DeviceStatus], StateType]


class FilterDescription(TypedDict):
    """Filter description class."""

    prefix: str
    postfix: str


class SwitchDescription(TypedDict):
    """Switch description class."""

    icon: str
    label: str
    entity_category: str


class LightDescription(TypedDict):
    """Light description class."""

    icon: str
    label: str
    entity_category: str