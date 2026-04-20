# rl_kill_fixed.py — Alt+F4 pe Rocket League => kill proces
# Dependență: psutil (pip install psutil). Rulează ca Administrator.

import ctypes
from ctypes import wintypes
import psutil

# --- tipuri pointer corecte pe Windows x64/x86 ---
PTR_BITS = ctypes.sizeof(ctypes.c_void_p) * 8
LONG_PTR  = ctypes.c_int64 if PTR_BITS == 64 else ctypes.c_long
ULONG_PTR = ctypes.c_uint64 if PTR_BITS == 64 else ctypes.c_ulong
UINT_PTR  = ctypes.c_uint64 if PTR_BITS == 64 else ctypes.c_uint

for name, tp in [("ULONG_PTR", ULONG_PTR), ("WPARAM", UINT_PTR), ("LPARAM", LONG_PTR), ("LRESULT", LONG_PTR)]:
    if not hasattr(wintypes, name):
        setattr(wintypes, name, tp)

HHOOK     = wintypes.HANDLE
HINSTANCE = wintypes.HINSTANCE if hasattr(wintypes, "HINSTANCE") else wintypes.HANDLE

USER32   = ctypes.windll.user32
KERNEL32 = ctypes.windll.kernel32

# --- constante ---
WH_KEYBOARD_LL = 13
WM_KEYDOWN     = 0x0100
WM_SYSKEYDOWN  = 0x0104
VK_F4          = 0x73
VK_MENU        = 0x12  # Alt
TARGET_EXE     = "RocketLeague.exe"

# --- structuri ---
class KBDLLHOOKSTRUCT(ctypes.Structure):
    _fields_ = [
        ("vkCode",      wintypes.DWORD),
        ("scanCode",    wintypes.DWORD),
        ("flags",       wintypes.DWORD),
        ("time",        wintypes.DWORD),
        ("dwExtraInfo", wintypes.ULONG_PTR),
    ]

LowLevelKeyboardProc = ctypes.WINFUNCTYPE(
    wintypes.LRESULT, ctypes.c_int, wintypes.WPARAM, wintypes.LPARAM
)

# --- prototipuri explicite (fix pentru OverflowError la CallNextHookEx) ---
USER32.SetWindowsHookExW.argtypes = [ctypes.c_int, LowLevelKeyboardProc, HINSTANCE, wintypes.DWORD]
USER32.SetWindowsHookExW.restype  = HHOOK

USER32.CallNextHookEx.argtypes = [HHOOK, ctypes.c_int, wintypes.WPARAM, wintypes.LPARAM]
USER32.CallNextHookEx.restype  = wintypes.LRESULT

USER32.GetWindowThreadProcessId.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.DWORD)]
USER32.GetWindowThreadProcessId.restype  = wintypes.DWORD

USER32.GetMessageW.argtypes = [ctypes.POINTER(wintypes.MSG), wintypes.HWND, wintypes.UINT, wintypes.UINT]
USER32.GetMessageW.restype  = wintypes.BOOL

USER32.TranslateMessage.argtypes = [ctypes.POINTER(wintypes.MSG)]
USER32.TranslateMessage.restype  = wintypes.BOOL

USER32.DispatchMessageW.argtypes = [ctypes.POINTER(wintypes.MSG)]
USER32.DispatchMessageW.restype  = wintypes.LRESULT

# --- utilitare ---
def fg_pid_name():
    hwnd = USER32.GetForegroundWindow()
    if not hwnd:
        return None, None
    pid = wintypes.DWORD(0)
    USER32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
    try:
        p = psutil.Process(pid.value)
        return pid.value, p.name()
    except psutil.Error:
        return None, None

def kill_tree(pid):
    try:
        p = psutil.Process(pid)
    except psutil.Error:
        return
    for c in p.children(recursive=True):
        try:
            c.kill()
        except psutil.Error:
            pass
    try:
        p.kill()
    except psutil.Error:
        pass

@LowLevelKeyboardProc
def hook_proc(nCode, wParam, lParam):
    if nCode == 0 and wParam in (WM_KEYDOWN, WM_SYSKEYDOWN):
        kb = ctypes.cast(lParam, ctypes.POINTER(KBDLLHOOKSTRUCT)).contents
        if (USER32.GetAsyncKeyState(VK_MENU) & 0x8000) and kb.vkCode == VK_F4:
            pid, name = fg_pid_name()
            if name and name.lower() == TARGET_EXE.lower():
                kill_tree(pid)
                return 1  # consumă evenimentul
    # transmiterea mai departe cu tipuri corecte
    return USER32.CallNextHookEx(HHOOK(0), nCode, wintypes.WPARAM(wParam), wintypes.LPARAM(lParam))

def main():
    hook_handle = USER32.SetWindowsHookExW(WH_KEYBOARD_LL, hook_proc, HINSTANCE(0), 0)
    if not hook_handle:
        err = KERNEL32.GetLastError()
        raise OSError(f"SetWindowsHookExW failed, GetLastError={err}")
    globals()["_HOOK_HANDLE"] = hook_handle   # menține referința
    globals()["_HOOK_PROC_REF"] = hook_proc   # menține callback-ul

    msg = wintypes.MSG()
    try:
        while USER32.GetMessageW(ctypes.byref(msg), 0, 0, 0) != 0:
            USER32.TranslateMessage(ctypes.byref(msg))
            USER32.DispatchMessageW(ctypes.byref(msg))
    finally:
        USER32.UnhookWindowsHookEx(hook_handle)

if __name__ == "__main__":
    main()
