import http.server
import socketserver
import threading
import time
from uuid import UUID
import pychromecast

SOUNDBAR_IP = "192.168.1.41"
SOUNDBAR_UUID = UUID("af87a814-eabb-0a54-9e90-aca39827ec2d")
SOUNDBAR_MODEL = "LG S90T Soundbar"
SOUNDBAR_NAME = "LG_Speaker_S90TR"

HOST_IP = "192.168.1.111"
HTTP_PORT = 8765

def run_http_server(server):
    try:
        server.serve_forever()
    except Exception:
        pass

def main():
    print(f"Starting local HTTP server on {HOST_IP}:{HTTP_PORT}...")
    handler = http.server.SimpleHTTPRequestHandler
    # Allow address reuse
    socketserver.TCPServer.allow_reuse_address = True
    httpd = socketserver.TCPServer(("0.0.0.0", HTTP_PORT), handler)
    server_thread = threading.Thread(target=run_http_server, args=(httpd,), daemon=True)
    server_thread.start()

    print(f"Connecting to {SOUNDBAR_NAME} at {SOUNDBAR_IP}...")
    cast = pychromecast.get_chromecast_from_host(
        (SOUNDBAR_IP, 8009, SOUNDBAR_UUID, SOUNDBAR_MODEL, SOUNDBAR_NAME)
    )
    cast.wait()
    print(f"Connected! Status: volume={cast.status.volume_level:.2f}, muted={cast.status.volume_muted}")

    media_url = f"http://{HOST_IP}:{HTTP_PORT}/test_tone.mp3"
    print(f"Sending play command for {media_url}...")

    mc = cast.media_controller
    mc.play_media(media_url, "audio/mp3", stream_type="BUFFERED", autoplay=True, title="Test Tone 440Hz")
    mc.block_until_active(timeout=10)

    print(f"Media state: {mc.status.player_state}")
    start_time = time.time()
    # Wait for playback to complete (duration is ~5 seconds)
    while time.time() - start_time < 8:
        time.sleep(0.5)
        state = mc.status.player_state
        print(f"Playing... state: {state}, current_time: {mc.status.current_time}")
        if state in ("IDLE", "UNKNOWN") and (time.time() - start_time > 3):
            print("Playback finished!")
            break

    print("Cleaning up...")
    httpd.shutdown()
    httpd.server_close()
    cast.disconnect()
    print("Done.")

if __name__ == "__main__":
    main()
