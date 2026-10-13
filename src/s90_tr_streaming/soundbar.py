import json
import socket
import struct
import time
from typing import Any, Dict, Optional
from Crypto.Cipher import AES

# Known cryptographic keys for LG Soundbar Temescal protocol
TEMESCAL_KEY = b'T^&*J%^7tr~4^%^&I(o%^!jIJ__+a0 k'
TEMESCAL_IV = b'\'%^Ur7gy$~t+f)%@'

DEFAULT_PORT = 9741

class LGSoundbarClient:
    """Client for controlling LG Soundbars via the Temescal protocol (port 9741)."""

    def __init__(self, host: str = "192.168.1.41", port: int = DEFAULT_PORT, timeout: float = 3.0):
        self.host = host
        self.port = port
        self.timeout = timeout

    def _encrypt(self, data: str) -> bytearray:
        padlen = 16 - (len(data) % 16)
        padded = data + (chr(padlen) * padlen)
        cipher = AES.new(TEMESCAL_KEY, AES.MODE_CBC, TEMESCAL_IV)
        encrypted = cipher.encrypt(padded.encode("utf-8"))
        length = len(encrypted)
        prelude = bytearray([0x10, 0x00, 0x00, 0x00, length])
        return prelude + encrypted

    def _decrypt(self, data: bytes) -> str:
        cipher = AES.new(TEMESCAL_KEY, AES.MODE_CBC, TEMESCAL_IV)
        decrypted = cipher.decrypt(data)
        padding_len = ord(decrypted[-1:])
        return str(decrypted[:-padding_len], "utf-8")

    def send_command(self, cmd_dict: Dict[str, Any], wait_response: bool = True) -> Optional[Dict[str, Any]]:
        """Send a JSON command packet and optionally wait for the first response."""
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(self.timeout)
        try:
            s.connect((self.host, self.port))
            packet = self._encrypt(json.dumps(cmd_dict))
            s.sendall(packet)

            if not wait_response:
                return None

            start = time.time()
            while time.time() - start < self.timeout:
                header = s.recv(1)
                if not header:
                    break
                if header[0] == 0x10:
                    length_bytes = s.recv(4)
                    if len(length_bytes) < 4:
                        break
                    length = struct.unpack(">I", length_bytes)[0]
                    enc_data = b""
                    while len(enc_data) < length:
                        chunk = s.recv(length - len(enc_data))
                        if not chunk:
                            break
                        enc_data += chunk
                    if len(enc_data) == length:
                        response_str = self._decrypt(enc_data)
                        try:
                            return json.loads(response_str)
                        except json.JSONDecodeError:
                            return None
            return None
        finally:
            s.close()

    def get_speaker_info(self) -> Dict[str, Any]:
        """Fetch general speaker info (power status, volume, mute, etc.)."""
        resp = self.send_command({"cmd": "get", "msg": "SPK_LIST_VIEW_INFO"})
        return resp.get("data", {}) if resp else {}

    def get_power_status(self) -> bool:
        """Return True if speaker is powered ON, False if in standby/sleep."""
        data = self.get_speaker_info()
        return bool(data.get("b_powerstatus", False))

    def set_power(self, power_on: bool, wait: bool = True, timeout: float = 5.0) -> bool:
        """Turn the speaker ON (power_on=True) or OFF/standby (power_on=False)."""
        current = self.get_power_status()
        if current == power_on:
            return True

        self.send_command(
            {"cmd": "set", "data": {"b_powerkey": power_on}, "msg": "SPK_LIST_VIEW_INFO"},
            wait_response=False,
        )

        if not wait:
            return True

        start = time.time()
        while time.time() - start < timeout:
            time.sleep(0.3)
            if self.get_power_status() == power_on:
                return True
        return self.get_power_status() == power_on

    def power_on(self, wait: bool = True, timeout: float = 5.0) -> bool:
        """Wake up the soundbar."""
        return self.set_power(True, wait=wait, timeout=timeout)

    def power_off(self, wait: bool = True, timeout: float = 5.0) -> bool:
        """Put the soundbar into sleep/standby."""
        return self.set_power(False, wait=wait, timeout=timeout)

    def set_volume(self, volume: int) -> None:
        """Set volume (0 - 100)."""
        volume = max(0, min(100, volume))
        self.send_command(
            {"cmd": "set", "data": {"i_vol": volume}, "msg": "SPK_LIST_VIEW_INFO"},
            wait_response=False,
        )

    def set_mute(self, mute: bool) -> None:
        """Mute or unmute speaker."""
        self.send_command(
            {"cmd": "set", "data": {"b_mute": mute}, "msg": "SPK_LIST_VIEW_INFO"},
            wait_response=False,
        )
