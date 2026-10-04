"""Logitech Easy-Switch: mouse'u (veya klavyeyi) başka bir Easy-Switch kanalına geçirir.

Hedef kanal, sırasıyla şuradan okunur:
  1. Komut satırı argümanı:  easy-switch 3
  2. Başlatan dosyanın adı:  easy-switch-3.exe / easy-switch-3.pyw  -> 3. kanal
  3. Hiçbiri yoksa sıradaki kanal (1 -> 2 -> 3 -> 1 ...)

Logi Options+ "Open file" / "Open application" eylemleri argüman veremediği için
2. yol var: her kanal için ayrı adlı bir kopya kullanılır.

Komut HID++ 2.0 CHANGE_HOST (0x1814) özelliğidir; cihazın kendi Easy-Switch
butonunun yaptığının aynısı. Logitech alıcıları (Bolt, Unifying, Lightspeed...)
ve doğrudan Bluetooth bağlantısı desteklenir; bilgisayara özel ayar yoktur.

Seçenekler:
  --device "MX Keys"  Hedef cihaz adı (varsayılan "MX Master 4"; ad içinde aranır).
                      Aynı alıcıda Easy-Switch destekleyen klavye de olabileceği
                      için cihaz adla seçilir.
  --dry-run           Kanal değiştirmeden ne yapılacağını yazar.

Windows'ta yalnızca standart kütüphane kullanılır: HID erişimi ctypes ile
Windows'un kendi hid.dll / setupapi.dll'i üzerinden yapılır, pip gerekmez.
Diğer sistemlerde hidapi paketi (pip install hidapi) kullanılır.

Program klavye ya da mouse girdisi okumaz; yalnızca Logitech'in HID++ kanalını
açar ve kendi gönderdiği komutların cevaplarını okur.
"""
import datetime
import os
import re
import sys
import time

