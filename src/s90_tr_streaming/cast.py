import time
from typing import Optional
from uuid import UUID
import pychromecast

SOUNDBAR_IP = "192.168.1.41"
SOUNDBAR_PORT = 8009
SOUNDBAR_UUID = UUID("af87a814-eabb-0a54-9e90-aca39827ec2d")
SOUNDBAR_MODEL = "LG S90T Soundbar"
SOUNDBAR_NAME = "LG_Speaker_S90TR"

class CastAudioStreamer:
    """Google Cast client for streaming audio to LG S90TR."""

    def __init__(
        self,
        ip: str = SOUNDBAR_IP,
        port: int = SOUNDBAR_PORT,
        uuid: UUID = SOUNDBAR_UUID,
        model: str = SOUNDBAR_MODEL,
        name: str = SOUNDBAR_NAME,
    ):
        self.ip = ip
        self.port = port
        self.uuid = uuid
        self.model = model
        self.name = name
        self._cast: Optional[pychromecast.Chromecast] = None

    def connect(self, timeout: float = 10.0) -> pychromecast.Chromecast:
        """Connect directly to the Cast device via IP."""
        if self._cast is not None and self._cast.socket_client.is_connected:
            return self._cast

        cast = pychromecast.get_chromecast_from_host(
            (self.ip, self.port, self.uuid, self.model, self.name),
            timeout=timeout,
        )
        cast.wait()
        self._cast = cast
        return cast

    def play_url(
        self,
        media_url: str,
        content_type: str = "audio/mp3",
        title: Optional[str] = None,
        stream_type: str = "BUFFERED",
        block_until_active: bool = True,
        timeout: float = 10.0,
    ) -> None:
        """Stream an audio URL directly to the soundbar."""
        cast = self.connect(timeout=timeout)
        mc = cast.media_controller
        mc.play_media(
            media_url,
            content_type=content_type,
            title=title or media_url.split("/")[-1],
            stream_type=stream_type,
            autoplay=True,
        )
        if block_until_active:
            mc.block_until_active(timeout=timeout)

    def pause(self) -> None:
        if self._cast and self._cast.media_controller:
            self._cast.media_controller.pause()

    def resume(self) -> None:
        if self._cast and self._cast.media_controller:
            self._cast.media_controller.play()

    def stop(self) -> None:
        if self._cast and self._cast.media_controller:
            self._cast.media_controller.stop()

    def disconnect(self) -> None:
        if self._cast is not None:
            self._cast.disconnect()
            self._cast = None
