"""Interfaces with Alarm.com cameras."""

from __future__ import annotations

import logging
from typing import Any

import pyalarmdotcomajax as pyadc
from homeassistant.components.camera import Camera, CameraEntityFeature
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import DiscoveryInfoType

from .const import DATA_HUB, DOMAIN
from .entity import device_info_fn
from .hub import AlarmHub
from .util import cleanup_orphaned_entities_and_devices

log = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Set up Alarm.com camera entities."""

    hub: AlarmHub = hass.data[DOMAIN][config_entry.entry_id][DATA_HUB]

    entities = [AdcCameraEntity(hub=hub, resource_id=device.id) for device in hub.api.cameras]
    async_add_entities(entities)

    current_entity_ids = {entity.entity_id for entity in entities}
    current_unique_ids = {uid for uid in (entity.unique_id for entity in entities) if uid is not None}
    await cleanup_orphaned_entities_and_devices(
        hass,
        config_entry,
        current_entity_ids,
        current_unique_ids,
        "camera",
    )


class AdcCameraEntity(Camera):
    """Alarm.com camera entity backed by the WebRTC token endpoint."""

    _attr_has_entity_name = True
    _attr_supported_features = CameraEntityFeature.ON_OFF
    _attr_should_poll = False

    def __init__(self, hub: AlarmHub, resource_id: str) -> None:
        """Initialize the camera entity."""
        super().__init__()
        self.hub = hub
        self.resource_id = resource_id
        self.controller = hub.api.cameras
        self._webrtc_config: dict[str, Any] | None = None

        self._attr_unique_id = resource_id
        self._attr_name = None
        self._attr_device_info = device_info_fn(hub, resource_id, None)
        self._update_base_state()

    @property
    def is_on(self) -> bool:
        """Return whether a current WebRTC config is cached."""
        return self._webrtc_config is not None

    @property
    def available(self) -> bool:
        """Return whether the camera entity is available."""
        camera = self.controller.get(self.resource_id)
        return bool(
            self.hub.available
            and camera is not None
            and not camera.attributes.loading
            and not camera.attributes.is_unreachable
        )

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return extra state attributes."""
        camera = self.controller.get(self.resource_id)
        attrs: dict[str, Any] = {
            "resource_id": self.resource_id,
            "webrtc_config": self._webrtc_config,
        }
        if camera is not None:
            attrs.update(
                {
                    "firmware_version": camera.attributes.firmware_version,
                    "public_ip": camera.attributes.public_ip,
                    "private_ip": camera.attributes.private_ip,
                    "is_malfunctioning": camera.attributes.is_malfunctioning,
                    "is_unreachable": camera.attributes.is_unreachable,
                }
            )
        return attrs

    @property
    def brand(self) -> str:
        """Return the camera brand."""
        return "Alarm.com"

    async def async_added_to_hass(self) -> None:
        """Register callbacks."""
        self.async_on_remove(self.hub.api.subscribe(self.event_handler, self.resource_id))

    @callback
    def _update_base_state(self) -> None:
        """Refresh static state pulled from the current resource cache."""
        camera = self.controller.get(self.resource_id)
        if camera is None:
            return

        self._attr_is_streaming = self._webrtc_config is not None
        self._attr_is_recording = False
        self._attr_name = None
        self._attr_device_info = device_info_fn(self.hub, self.resource_id, None)

    @callback
    def event_handler(self, message: pyadc.EventBrokerMessage) -> None:
        """Handle Alarm.com resource updates."""
        if message.topic in [
            pyadc.EventBrokerTopic.RESOURCE_ADDED,
            pyadc.EventBrokerTopic.RESOURCE_UPDATED,
            pyadc.EventBrokerTopic.CONNECTION_EVENT,
        ]:
            self._update_base_state()
            self.async_write_ha_state()
        elif message.topic == pyadc.EventBrokerTopic.RESOURCE_DELETED:
            self.hass.async_create_task(self.async_remove(force_remove=True))

    async def async_turn_on(self) -> None:
        """Fetch fresh WebRTC tokens for this camera."""
        try:
            self._webrtc_config = await self.controller.get_live_stream_info(self.resource_id)
        except (pyadc.AuthenticationException, pyadc.ServiceUnavailable, pyadc.UnexpectedResponse) as err:
            log.error("Failed to fetch Alarm.com camera stream info for %s: %s", self.resource_id, err)
            self._webrtc_config = None
        self._update_base_state()
        self.async_write_ha_state()

    async def async_turn_off(self) -> None:
        """Discard cached WebRTC tokens."""
        self._webrtc_config = None
        self._update_base_state()
        self.async_write_ha_state()

    async def async_camera_image(self, width: int | None = None, height: int | None = None) -> bytes | None:
        """Return a still image from the camera.

        Alarm.com does not currently expose a snapshot path through this integration.
        """
        return None