if os.name == "nt":
    import ctypes
    from ctypes import wintypes as wt

    class _GUID(ctypes.Structure):
        _fields_ = [("Data1", wt.DWORD), ("Data2", wt.WORD), ("Data3", wt.WORD), ("Data4", ctypes.c_ubyte * 8)]

    class _SP_DEVICE_INTERFACE_DATA(ctypes.Structure):
        _fields_ = [("cbSize", wt.DWORD), ("InterfaceClassGuid", _GUID), ("Flags", wt.DWORD), ("Reserved", ctypes.c_size_t)]

    class _HIDD_ATTRIBUTES(ctypes.Structure):
        _fields_ = [("Size", wt.ULONG), ("VendorID", wt.USHORT), ("ProductID", wt.USHORT), ("VersionNumber", wt.USHORT)]

    class _HIDP_CAPS(ctypes.Structure):
        _fields_ = [("Usage", wt.USHORT), ("UsagePage", wt.USHORT), ("InputReportByteLength", wt.USHORT),
                    ("OutputReportByteLength", wt.USHORT), ("FeatureReportByteLength", wt.USHORT),
                    ("Reserved", wt.USHORT * 17), ("Counts", wt.USHORT * 10)]

    class _OVERLAPPED(ctypes.Structure):
        _fields_ = [("Internal", ctypes.c_size_t), ("InternalHigh", ctypes.c_size_t),
                    ("Offset", wt.DWORD), ("OffsetHigh", wt.DWORD), ("hEvent", wt.HANDLE)]

    class hid:  # noqa: N801 - hidapi'nin "hid" modülüyle aynı arayüz
        """hidapi'nin bu programın kullandığı kısmının ctypes ile Windows karşılığı."""

        _k32 = ctypes.WinDLL("kernel32", use_last_error=True)
        _hid = ctypes.WinDLL("hid")
        _setupapi = ctypes.WinDLL("setupapi", use_last_error=True)
        _INVALID = ctypes.c_void_p(-1).value
        _GENERIC_RW = 0x80000000 | 0x40000000
        _SHARE_RW = 0x1 | 0x2
        _OPEN_EXISTING = 3
        _FLAG_OVERLAPPED = 0x40000000
        _ERROR_IO_PENDING = 997
        _WAIT_TIMEOUT = 0x102
        _HIDP_STATUS_SUCCESS = 0x00110000

        _k32.CreateFileW.restype = ctypes.c_void_p
        _k32.CreateFileW.argtypes = [wt.LPCWSTR, wt.DWORD, wt.DWORD, ctypes.c_void_p, wt.DWORD, wt.DWORD, ctypes.c_void_p]
        _k32.CloseHandle.argtypes = [ctypes.c_void_p]
        _k32.CreateEventW.restype = ctypes.c_void_p
        _k32.CreateEventW.argtypes = [ctypes.c_void_p, wt.BOOL, wt.BOOL, wt.LPCWSTR]
        _k32.ReadFile.argtypes = [ctypes.c_void_p, ctypes.c_void_p, wt.DWORD, ctypes.c_void_p, ctypes.c_void_p]
        _k32.WriteFile.argtypes = [ctypes.c_void_p, ctypes.c_void_p, wt.DWORD, ctypes.c_void_p, ctypes.c_void_p]
        _k32.WaitForSingleObject.restype = wt.DWORD
        _k32.WaitForSingleObject.argtypes = [ctypes.c_void_p, wt.DWORD]
        _k32.CancelIoEx.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
        _k32.GetOverlappedResult.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.POINTER(wt.DWORD), wt.BOOL]
        _setupapi.SetupDiGetClassDevsW.restype = ctypes.c_void_p
        _setupapi.SetupDiGetClassDevsW.argtypes = [ctypes.c_void_p, wt.LPCWSTR, ctypes.c_void_p, wt.DWORD]
        _setupapi.SetupDiEnumDeviceInterfaces.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, wt.DWORD, ctypes.c_void_p]
        _setupapi.SetupDiGetDeviceInterfaceDetailW.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, wt.DWORD,
                                                              ctypes.POINTER(wt.DWORD), ctypes.c_void_p]
        _setupapi.SetupDiDestroyDeviceInfoList.argtypes = [ctypes.c_void_p]
        _hid.HidD_GetHidGuid.argtypes = [ctypes.c_void_p]
        _hid.HidD_GetAttributes.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
        _hid.HidD_GetPreparsedData.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_void_p)]
        _hid.HidD_FreePreparsedData.argtypes = [ctypes.c_void_p]
        _hid.HidP_GetCaps.restype = ctypes.c_long
        _hid.HidP_GetCaps.argtypes = [ctypes.c_void_p, ctypes.c_void_p]

        @classmethod
        def _interface_paths(cls):
            guid = _GUID()
            cls._hid.HidD_GetHidGuid(ctypes.byref(guid))
            info = cls._setupapi.SetupDiGetClassDevsW(ctypes.byref(guid), None, None, 0x12)  # PRESENT | DEVICEINTERFACE
            if info == cls._INVALID:
                return
            try:
                i = 0
                while True:
                    iface = _SP_DEVICE_INTERFACE_DATA(cbSize=ctypes.sizeof(_SP_DEVICE_INTERFACE_DATA))
                    if not cls._setupapi.SetupDiEnumDeviceInterfaces(info, None, ctypes.byref(guid), i, ctypes.byref(iface)):
                        return
                    i += 1
                    need = wt.DWORD()
                    cls._setupapi.SetupDiGetDeviceInterfaceDetailW(info, ctypes.byref(iface), None, 0, ctypes.byref(need), None)
                    buf = ctypes.create_string_buffer(need.value)
                    # SP_DEVICE_INTERFACE_DETAIL_DATA_W.cbSize: 64 bitte 8, 32 bitte 6
                    ctypes.c_uint32.from_buffer(buf).value = 8 if ctypes.sizeof(ctypes.c_void_p) == 8 else 6
                    if cls._setupapi.SetupDiGetDeviceInterfaceDetailW(info, ctypes.byref(iface), buf, need, None, None):
                        yield ctypes.wstring_at(ctypes.addressof(buf) + 4)
            finally:
                cls._setupapi.SetupDiDestroyDeviceInfoList(info)

        @classmethod
        def _open(cls, path, access):
            h = cls._k32.CreateFileW(path, access, cls._SHARE_RW, None, cls._OPEN_EXISTING,
                                     cls._FLAG_OVERLAPPED if access else 0, None)
            if h in (None, cls._INVALID):
                raise OSError(ctypes.get_last_error(), f"HID cihazı açılamadı: {path}")
            return h

        @classmethod
        def _caps(cls, h):
            pp = ctypes.c_void_p()
            if not cls._hid.HidD_GetPreparsedData(h, ctypes.byref(pp)):
                return None
            try:
                caps = _HIDP_CAPS()
                ok = cls._hid.HidP_GetCaps(pp, ctypes.byref(caps)) == cls._HIDP_STATUS_SUCCESS
                return caps if ok else None
            finally:
                cls._hid.HidD_FreePreparsedData(pp)

        @classmethod
        def enumerate(cls, vendor_id=0, product_id=0):
            for path in cls._interface_paths():
                try:
                    h = cls._open(path, 0)  # erişimsiz açış: yalnızca öznitelik sorgusu
                except OSError:
                    continue
                try:
                    attrs = _HIDD_ATTRIBUTES(Size=ctypes.sizeof(_HIDD_ATTRIBUTES))
                    caps = cls._caps(h)
                    if not cls._hid.HidD_GetAttributes(h, ctypes.byref(attrs)) or caps is None:
                        continue
                finally:
                    cls._k32.CloseHandle(h)
                if vendor_id and attrs.VendorID != vendor_id or product_id and attrs.ProductID != product_id:
                    continue
                yield {"path": path, "vendor_id": attrs.VendorID, "product_id": attrs.ProductID,
                       "usage_page": caps.UsagePage, "usage": caps.Usage}

        class device:  # noqa: N801
            def __init__(self):
                self._h = None

            def open_path(self, path):
                self._h = hid._open(path, hid._GENERIC_RW)
                caps = hid._caps(self._h)
                self._in_len = caps.InputReportByteLength if caps else 64
                self._out_len = caps.OutputReportByteLength if caps else 64
                self._event = hid._k32.CreateEventW(None, True, False, None)

            def _io(self, func, buf, size, timeout_ms):
                ov = _OVERLAPPED(hEvent=self._event)
                done = wt.DWORD()
                if not func(self._h, buf, size, None, ctypes.byref(ov)):
                    err = ctypes.get_last_error()
                    if err != hid._ERROR_IO_PENDING:
                        raise OSError(err, "HID okuma/yazma hatası")
                    if hid._k32.WaitForSingleObject(self._event, timeout_ms) == hid._WAIT_TIMEOUT:
                        hid._k32.CancelIoEx(self._h, ctypes.byref(ov))
                        hid._k32.GetOverlappedResult(self._h, ctypes.byref(ov), ctypes.byref(done), True)
                        return 0
                if not hid._k32.GetOverlappedResult(self._h, ctypes.byref(ov), ctypes.byref(done), True):
                    return 0
                return done.value

            def write(self, data):
                # Windows rapor uzunluğunun tam tutmasını ister
                buf = ctypes.create_string_buffer(bytes(data)[: self._out_len].ljust(self._out_len, b"\0"), self._out_len)
                return self._io(hid._k32.WriteFile, buf, self._out_len, 1000)

            def read(self, size, timeout_ms):
                buf = ctypes.create_string_buffer(self._in_len)
                n = self._io(hid._k32.ReadFile, buf, self._in_len, timeout_ms)
                return list(buf.raw[: min(n, size)])

            def close(self):
                if self._h:
                    hid._k32.CloseHandle(self._h)
                    hid._k32.CloseHandle(self._event)
                    self._h = None
