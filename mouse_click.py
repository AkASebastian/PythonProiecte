# auto_clicker.py
# Rulează ca Administrator. Nu garantează funcționare în aplicații protejate (EAC/anti-cheat).
import ctypes, time, threading
from ctypes import wintypes
import keyboard  # pip install keyboard

# ---- SendInput setup (compatibilitate ULONG_PTR) ----
user32 = ctypes.windll.user32
if not hasattr(wintypes, "ULONG_PTR"):
    wintypes.ULONG_PTR = ctypes.c_uint64 if ctypes.sizeof(ctypes.c_void_p) == 8 else ctypes.c_ulong

class MOUSEINPUT(ctypes.Structure):
    _fields_ = [
        ("dx", wintypes.LONG),
        ("dy", wintypes.LONG),
        ("mouseData", wintypes.DWORD),
        ("dwFlags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", wintypes.ULONG_PTR),
    ]
class _INPUTunion(ctypes.Union):
    _fields_ = [("mi", MOUSEINPUT)]
class INPUT(ctypes.Structure):
    _anonymous_ = ("u",)
    _fields_ = [("type", wintypes.DWORD), ("u", _INPUTunion)]

INPUT_MOUSE = 0
MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP   = 0x0004

SendInput = user32.SendInput
SendInput.argtypes = (wintypes.UINT, ctypes.POINTER(INPUT), ctypes.c_int)
SendInput.restype  = wintypes.UINT

def click_left():
    down = INPUT()
    down.type = INPUT_MOUSE
    down.mi = MOUSEINPUT(0, 0, 0, MOUSEEVENTF_LEFTDOWN, 0, 0)
    up = INPUT()
    up.type = INPUT_MOUSE
    up.mi = MOUSEINPUT(0, 0, 0, MOUSEEVENTF_LEFTUP, 0, 0)
    if SendInput(1, ctypes.byref(down), ctypes.sizeof(down)) != 1:
        raise OSError("SendInput leftdown failed")
    time.sleep(0.01)
    if SendInput(1, ctypes.byref(up), ctypes.sizeof(up)) != 1:
        raise OSError("SendInput leftup failed")

# ---- Auto-click controller ----
class AutoClicker:
    def __init__(self, interval_seconds=0.1, burst_count=1):
        self.interval = float(interval_seconds)
        self.burst = int(burst_count)  # clicks per cycle
        self._stop_event = threading.Event()
        self._thread = None

    def _run(self):
        while not self._stop_event.is_set():
            for _ in range(self.burst):
                click_left()
                if self._stop_event.is_set():
                    break
                # tiny spacing between burst clicks
                time.sleep(0.01)
            # wait interval (responsive to stop)
            end = time.time() + self.interval
            while time.time() < end:
                if self._stop_event.is_set():
                    break
                time.sleep(0.005)

    def start(self):
        if self._thread and self._thread.is_alive():
            return
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self):
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=1)

# ---- Configuration ----
INTERVAL_SECONDS = 0.05   # time between click bursts (set to desired rate)
BURST_CLICKS = 1         # clicks per cycle (1 = single click)
STOP_KEY = "esc"         # key to stop the auto-clicker immediately

# ---- Main ----
if __name__ == "__main__":
    ac = AutoClicker(interval_seconds=INTERVAL_SECONDS, burst_count=BURST_CLICKS)
    ac.start()
    keyboard.wait(STOP_KEY)  # press STOP_KEY to stop
    ac.stop()
