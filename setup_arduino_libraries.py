#!/usr/bin/env python3
import os
import sys
import platform
import shutil

def get_arduino_libraries_path():
    home = os.path.expanduser("~")
    system = platform.system()
    
    if system == "Linux":
        paths = [
            os.path.join(home, "Arduino", "libraries"),
            os.path.join(home, "sketchbook", "libraries"),
            os.path.join(home, ".arduino15", "libraries")
        ]
    elif system == "Darwin":  # macOS
        paths = [
            os.path.join(home, "Documents", "Arduino", "libraries"),
            os.path.join(home, "Library", "Arduino15", "libraries")
        ]
    elif system == "Windows":
        paths = [
            os.path.join(home, "Documents", "Arduino", "libraries"),
            os.path.join(home, "OneDrive", "Documents", "Arduino", "libraries")
        ]
    else:
        paths = []
        
    for p in paths:
        if os.path.exists(p):
            return p
            
    if system == "Windows":
        default_path = os.path.join(home, "Documents", "Arduino", "libraries")
    else:
        default_path = os.path.join(home, "Arduino", "libraries")
        
    return default_path

def install_library(src_abs, dest_abs, lib_name):
    if os.path.exists(dest_abs) or os.path.islink(dest_abs):
        try:
            if os.path.islink(dest_abs):
                os.unlink(dest_abs)
            elif os.path.isdir(dest_abs):
                shutil.rmtree(dest_abs)
            else:
                os.remove(dest_abs)
        except Exception as e:
            print(f"  [ERROR] Failed to clean existing {lib_name}: {e}")
            return False

    has_src = os.path.exists(os.path.join(src_abs, "src"))
    has_include = os.path.exists(os.path.join(src_abs, "include"))

    # Always restructure into Arduino v1.5 standard (using a target src/ directory)
    # This ensures recursive compilation of nested files (like Epub, Xtc subfolders)
    try:
        os.makedirs(dest_abs, exist_ok=True)
        dest_src = os.path.join(dest_abs, "src")
        os.makedirs(dest_src, exist_ok=True)

        # Write library.properties
        with open(os.path.join(dest_abs, "library.properties"), "w") as f:
            f.write(f"name={lib_name}\n"
                    f"version=1.0.0\n"
                    f"author=FreeInk SDK\n"
                    f"maintainer=FreeInk SDK\n"
                    f"sentence=FreeInk SDK library wrapper for Arduino IDE\n"
                    f"paragraph=This is an automatically generated library.properties file to enable compilation in Arduino IDE.\n"
                    f"category=Uncategorized\n"
                    f"url=https://github.com/Free-Ink/freeink-sdk\n"
                    f"architectures=*\n")

        # Symlink or copy contents of a folder into target's src/ directory
        def map_contents(from_dir, target_dir):
            if not os.path.exists(from_dir):
                return
            for item in os.listdir(from_dir):
                if item in ("library.json", "library.properties", "README", "README.md", ".gitignore"):
                    continue
                item_src = os.path.join(from_dir, item)
                item_dest = os.path.join(target_dir, item)
                if hasattr(os, 'symlink'):
                    os.symlink(item_src, item_dest, target_is_directory=os.path.isdir(item_src))
                else:
                    if os.path.isdir(item_src):
                        shutil.copytree(item_src, item_dest)
                    else:
                        shutil.copy2(item_src, item_dest)

        if has_src or has_include:
            if has_include:
                map_contents(os.path.join(src_abs, "include"), dest_src)
            if has_src:
                map_contents(os.path.join(src_abs, "src"), dest_src)
        else:
            map_contents(src_abs, dest_src)

        print(f"  [Restructured v1.5] {lib_name}")
        return True

    except Exception as e:
        # Fallback to copy if symlink failed
        try:
            if os.path.exists(dest_abs):
                shutil.rmtree(dest_abs)
            os.makedirs(dest_abs, exist_ok=True)
            dest_src = os.path.join(dest_abs, "src")
            os.makedirs(dest_src, exist_ok=True)
            
            with open(os.path.join(dest_abs, "library.properties"), "w") as f:
                f.write(f"name={lib_name}\n"
                        f"version=1.0.0\n"
                        f"author=FreeInk SDK\n"
                        f"maintainer=FreeInk SDK\n"
                        f"sentence=FreeInk SDK library wrapper for Arduino IDE\n"
                        f"paragraph=This is an automatically generated library.properties file to enable compilation in Arduino IDE.\n"
                        f"category=Uncategorized\n"
                        f"url=https://github.com/Free-Ink/freeink-sdk\n"
                        f"architectures=*\n")
            
            def copy_contents(from_dir, target_dir):
                if not os.path.exists(from_dir):
                    return
                for item in os.listdir(from_dir):
                    if item in ("library.json", "library.properties", "README", "README.md", ".gitignore"):
                        continue
                    item_src = os.path.join(from_dir, item)
                    item_dest = os.path.join(target_dir, item)
                    if os.path.isdir(item_src):
                        shutil.copytree(item_src, item_dest)
                    else:
                        shutil.copy2(item_src, item_dest)
                        
            if has_src or has_include:
                if has_include:
                    copy_contents(os.path.join(src_abs, "include"), dest_src)
                if has_src:
                    copy_contents(os.path.join(src_abs, "src"), dest_src)
            else:
                copy_contents(src_abs, dest_src)
                
            print(f"  [Restructured v1.5 (Copied)] {lib_name}")
            return True
        except Exception as e2:
            print(f"  [FAILED] {lib_name}: {e2}")
            return False