else:
    import hid

DEFAULT_DEVICE = "MX Master 4"
LOGI_VID = 0x046D
LONG_REPORT = 0x11
SW_ID = 0x0A
FEAT_ROOT = 0x00
FEAT_DEVICE_NAME = 0x0005
FEAT_CHANGE_HOST = 0x1814
REPLY_TIMEOUT = 1.0  # saniye; uyuyan ya da olmayan cihaz için bekleme sınırı

FROZEN = getattr(sys, "frozen", False)  # PyInstaller ile derlenmiş .exe
BASE_DIR = os.path.dirname(os.path.abspath(sys.executable if FROZEN else __file__))
LOG_PATH = os.path.join(BASE_DIR, "easy-switch.log")


class HidppError(Exception):
    pass


class Device:
    def __init__(self, handle, index):
        self.handle = handle
        self.index = index

    def request(self, feat_index, func, params=b""):
        fn = (func << 4) | SW_ID
        self.handle.write(bytes([LONG_REPORT, self.index, feat_index, fn]) + params.ljust(16, b"\0"))
        deadline = time.monotonic() + REPLY_TIMEOUT
        while time.monotonic() < deadline:
            r = bytes(self.handle.read(20, 100))
            if len(r) < 5 or r[1] != self.index:
                continue
            if r[2] == 0x8F or (r[2] == 0xFF and r[3] == feat_index):  # HID++ 1.0 / 2.0 hata
                raise HidppError(f"cihaz hata döndü: {r[:8].hex()}")
            if r[2] == feat_index and r[3] == fn:
                return r[4:]
        raise HidppError("cevap gelmedi")

    def feature_index(self, feature_id):
        idx = self.request(FEAT_ROOT, 0, feature_id.to_bytes(2, "big"))[0]
        if idx == 0:
            raise HidppError(f"özellik 0x{feature_id:04X} desteklenmiyor")
        return idx

    def name(self):
        fi = self.feature_index(FEAT_DEVICE_NAME)
        length = self.request(fi, 0)[0]
        name = b""
        while len(name) < length:
            name += self.request(fi, 1, bytes([len(name)]))[: length - len(name)]
        return name.decode("ascii", "replace")


