# LG S90TR Soundbar Streaming & Wake Controller

Python library and CLI for controlling the power state and audio streaming of the **LG S90TR 5.1 Dolby Atmos Soundbar** over local Wi-Fi / Ethernet.

Designed as the audio playback backend for Raspberry Pi NFC/RFID music players.

---

## Features

- **Direct IP Wake-on-Demand:** Wakes the soundbar from standby / sleep over the network using LG's Temescal protocol (`port 9741`) before starting playback.
- **Fast Google Cast Playback:** Connects directly via IP to the soundbar's Cast receiver (`port 8009`) without mDNS discovery latency.
- **Unified Controller:** `wake_and_play(url_or_path)` handles waking the speaker, waiting for readiness, setting volume, and launching the stream.
- **CLI Utilities:** Easy commands for testing, power management, volume, and playback.

---

## Network Setup

- **Soundbar IP:** `192.168.1.41` (Static DHCP Reservation recommended)
- **Soundbar MAC:** `F4:14:BF:00:55:DA`
- **Cast Port:** `8009` (TLS CastV2)
- **Temescal Control Port:** `9741`

---

## Installation

Using [uv](https://docs.astral.sh/uv/):

```bash
cd /home/vega/Documents/git/local/s90_tr_streaming
uv sync
```

---

## CLI Usage

```bash
# Check power status and volume
uv run s90 status

# Wake up the soundbar
uv run s90 wake

# Put soundbar into standby / sleep
uv run s90 sleep

# Set volume (0-100)
uv run s90 volume 25

# Stream local audio file or web URL (automatically wakes speaker if asleep)
uv run s90 play test_tone.mp3
uv run s90 play http://example.com/audio.mp3

# Run the test tone
uv run s90 test
```

---

## Python API Usage

```python
from s90_tr_streaming import S90TRController

controller = S90TRController(ip="192.168.1.41")

# Check if soundbar is awake
if not controller.is_awake():
    print("Soundbar is sleeping. Waking up...")
    controller.wake()

# Set volume and stream audio
controller.wake_and_play(
    media_url="http://192.168.1.111:8000/my_playlist_track.mp3",
    volume=20,
    title="NFC Album Track"
)
```