def main():
    dest_dir = get_arduino_libraries_path()
    print(f"Detected Arduino libraries folder: {dest_dir}")
    
    if sys.stdout.isatty():
        val = input(f"Install libraries here? [Y/n]: ").strip().lower()
        if val not in ('', 'y', 'yes'):
            dest_dir = input("Enter the absolute path to your Arduino libraries folder: ").strip()
            
    if not os.path.exists(dest_dir):
        try:
            os.makedirs(dest_dir, exist_ok=True)
            print(f"Created directory: {dest_dir}")
        except Exception as e:
            print(f"Error creating directory {dest_dir}: {e}")
            sys.exit(1)
            
    # Libraries to link from freeink-sdk/libs/
    sdk_libs = {
        "freeink-sdk/libs/display/FreeInkDisplay": "FreeInkDisplay",
        "freeink-sdk/libs/hardware/BatteryMonitor": "BatteryMonitor",
        "freeink-sdk/libs/hardware/InputManager": "InputManager",
        "freeink-sdk/libs/hardware/SDCardManager": "SDCardManager",
        "freeink-sdk/libs/hardware/BoardConfig": "BoardConfig",
        "freeink-sdk/libs/hardware/PowerManager": "PowerManager",
        "freeink-sdk/libs/ui/FreeInkUI": "FreeInkUI",
        "freeink-sdk/libs/assets/Icons": "Icons",
    }
    
    # Libraries to link from lib/
    local_lib_dir = "lib"
    local_libs = {}
    if os.path.exists(local_lib_dir):
        for item in os.listdir(local_lib_dir):
            item_path = os.path.join(local_lib_dir, item)
            if os.path.isdir(item_path) and item != "README":
                local_libs[item_path] = item

    all_libs = {**sdk_libs, **local_libs}
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    print("\nInstalling/Restructuring libraries...")
    success_count = 0
    fail_count = 0
    
    for src_rel, lib_name in all_libs.items():
        src_abs = os.path.join(script_dir, src_rel)
        dest_abs = os.path.join(dest_dir, lib_name)
        
        if not os.path.exists(src_abs):
            print(f"Warning: Source path {src_rel} does not exist. Skipping.")
            continue
            
        ok = install_library(src_abs, dest_abs, lib_name)
        if ok:
            success_count += 1
        else:
            fail_count += 1
                
    print(f"\nDone! Successfully installed/restructured {success_count} libraries.")
    if fail_count > 0:
        print(f"Failed to install {fail_count} libraries.")
        
    print("\nNote: Please make sure you also install the following dependencies via the Arduino Library Manager:")
    print("  - SdFat (by Bill Greiman)")
    print("  - ArduinoJson")
    print("  - QRCode")
    print("  - PNGdec")
    print("  - JPEGDEC")
    print("  - WebSockets")

if __name__ == "__main__":
    main()