def candidates():
    """HID++ uzun rapor kanalı olan (hid yolu, cihaz indeksleri) çiftleri.

    Alıcılar 0xFF00/0x0002 kanalını açar, arkasındaki cihazlar 1..6 indekslidir.
    Bluetooth'la doğrudan bağlı cihazlar 0xFF43/0x0202 kanalını açar, indeksleri 0xFF'dir.
    """
    seen = set()
    for d in hid.enumerate():
        if d["path"] in seen:
            continue
        seen.add(d["path"])
        if d["vendor_id"] == LOGI_VID and d["usage_page"] == 0xFF00 and d["usage"] == 0x0002:
            yield d["path"], list(range(1, 7))
        elif d["usage_page"] == 0xFF43 and d["usage"] == 0x0202:
            yield d["path"], [0xFF]


def find_device(wanted):
    seen_names = []
    for path, indexes in candidates():
        handle = hid.device()
        try:
            handle.open_path(path)
        except OSError:
            continue
        for index in indexes:
            dev = Device(handle, index)
            try:
                name = dev.name()
            except HidppError:
                continue
            if wanted.lower() in name.lower():
                return dev
            seen_names.append(name)
        handle.close()
    found = f" (bulunanlar: {', '.join(seen_names)})" if seen_names else ""
    raise HidppError(f"{wanted} bulunamadı; uyuyor ya da bu bilgisayara bağlı değil olabilir{found}")


def parse_args(argv):
    target, device, dry_run = None, DEFAULT_DEVICE, False
    rest = list(argv[1:])
    while rest:
        a = rest.pop(0)
        if a == "--dry-run":
            dry_run = True
        elif a == "--device" and rest:
            device = rest.pop(0)
        elif a.isdigit():
            target = int(a)
        else:
            raise HidppError(f"tanınmayan argüman: {a}")
    if target is None:
        m = re.search(r"-(\d+)$", os.path.splitext(os.path.basename(argv[0]))[0])
        target = int(m.group(1)) if m else None
    return target, device, dry_run


def log(msg):
    line = f"{datetime.datetime.now():%Y-%m-%d %H:%M:%S} {msg}"
    if sys.stdout:  # pythonw / pencereli .exe'de stdout yok
        print(line)
    try:
        if os.path.exists(LOG_PATH) and os.path.getsize(LOG_PATH) > 256 * 1024:
            os.replace(LOG_PATH, LOG_PATH + ".1")
        with open(LOG_PATH, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except OSError:
        pass


def alert(msg):
    """Konsolsuz çalışırken hatayı görünür kılar (yalnız Windows)."""
    if sys.stdout or os.name != "nt":
        return
    import ctypes
    ctypes.windll.user32.MessageBoxW(None, msg, "Easy-Switch", 0x10)


def main(argv=None):
    argv = argv or sys.argv
    try:
        target, wanted, dry_run = parse_args(argv)
        dev = find_device(wanted)
        fi = dev.feature_index(FEAT_CHANGE_HOST)
        info = dev.request(fi, 0)  # getHostInfo -> [kanal sayısı, şu anki kanal (0 tabanlı)]
        count, current = info[0], info[1] + 1
        if target is None:
            target = current % count + 1
        if not 1 <= target <= count:
            raise HidppError(f"kanal {target} geçersiz; cihazda {count} kanal var")
        if target == current:
            log(f"zaten {current}. kanalda, bir şey yapılmadı")
            return 0
        if dry_run:
            log(f"[dry-run] {current}. kanaldan {target}. kanala geçilecekti")
            return 0
        # setCurrentHost: cevap beklenmez, cihaz hemen bağlantıyı bırakır
        dev.handle.write(bytes([LONG_REPORT, dev.index, fi, (1 << 4) | SW_ID, target - 1]).ljust(20, b"\0"))
        log(f"{current}. kanaldan {target}. kanala geçildi")
        return 0
    except Exception as e:
        log(f"HATA: {e}")
        alert(str(e))
        return 1


if __name__ == "__main__":
    sys.exit(main())
