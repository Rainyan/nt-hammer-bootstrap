#!/usr/bin/env python3

import os
assert os.name == "nt", "This script supports Windows only."
import sys

from collections import OrderedDict
import webbrowser
import winreg
from time import sleep

import PySimpleGUI as sg
from valve_keyvalues_python.valve_keyvalues_python.keyvalues import KeyValues


DEBUG = True

STEAM_APPIDS = {
    "Neotokyo": 244630,
    "Source SDK": 211,
    "Source SDK Base 2006": 215,
}

TOOL_HOMEPAGE = "https://github.com/Rainyan/nt-hammer-bootstrap"
VERSION = "0.1.0"


def resource_path():
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.dirname(os.path.realpath(__file__))
    return os.path.normpath(base_path)


def get_steam_install_path():
    keys = (
        "SOFTWARE\Wow6432Node\Valve\Steam",  # x64
        "SOFTWARE\Valve\Steam",  # x86
    )
    registry = winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE)
    for key in keys:
        try:
            handle = winreg.OpenKey(registry, key)
        except FileNotFoundError:
            continue
        (steam_path, _) = winreg.QueryValueEx(handle, "InstallPath")
        winreg.CloseKey(handle)
        return os.path.normpath(steam_path)
    assert False, "Could not find Steam install path."


def get_app_install_path(appid):
    libfolders = os.path.join(get_steam_install_path(), "config", "libraryfolders.vdf")
    assert os.path.exists(libfolders)
    kv = KeyValues(filename=libfolders)
    d = OrderedDict()
    for k in kv["libraryfolders"]:
        if not str(appid) in kv["libraryfolders"][k]["apps"]:
            continue
        return os.path.normpath(os.path.join(kv["libraryfolders"][k]["path"], "steamapps", "common"))
        break
    return ""


def generate_hammer_config():
    neotokyo_base_path = os.path.join(get_app_install_path(STEAM_APPIDS["Neotokyo"]), "NEOTOKYO")
    if not os.path.isdir(neotokyo_base_path):
        oneshot_window("Abort", "Could not find NEOTOKYO Steam installation.")
        exit(1)
    # assert os.path.isdir(neotokyo_base_path), "Could not find NEOTOKYO Steam installation."
    mapping_path = os.path.join(neotokyo_base_path, "mapping")
    try:
        os.mkdir(mapping_path)
    except FileExistsError as err:
        if DEBUG:
            pass
        else:
            oneshot_window("Continue", "Mapping path already exists! Are you sure you want to continue? If not, abort with the top-right X button.")
            pass
            # err.add_note("You should only use this script for a clean Hammer environment setup.")
            # raise err
    with open(os.path.join(resource_path(), "payload", "GameInfo.txt"), mode="r", encoding="utf-8") as f_read:
        with open(os.path.join(mapping_path, "GameInfo.txt"), mode="w", encoding="utf-8") as f_write:
            f_write.write(f_read.read())

    source_sdk_base_path = os.path.join(get_app_install_path(STEAM_APPIDS["Source SDK"]))
    sdk_path = os.path.join(source_sdk_base_path, "SourceSDK", "bin", "ep1", "bin")
    sdk_content_path = os.path.join(source_sdk_base_path, "sourcesdk_content")

    if not os.path.isdir(neotokyo_base_path):
        oneshot_window("Abort", "Could not find Source SDK installation. "
                                "Make sure you have both Source SDK and "
                                "Source SDK Base 2006 installed, and launch "
                                "and quit Source SDK from Steam library tools "
                                "at least once.")
        sys.exit(1)
    # assert os.path.isdir(neotokyo_base_path), ("Could not find Source SDK installation. "
    #                                             "Make sure you have both Source SDK and "
    #                                             "Source SDK Base 2006 installed, and launch "
    #                                             "and quit Source SDK from Steam library tools "
    #                                             "at least once.")

    payload_gameconfig = os.path.join(resource_path(), "payload", "GameConfig.txt")
    gameconfig_path = os.path.join(sdk_path, "GameConfig.txt")
    if os.path.exists(gameconfig_path):
        oneshot_window("Continue", f'GameConfig path already exists ({gameconfig_path}). Are you sure you want to continue? If not, abort with the top-right X button.')
        # response = input(f'GameConfig path already exists ({gameconfig_path}). If you want to overwrite it, please type "yes": ')
        # if response.lower() != "yes":
        #     print('Response was not "yes"; exiting.')
        #     sys.exit(1)
        # else:
        #     print(f"Overwriting: {gameconfig_path}")
    with open(payload_gameconfig, mode="r", encoding="utf-8") as f_read:
        data = f_read.read()
        data = data.replace("$NTBASE", neotokyo_base_path)
        data = data.replace("$MAPPING", mapping_path)
        data = data.replace("$SDKPATH", sdk_path)
        data = data.replace("$SDKCONTENTPATH", sdk_content_path)
        with open(gameconfig_path, mode="w", encoding="utf-8") as f_write:
            f_write.write(data)

    try:
        os.makedirs(os.path.join(sdk_content_path, "neotokyo", "mapsrc"))
    except FileExistsError:
        pass


