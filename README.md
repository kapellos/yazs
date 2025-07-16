# 💣 Yet Another Zip Smuggler

This tool creates a **malicious ZIP archive** containing a `.lnk` (Windows shortcut) file and **injects a hidden base64-encoded payload** (tar-archived files) into the middle of the ZIP file before the Central Directory. The `.lnk` can be configured to **execute a decoy URL and extract+run the payload**, or **persist across reboots** by writing to the Windows Startup folder.

> **⚠️ DISCLAIMER**\
> This tool is intended **strictly for educational purposes** and **authorized red team engagements**. Misuse of this code may be illegal. The author takes no responsibility for any damage caused.

---

## 📆 Features

- Creates a `.tar` archive of files and base64-encodes it.
- Embeds the payload into a ZIP file without breaking its structure.
- Generates a `.lnk` file pointing to `cmd.exe`, executing extraction and payload logic.
- Supports **persistence mode**: writes to Startup and reboots the system.
- Mimics a PDF icon using Microsoft Edge executable for deception.

---

## 🛠️ Requirements

- Python 3.x
- Windows OS (for `.lnk` creation)
- `pywin32` (`pip install pywin32`)

---

## 🚀 Usage

```bash
python3 yazs.py <lnk_name.lnk> <decoy_url> <file1> [file2 ...] [--persist]
```

### Arguments:

| Argument    | Description                                                       |
| ----------- | ----------------------------------------------------------------- |
| `lnk_name`  | Name of the `.lnk` file to generate.                              |
| `decoy_url` | URL to open as a distraction/decoy.                               |
| `file1 ...` | Files to embed in the payload (first one is the "malware").       |
| `--persist` | Optional. Enables persistence via Startup folder + system reboot. |

---

## 🔍 Example

```bash
python3 yazs.py update.lnk https://example.com mypayload.exe helper.dll --persist
```

This creates:

- `update.lnk.zip` — the final ZIP containing the `.lnk`
- `update.tar` — the hidden base64-encoded payload injected into the ZIP

---

## ⚙️ How It Works

1. **Payload Packaging:**\
   Selected files are packed into a `.tar`, base64-encoded.

2. **LNK Generation:**\
   A `.lnk` file is created to run `cmd.exe` with complex arguments:

   - Extracts the base64 from the ZIP using `findstr`.
   - Uses `certutil -decodehex` and `tar -xf` to unpack.
   - Executes payload or creates persistence.

3. **ZIP Injection:**\
   The payload is inserted **before the Central Directory** of the ZIP file, keeping the archive valid.

---

## 🔐 Red Team Notes

- **Persistence** mimics Windows Update behavior with a fake reboot message.
- Payload is injected in a way that **does not break** ZIP structure.
- Decoy URL can be any trusted or misleading website to reduce suspicion.

---

## 📌 Output

- `yourname.tar` — intermediate archive
- `yourname.zip` — final payload-injected ZIP
- `yourname_lnk/` — temporary folder (auto-deleted)

---

## ❗ Legal

Only use this tool in environments where you have **explicit permission** to test. Unauthorized use is illegal and unethical.

---

## 📄 License

MIT License

---

## 🙏 Credits

Inspired by and based on research from [Alex Reid's ZIP Smuggling project](https://github.com/Octoberfest7/zip_smuggling).

