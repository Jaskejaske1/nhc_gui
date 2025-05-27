import socket
import json
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass

class NikoError(Exception):
    def __init__(self, code: int, cmd: str, message: Optional[str] = None):
        self.code = code
        self.cmd = cmd
        self.message = message or f"Niko protocol error {code} (cmd={cmd})"
        super().__init__(self.message)

@dataclass
class Settings:
    """Holds app settings (expandable for settings panel)."""
    niko_ip: str = "192.168.1.10"
    # Add more fields as needed (port, refresh rate, etc.)

class NikoDevice:
    def __init__(self, id_: int, name: str, type_: int, location: int, value1: Any):
        self.id = id_
        self.name = name
        self.type = type_
        self.location = location
        self.value1 = value1

    @property
    def is_dimmable(self) -> bool:
        return self.type == 2

    @property
    def is_socket(self) -> bool:
        # You may refine this logic if you wish to distinguish sockets from switches
        return self.type == 1 and "stopcontact" in self.name.lower()

    @property
    def is_switch(self) -> bool:
        return self.type == 1 and not self.is_socket

    # In state_text property of NikoDevice (core/niko_client.py)
    @property
    def state_text(self) -> str:
        if self.is_dimmable:
            percent = int(self.value1)
            return f"{percent}%"
        elif self.is_socket or self.is_switch:
            return "ON" if self.value1 else "OFF"
        return str(self.value1)

    def __repr__(self):
        return (
            f"NikoDevice(id={self.id}, name={self.name}, type={self.type}, "
            f"location={self.location}, value1={self.value1})"
        )

class NikoLocation:
    def __init__(self, id_: int, name: str):
        self.id = id_
        self.name = name

    def __repr__(self):
        return f"NikoLocation(id={self.id}, name={self.name})"

class NikoClient:
    def __init__(self, ip: str, port: int = 8000, timeout: float = 5.0):
        self.ip = ip
        self.port = port
        self.timeout = timeout

    def _send_cmd(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        if "cmd" not in payload or not isinstance(payload["cmd"], str):
            raise ValueError("'cmd' field must be present and a string")
        data = (json.dumps(payload) + "\r\n").encode("utf-8")
        with socket.create_connection((self.ip, self.port), timeout=self.timeout) as sock:
            sock.settimeout(self.timeout)
            sock.sendall(data)
            resp = b""
            while True:
                chunk = sock.recv(4096)
                if not chunk:
                    break
                resp += chunk
                if b"\r" in chunk or b"\n" in chunk:
                    break
        try:
            resp_json = json.loads(resp.strip().decode("utf-8"))
        except Exception as e:
            raise RuntimeError(f"Could not decode controller response: {resp!r}") from e
        data_field = resp_json.get("data", {})
        if isinstance(data_field, dict) and "error" in data_field and data_field["error"] != 0:
            raise NikoError(data_field["error"], resp_json.get("cmd", ""))
        return resp_json

    def system_info(self) -> Dict[str, Any]:
        return self._send_cmd({"cmd": "systeminfo"}).get("data", {})

    def list_actions(self) -> List[NikoDevice]:
        data = self._send_cmd({"cmd": "listactions"}).get("data", [])
        return [
            NikoDevice(
                id_=d.get("id"),
                name=d.get("name"),
                type_=d.get("type"),
                location=d.get("location"),
                value1=d.get("value1"),
            )
            for d in data
        ]

    def list_locations(self) -> List[NikoLocation]:
        data = self._send_cmd({"cmd": "listlocations"}).get("data", [])
        return [
            NikoLocation(id_=d.get("id"), name=d.get("name"))
            for d in data
        ]

    def execute_action(self, action_id: Union[int, str], value1: Union[int, str], **kwargs) -> None:
        payload = {
            "cmd": "executeactions",
            "actions": [{"id": action_id, "value1": int(value1)}]
        }
        payload.update(kwargs)
        self._send_cmd(payload)

    def raw_command(self, cmd: str, **fields):
        payload = {"cmd": cmd}
        payload.update(fields)
        return self._send_cmd(payload)