def install_steamapp(app):
    print(f"Installing app {app}...")
    webbrowser.open(f"steam://install/{STEAM_APPIDS[app]}")


def launch_steamapp(app):
    print(f"Launching app {app}...")
    webbrowser.open(f"steam://run/{STEAM_APPIDS[app]}")


def oneshot_window(text_button="",
                   text_label="Please follow the instructions, and press the button when ready.",
                   title=f"Hammer install helper (v{VERSION})"):
    label = sg.Text(text_label)
    button = sg.Button(text_button)
    layout = [[label], [button]]
    window = sg.Window(title, layout)
    event, _ = window.read()
    window.close()
    if event is None:
        sys.exit(0)


def instruct_app_installation(app_name):
    oneshot_window("Ready to begin", f"Steam will now install {app_name}.\nIf it was already installed, nothing will happen, and you can continue as-is.\nOtherwise, please complete the Steam install procedure before continuing.")
    install_steamapp(app_name)
    oneshot_window(f"Press when {app_name} has been fully installed in Steam.", f"Now installing {app_name}. If it was already installed, nothing will happen, and you can continue as-is.")
    oneshot_window(f"Press here to launch {app_name}",
                   f"Please launch {app_name}, and then close it. This step generates some required files.")
    launch_steamapp(app_name)
    oneshot_window(f"Please close {app_name}, and then press this button when you're ready to continue.", f"{app_name} setup completed.")


oneshot_window("Next", "This is an interactive helper tool for setting up Hammer, for mapping for Neotokyo.")
oneshot_window("Next", "Please read the instruction texts carefully before clicking next!\nSome of them will require you to perform actions before continuing.")
oneshot_window("Next", "If you wish to cancel the installation at any time, press the X button in the top-right corner of these popup windows.")
oneshot_window("Ready to continue", "Please open Steam and log in before continuing.")
instruct_app_installation("Neotokyo")
instruct_app_installation("Source SDK")
instruct_app_installation("Source SDK Base 2006")
oneshot_window("Ready to continue", "All Steam requirements are now installed.")
oneshot_window("Ready to generate Hammer configs", "Next, the tool will generate the required GameInfo/GameConfig configs.\nPlease back these up if you need to; we will overwrite them otherwise.")
generate_hammer_config()
oneshot_window("Finish",
               "All done! To launch Hammer, please open Source SDK from Steam library's Tools section.\n"
               'In the "Engine version" section, select "Source SDK 2006".\n'
               'In the "Current Game" section, select "NEOTOKYO".\n\n'
               'If you ran into any bugs/issues when using this tool, please report them at:\n'
               f'{TOOL_HOMEPAGE}')
sys.exit(0)


# if not DEBUG:
#     input("Please launch Steam if it's not already running. Press the Enter key to continue setup.")
#     print("\n## APPS INSTALLATION ##")
#     install_steamapp("Neotokyo")
#     install_steamapp("Source SDK")
#     install_steamapp("Source SDK Base 2006")
#     print("\n## APPS PREREQUISITES ##")
#     launch_steamapp("Neotokyo")
#     launch_steamapp("Source SDK")
# print("\n## GENERATING CONFIGURATION ##")
# generate_hammer_config()
# print('\nAll done! To launch Hammer, please open Source SDK from Steam library\'s Tools section. '
#       'In the "Engine version" section, select "Source SDK 2006". In the "Current Game" section, select "NEOTOKYO".')
# input("\nPress Enter to exit this setup.")