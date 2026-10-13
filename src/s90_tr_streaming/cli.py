import argparse
import http.server
import socketserver
import sys
import threading
import time
from pathlib import Path
from .controller import S90TRController
from .soundbar import LGSoundbarClient

def play_local_file(controller: S90TRController, file_path: Path, host_ip: str = "192.168.1.111", port: int = 8765):
    """Serve a local file over HTTP and play it."""
    file_path = file_path.resolve()
    if not file_path.exists():
        print(f"Error: File {file_path} does not exist.")
        sys.exit(1)

    parent_dir = file_path.parent

    class Handler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=str(parent_dir), **kwargs)

        def log_message(self, format, *args):
            pass

    socketserver.TCPServer.allow_reuse_address = True
    httpd = socketserver.TCPServer(("0.0.0.0", port), Handler)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()

    url = f"http://{host_ip}:{port}/{file_path.name}"
    print(f"Serving {file_path.name} at {url}...")

    controller.wake_and_play(url, title=file_path.stem)
    print("Playback triggered. Waiting 6 seconds...")
    time.sleep(6)

    httpd.shutdown()
    httpd.server_close()

def main():
    parser = argparse.ArgumentParser(description="LG S90TR Soundbar Control and Streaming")
    parser.add_argument("--ip", default="192.168.1.41", help="Soundbar IP address")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Status
    subparsers.add_parser("status", help="Get soundbar power status and volume")

    # Wake
    subparsers.add_parser("wake", help="Wake up / power on soundbar")

    # Sleep
    subparsers.add_parser("sleep", help="Put soundbar into sleep / standby")

    # Volume
    vol_parser = subparsers.add_parser("volume", help="Set soundbar volume (0-100)")
    vol_parser.add_argument("level", type=int, help="Volume level (0-100)")

    # Play URL
    play_parser = subparsers.add_parser("play", help="Wake soundbar and stream an audio URL")
    play_parser.add_argument("url", help="Media URL or local file path")
    play_parser.add_argument("--volume", type=int, default=None, help="Optional volume level")

    # Test
    subparsers.add_parser("test", help="Wake soundbar and play local test tone")

    args = parser.parse_args()
    controller = S90TRController(ip=args.ip)

    if args.command == "status":
        info = controller.soundbar.get_speaker_info()
        power = info.get("b_powerstatus", False)
        vol = info.get("i_vol", "Unknown")
        mute = info.get("b_mute", False)
        source = info.get("s_audio_source", "Unknown")
        print(f"Device: {info.get('s_user_name', 'LG_Speaker_S90TR')}")
        print(f"Power:  {'ON (Awake)' if power else 'OFF (Standby/Sleep)'}")
        print(f"Volume: {vol} (Muted: {mute})")
        print(f"Source: {source}")

    elif args.command == "wake":
        print("Waking up soundbar...")
        success = controller.wake()
        print("Awake!" if success else "Failed to confirm wake.")

    elif args.command == "sleep":
        print("Putting soundbar to sleep...")
        success = controller.sleep()
        print("Asleep!" if success else "Failed to confirm sleep.")

    elif args.command == "volume":
        print(f"Setting volume to {args.level}...")
        controller.soundbar.set_volume(args.level)
        print("Volume set.")

    elif args.command == "play":
        path = Path(args.url)
        if path.exists():
            play_local_file(controller, path)
        else:
            controller.wake_and_play(args.url, volume=args.volume)

    elif args.command == "test":
        test_file = Path(__file__).resolve().parent.parent.parent / "test_tone.mp3"
        play_local_file(controller, test_file)

if __name__ == "__main__":
    main()
