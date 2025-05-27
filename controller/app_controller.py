from core.niko_client import NikoClient, NikoDevice, NikoLocation, NikoError, Settings
from typing import List, Dict, Optional, Any

class AppController:
    """
    Mediates between core protocol logic and the UI.
    Handles devices, locations, system info, and settings.
    """

    def __init__(self, settings: Settings):
        self.settings = settings
        self.niko = NikoClient(settings.niko_ip)
        self.devices: List[NikoDevice] = []
        self.locations: List[NikoLocation] = []
        self.system_info: Dict[str, Any] = {}

    def refresh_data(self):
        """Fetches all data from the Niko controller (system info, devices, locations)."""
        self.system_info = self.niko.system_info()
        self.devices = self.niko.list_actions()
        self.locations = self.niko.list_locations()

    def get_devices_for_location(self, location_id: int) -> List[NikoDevice]:
        return [d for d in self.devices if d.location == location_id]

    def execute_device_action(self, device: NikoDevice, value1: Any):
        self.niko.execute_action(device.id, value1)

    def get_device_state_text(self, device: NikoDevice) -> str:
        """Returns a user-friendly status string for the device (for UI)."""
        return device.state_text

    def is_device_dimmable(self, device: NikoDevice) -> bool:
        return device.is_dimmable

    def is_device_socket(self, device: NikoDevice) -> bool:
        return device.is_socket

    def is_device_switch(self, device: NikoDevice) -> bool:
        return device.is_switch

    def update_settings(self, new_settings: Settings):
        """Update the app's settings and re-initialize the Niko client."""
        self.settings = new_settings
        self.niko = NikoClient(self.settings.niko_ip)