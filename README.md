# easy-switch

**English** | [Türkçe](README.tr.md)

A small Windows tool that switches a Logitech mouse (or keyboard) to another Easy-Switch channel with a single button press.

Logitech MX devices can be paired with up to three computers/devices, and you switch between them with the Easy-Switch button on the bottom of the device. Logi Options+ does not let you assign this switch directly to a button; it can only be done through the Actions Ring, in two steps. **easy-switch** fills that gap: assign this program to any button in Options+, and a single press moves the device to another channel.

The program can be used in two ways: as plain Python code on computers that have Python installed (no `.exe` needed), or as a ready-made `.exe` that needs no Python. See [Installation](#installation) for details.

## How it works

The program sends exactly the same command the device's own Easy-Switch button sends: the `CHANGE_HOST` (`0x1814`) feature of the HID++ 2.0 protocol.

1. The computer's HID devices are scanned:

   | Connection | HID++ channel (usage page / usage) | Device index |
   | --- | --- | --- |
   | Logitech receiver (Bolt, Unifying, Lightspeed...) | `0xFF00` / `0x0002` | `1`..`6` |
   | Direct Bluetooth | `0xFF43` / `0x0202` | `0xFF` |

2. Each device's name is read with the `DEVICE_NAME` (`0x0005`) feature, and the target device is found by name. Selection is by name because another Easy-Switch device (a keyboard, for example) may share the same receiver.
3. `CHANGE_HOST.getHostInfo` reads the number of channels and the current channel.
4. `CHANGE_HOST.setCurrentHost` switches to the target channel. The device drops the connection immediately, so no reply is expected.

There are no computer-specific settings; the same program works on every computer.

## Channel selection

The target channel is taken from, in order:

1. **Command-line argument:** `easy-switch.exe 3` or `python easy_switch.py 3`
2. **The program's file name:** `easy-switch-3.exe` or `easy-switch-3.pyw` → channel 3
3. If neither is given, the **next channel** (1 → 2 → 3 → 1)

Option 2 exists because Logi Options+ cannot pass arguments to a program: for each channel you use a copy of the same program whose name ends with the channel number.

| With Python | With `.exe` | Behavior |
| --- | --- | --- |
| `easy-switch.pyw` | `easy-switch.exe` | Switches to the next channel |
| `easy-switch-1.pyw` | `easy-switch-1.exe` | Switches to channel 1 |
| `easy-switch-2.pyw` | `easy-switch-2.exe` | Switches to channel 2 |
| `easy-switch-3.pyw` | `easy-switch-3.exe` | Switches to channel 3 |

If the device is already on the target channel, the program does nothing.

## Installation

There are two ways; both do the same job:

| | A. With Python (`.pyw`) | B. Ready-made program (`.exe`) |
| --- | --- | --- |
| When? | Computers where running `.exe` files is blocked, or where the `.exe` is flagged by antivirus | If you don't want to install Python |
| Requires | Python (no extra packages) | Nothing |
| Options+ action | **Open file** | **Open application** |

> [!NOTE]
> The program only works on the computer it is installed on. Once the device has moved to another computer, to come back either install the program on that computer too and assign the button there, or use the device's own Easy-Switch button.

### A. Running with Python (no `.exe` needed)

If you have never installed Python before, follow these steps from start to finish.

#### 1. Install Python

1. Open <https://www.python.org/downloads/windows/>. Under **Stable Releases**, click the **Download Windows installer (64-bit)** link below one of the top releases. The downloaded file should be named something like `python-3.x.x-amd64.exe`.
2. Run the downloaded installer.
3. Tick the two boxes at the bottom of the first screen:
   - **Use admin privileges when installing py.exe**
   - **Add python.exe to PATH**
4. Click **Install Now** and wait for the installation to finish.

> [!IMPORTANT]
> The Python installer is itself an `.exe`. On computers where running `.exe` files is blocked, ask your IT department to install Python; in most organizations Python is an approved application. Once Python is installed, nothing else needs to be installed for this program.

**Check:** type `cmd` in the Start menu, open **Command Prompt**, and type:

```bat
python --version
```

You should see a version number such as `Python 3.12.5`. The program works with Python 3.10 and later.

#### 2. Download the program files

1. On this GitHub page, click the green **Code** button, then **Download ZIP**.
2. Right-click the downloaded ZIP file and choose **Extract All**.
3. Move the extracted folder to a permanent location, for example `C:\Tools\easy-switch`. Options+ will launch the file from this path, so the folder should not be moved later.

These files are all you need in the folder; the `dist/` folder is not needed for this method:

| File | Purpose |
| --- | --- |
| `easy_switch.py` | The program itself; always required |
| `easy-switch.pyw` | Switches to the next channel |
| `easy-switch-1.pyw` | Switches to channel 1 |
| `easy-switch-2.pyw` | Switches to channel 2 |
| `easy-switch-3.pyw` | Switches to channel 3 |

The `.pyw` files are small launchers that run the program without opening a black console window. The file name decides which channel to switch to. They must be in the same folder as `easy_switch.py`.

#### 3. Try the program

Move the mouse to wake it up. In Command Prompt, go to the folder and run the program in dry-run mode. This mode does not switch channels; it only reports what it would do:

```bat
cd C:\Tools\easy-switch
python easy_switch.py --dry-run
```

You should see a line similar to this:

```text
2026-10-05 01:49:49 [dry-run] 2. kanaldan 3. kanala geçilecekti
```

This means "would switch from channel 2 to channel 3". The program's messages are currently in Turkish; see [Log and errors](#log-and-errors) for the meaning of each message.

If your mouse is not an MX Master 4, give the device name: `python easy_switch.py --device "MX Anywhere 3" --dry-run`. If the name is not found, the error message lists the names of the Logitech devices seen on the computer.

#### 4. Connect it to Logi Options+

1. Open Logi Options+ and click your mouse.
2. On the mouse picture, click the button you want to use for switching (for example the **Forward** button on the side). That button's previous function will be lost.
3. In the action list that opens on the right, choose **Open file**.
4. Click **BROWSE FILE** and select the `.pyw` file you want, for example `C:\Tools\easy-switch\easy-switch-3.pyw`.
5. Press the button. The mouse moves to the other device in about half a second.

> [!TIP]
> If nothing happens when you press the button, check the `easy-switch.log` file in the folder. If the file was never created, Windows is not opening `.pyw` files with Python: right-click the `.pyw` file, choose **Open with** → **Python** → **Always use this app**, and try again.

### B. Running the ready-made program (`.exe`)

#### Using the ready-made `.exe` files

1. Download the `.exe` files from the [latest release](https://github.com/serkanayaz/easy-switch/releases/latest) and put them in a permanent folder, for example `C:\Tools\easy-switch`.

   | File | Behavior |
   | --- | --- |
   | `easy-switch.exe` | Switches to the next channel |
   | `easy-switch-1.exe` | Switches to channel 1 |
   | `easy-switch-2.exe` | Switches to channel 2 |
   | `easy-switch-3.exe` | Switches to channel 3 |

2. Logi Options+ → your mouse → the button you will use for switching → **Open application** from the action list → **BROWSE APPLICATION** → the `.exe` you want.
3. Press the button.

On the first run, Windows SmartScreen may show a "Windows protected your PC" warning. This is normal because the program is unsigned; you can continue with **More info** → **Run anyway**.

#### Building the `.exe` files yourself

Instead of trusting the ready-made files, you can build the `.exe` files from the source code yourself. For this, install Python and download the files using steps 1 and 2 of method A. Then, in Command Prompt:

```bat
cd C:\Tools\easy-switch
pip install pyinstaller
pyinstaller --onefile --windowed --name easy-switch --exclude-module hid easy_switch.py

cd dist
copy easy-switch.exe easy-switch-1.exe
copy easy-switch.exe easy-switch-2.exe
copy easy-switch.exe easy-switch-3.exe
```

- `--onefile`: packs everything into a single `.exe` file.
- `--windowed`: prevents a console window from opening.
- `--exclude-module hid`: leaves out the `hidapi` package, which is not needed on Windows.

The `.exe` files are created in the `dist` folder. The four files are identical apart from their names; the name decides which channel to switch to. To test, run `dist\easy-switch.exe --dry-run` and check the result in `dist\easy-switch.log`. To connect it to Options+, follow the steps above.

### Security

The program does **not** read keyboard or mouse input. It only opens Logitech's HID++ channel, writes its own commands to the device, and reads only the replies to those commands. Windows reserves the keyboard and mouse channels for the operating system; the program does not access them. On Windows, HID access goes through `ctypes` and Windows' own `hid.dll` / `setupapi.dll`; no external packages are involved. The entire program is in a single readable file: `easy_switch.py`.

### macOS and Linux

Install the `hidapi` package with `pip install hidapi` and try `python3 easy_switch.py --dry-run`. These platforms have not been tested.

## Command line

```text
easy-switch.exe [CHANNEL] [--device NAME] [--dry-run]
python easy_switch.py [CHANNEL] [--device NAME] [--dry-run]
```

Both forms take the same options; in the examples below, `easy-switch.exe` can be replaced with `python easy_switch.py`.

| Option | Description |
| --- | --- |
| `CHANNEL` | Channel to switch to (`1`, `2`, `3`). If omitted, the file name is checked; if that has no number either, the next channel is used. |
| `--device NAME` | Name of the target device; matched as a substring, case-insensitive. Default: `MX Master 4`. |
| `--dry-run` | Does not switch channels; writes what it would do to the log file. |

Examples:

```bash
easy-switch.exe 2
easy-switch.exe --device "MX Keys" 3
easy-switch.exe --dry-run
```

## Log and errors

Every run writes one line to `easy-switch.log` in the program's folder. When the file exceeds 256 KB it is kept as `easy-switch.log.1`.

If an error occurs while running without a console, a warning window is also shown. The program's messages are currently in Turkish:

| Message | Meaning |
| --- | --- |
| `N. kanaldan M. kanala geçildi` | Switched from channel N to channel M. |
| `[dry-run] N. kanaldan M. kanala geçilecekti` | Dry run: would switch from channel N to channel M. |
| `zaten N. kanalda, bir şey yapılmadı` | Already on channel N; nothing was done. |

Common errors:

| Error | Meaning and fix |
| --- | --- |
| `... bulunamadı; uyuyor ya da bu bilgisayara bağlı değil olabilir` | "... not found; it may be asleep or not connected to this computer." Move the device to wake it up. The end of the message lists the Logitech devices seen on that computer (`bulunanlar:` = "found:"); you can pick one of them with `--device`. |
| `kanal N geçersiz; cihazda M kanal var` | "Channel N is invalid; the device has M channels." The channel number in the file name or argument is larger than the device's channel count. |

When the device is not found, the error takes a few seconds because the program scans every connected receiver; a normal switch is instant.

## Requirements and limitations

- Windows 10/11; the `.exe` needs nothing, the `.pyw` needs only Python. The source code may also work on macOS and Linux with `hidapi`, but these platforms have not been tested.
- The device must support the HID++ 2.0 `CHANGE_HOST` feature (current Logitech devices that have an Easy-Switch button).
- Works while Logi Options+ is running; it does not interfere with it.
- Tested with: MX Master 4, Logi Bolt receiver, Windows 11.

## Files

| File | Contents |
| --- | --- |
| `easy_switch.py` | The entire program |
| `easy-switch*.pyw` | Console-less Python launchers |
| `dist/README.txt` | Short user note shipped with the `.exe` files (Turkish) |

The compiled `.exe` files are not stored in the repository; they are published on the [Releases](https://github.com/serkanayaz/easy-switch/releases) page.

## License

[MIT](LICENSE)
