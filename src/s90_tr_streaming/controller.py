import time
from typing import Optional
from .soundbar import LGSoundbarClient
from .cast import CastAudioStreamer

class S90TRController:
    """Unified controller for LG S90TR soundbar power management and audio streaming."""

    def __init__(self, ip: str = "192.168.1.41"):
        self.ip = ip
        self.soundbar = LGSoundbarClient(host=ip)
        self.cast = CastAudioStreamer(ip=ip)

    def is_awake(self) -> bool:
        return self.soundbar.get_power_status()

    def wake(self, timeout: float = 5.0) -> bool:
        if self.is_awake():
            return True
        return self.soundbar.power_on(wait=True, timeout=timeout)

    def sleep(self, timeout: float = 5.0) -> bool:
        if not self.is_awake():
            return True
        return self.soundbar.power_off(wait=True, timeout=timeout)

    def wake_and_play(
        self,
        media_url: str,
        content_type: str = "audio/mp3",
        title: Optional[str] = None,
        volume: Optional[int] = None,
    ) -> None:
        """Ensure speaker is awake, optionally set volume, and stream audio."""
        if not self.is_awake():
            print(f"[S90TR] Speaker is currently asleep. Sending wake command...")
            woken = self.wake()
            if not woken:
                print(f"[S90TR] Warning: Wake command sent but power status did not confirm within timeout.")
            else:
                print(f"[S90TR] Speaker awake!")
                time.sleep(0.5)

        if volume is not None:
            self.soundbar.set_volume(volume)

        print(f"[S90TR] Streaming: {media_url}")
        self.cast.play_url(media_url, content_type=content_type, title=title)
