#!/usr/bin/env python3

"""An interactive GUI helper for setting up Source SDK and Hammer editor for NT mapping."""

import os
assert os.name == "nt", "This script supports Windows only."
import sys

from functools import partial
import webbrowser
import winreg

import pyperclip
import PySimpleGUI as sg
from valve_keyvalues_python.valve_keyvalues_python.keyvalues import KeyValues


COPYRIGHT = """
   Copyright (C) 2022 github.com/Rainyan

   This program is free software: you can redistribute it and/or modify
   it under the terms of the GNU General Public License as published by
   the Free Software Foundation, either version 3 of the License, or
   (at your option) any later version.

   This program is distributed in the hope that it will be useful,
   but WITHOUT ANY WARRANTY; without even the implied warranty of
   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
   GNU General Public License for more details.

   You should have received a copy of the GNU General Public License
   along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

ACKNOWLEDGEMENTS = """
    This project uses the following open-source software:

    - valve-keyvalues-python (https://github.com/gorgitko/valve-keyvalues-python)
    - PySimpleGUI (https://github.com/PySimpleGUI/PySimpleGUI)
    - Pyperclip (https://github.com/asweigart/pyperclip)
"""


# This needs to be in the install order.
STEAM_APPIDS = {
    "Neotokyo": 244630,
    "Source SDK": 211,
    "Source SDK Base 2006": 215,
}

TOOL_HOMEPAGE = "https://github.com/Rainyan/nt-hammer-bootstrap"

VERSION = "0.5.4"


def resource_path():
    """Returns the resource path."""
    try:
        base_path = sys._MEIPASS  # pylint: disable=protected-access
    except AttributeError:
        debug(False, "PyInstaller did not set sys._MEIPASS!")
        base_path = os.path.dirname(os.path.realpath(__file__))
    return os.path.normpath(base_path)


def get_steam_install_path():
    """Returns the path where Steam is installed."""
    keys = (
        "SOFTWARE\\Wow6432Node\\Valve\\Steam",  # x64
        "SOFTWARE\\Valve\\Steam",  # x86
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
    debug(False, "Could not find Steam install path")


def generate_hammer_config():
    """Generates the GameInfo.txt and GameConfig.txt configs for NT Hammer."""
    neotokyo_base_path = os.path.join(get_app_install_path(STEAM_APPIDS["Neotokyo"]), "NEOTOKYO")
    stack = []
    if not os.path.isdir(neotokyo_base_path):
        oneshot_window("Abort", "Could not find NEOTOKYO Steam installation.")
        sys.exit(1)
    mapping_path = os.path.join(neotokyo_base_path, "mapping")
    try:
        print(f"{mapping_path=}")
        os.mkdir(mapping_path)
    except FileExistsError:
        stack.append(partial(oneshot_window,
                             "Continue",
                             "Mapping path already exists! "
                             "Are you sure you want to continue?\n"
                             "If not, abort with the top-right X button."))
        show_stack(stack)

    respath = resource_path()
    debug(os.path.isdir(respath), "Respath is not a valid directory")

    gameinfo_readpath = os.path.join(resource_path(), "payload", "GameInfo.txt")
    debug(os.path.isfile(gameinfo_readpath), "GameInfo readpath file must exist")

    print(f'gameinfo readpath: {os.path.join(resource_path(), "payload", "GameInfo.txt")}')
    print(f'gameinfo writepath: {os.path.join(mapping_path, "GameInfo.txt")}')

    with open(gameinfo_readpath, mode="r", encoding="utf-8") as f_read:
        with open(os.path.join(mapping_path, "GameInfo.txt"),
                  mode="w", encoding="utf-8") as f_write:
            f_write.write(f_read.read())

    source_sdk_base_path = os.path.join(get_app_install_path(STEAM_APPIDS["Source SDK"]))
    sdk_path = os.path.join(source_sdk_base_path, "SourceSDK", "bin", "ep1", "bin")
    sdk_content_path = os.path.join(source_sdk_base_path, "sourcesdk_content")

    if (not os.path.isdir(source_sdk_base_path) or
            not os.path.isdir(sdk_path) or
            not os.path.isdir(sdk_content_path)):
        oneshot_window("Abort", "Could not find Source SDK installation.\n"
                                "Make sure you have both Source SDK and "
                                "Source SDK Base 2006 installed,\nand launch "
                                "and quit Source SDK from Steam library tools "
                                "at least once.")
        sys.exit(1)

    payload_gameconfig = os.path.join(resource_path(), "payload", "GameConfig.txt")
    debug(os.path.isfile(payload_gameconfig), "Failed to read payload GameConfig")

    gameconfig_path = os.path.join(sdk_path, "GameConfig.txt")
    if os.path.exists(gameconfig_path):
        stack.append(partial(oneshot_window,
                             "Continue",
                             f'GameConfig path already exists ({gameconfig_path}).'
                             "\nAre you sure you want to continue? "
                             "If not, abort with the top-right X button."))
        show_stack(stack)

    with open(payload_gameconfig, mode="r", encoding="utf-8") as f_read:
        data = f_read.read()
        data = data.replace("$NTBASE", neotokyo_base_path)
        data = data.replace("$MAPPING", mapping_path)
        data = data.replace("$SDKPATH", sdk_path)
        data = data.replace("$SDKCONTENTPATH", sdk_content_path)
        with open(gameconfig_path, mode="w", encoding="utf-8") as f_write:
            f_write.write(data)

    os.makedirs(os.path.join(sdk_content_path, "neotokyo", "mapsrc"),
                exist_ok=True)
    debug(os.path.isdir(os.path.join(sdk_content_path, "neotokyo", "mapsrc")),
          "Failed to recursively build neotokyo mapsrc")


def install_steamapp(app):
    """Initiates a Steam install of an app.

       Input: App name which has a STEAM_APPIDS value defined."""
    print(f"Installing app {app}...")
    webbrowser.open(f"steam://install/{STEAM_APPIDS[app]}")


def launch_steamapp(app):
    """Launches a Steam app.

       Input: App name which has a STEAM_APPIDS value defined."""
    print(f"Launching app {app}...")
    webbrowser.open(f"steam://run/{STEAM_APPIDS[app]}")


def error_window(error="Unknown error"):
    """Create a blocking one-and-done critical error GUI window.

       Execution will end with error code once this window closes.
    """
    title=f"Hammer install helper (v{VERSION})"
    copy_button_text = "Copy error message to clipboard"
    while True:
        label = sg.Text(error)
        button_copy = sg.Button(copy_button_text)
        button_exit = sg.Button("Abort")
        layout = [ [label], [button_copy], [button_exit] ]
        window = sg.Window(title, layout)
        event, _ = window.read()
        window.close()
        if event == copy_button_text:
            pyperclip.copy(error)
            copy_button_text = "✔️Copied to clipboard"
        else:
            break
    sys.exit(1)


def oneshot_window(text_button="",
                   text_label="Please follow the instructions, and press the button when ready.",
                   title=f"Hammer install helper (v{VERSION})"):
    """Create a blocking one-and-done GUI window.

       Returns whether this window should get re-displayed after blocking."""
    label = sg.Text(text_label)
    button = sg.Button(text_button)
    layout = [
        [sg.Menu( [["&Help", ["&About"]]] ),
        [label], [button]] ]
    window = sg.Window(title, layout)
    event, _ = window.read()
    window.close()
    if event is None:
        sys.exit(0)
    elif event == "About":
        show_about()
        return True
    return False


def debug(*assertion):
    """Debug helper for visualizing failed assertions.

       First argument is asserted, and all arguments are dumped in the error
       message."""
    try:
        assert assertion[0]
        print("Assertion passed")
    except AssertionError:
        error_window(f"{assertion=}")


def get_app_install_path(appid):
    """Return the path where a Steam AppID is installed."""
    libfolders = os.path.join(get_steam_install_path(), "config", "libraryfolders.vdf")
    debug(os.path.exists(libfolders), f"os.path.exists(libfolders): {libfolders=}")
    kv = KeyValues(filename=libfolders)  # pylint: disable=invalid-name
    for k in kv["libraryfolders"]:
        if not str(appid) in kv["libraryfolders"][k]["apps"]:
            continue
        return os.path.normpath(os.path.join(kv["libraryfolders"][k]["path"],
                                             "steamapps",
                                             "common"))
    debug(False, f"Could not find app install path ({appid=})")


def show_about():
    """Show copyright stuff."""
    sg.popup(
        "About this app",
        ("COPYRIGHT:\n\n" +
         COPYRIGHT +
         "\n\n- - - - - - - - - -\n\nACKNOWLEDGEMENTS:\n" +
         ACKNOWLEDGEMENTS)
    )


def instruct_app_installation(app_name):
    """Specialized version of oneshot_window() for Steam app installation.

       Input: App name which has a STEAM_APPIDS value defined."""
    stack = []
    stack.append(partial(oneshot_window,
                         "Ready to begin",
                         f"Steam will now install {app_name}.\nIf it was already installed, "
                         "nothing will happen, and you can continue as-is.\nOtherwise, please "
                         "complete the Steam install procedure before continuing."))
    show_stack(stack)
    install_steamapp(app_name)
    stack.append(partial(oneshot_window,
                         f"Press when {app_name} has been fully installed in Steam.",
                         f"Now installing {app_name}. If it was already installed, "
                         "nothing will happen, and you can continue as-is."))
    stack.append(partial(oneshot_window,
                         f"Press here to launch {app_name}",
                         f"Please launch {app_name}, and then close it. "
                         "This step generates some required files."))
    show_stack(stack)
    launch_steamapp(app_name)
    stack.append(partial(oneshot_window,
                         f"Please close {app_name}, and then press this button when you're "
                         "ready to continue.", f"{app_name} setup completed."))
    show_stack(stack)


def show_stack(stack):
    """Given a stack of GUI windows, pop and display them all in FIFO order."""
    stack.reverse()
    while True:
        try:
            gui_function = stack.pop()
            while True:
                if not gui_function():
                    break
        except IndexError:
            break


STACK = []
STACK.append(partial(oneshot_window,
                     "Next",
                     "This is an interactive helper tool for setting up Hammer, "
                     "for mapping for Neotokyo."))
STACK.append(partial(oneshot_window,
                     "Next",
                     "Please read the instruction texts carefully before clicking next!\n"
                     "Some of them will require you to perform actions before continuing."))
STACK.append(partial(oneshot_window,
                     "Next",
                     "If you wish to cancel the installation at any time,\npress the X button "
                     "in the top-right corner of these popup windows."))
STACK.append(partial(oneshot_window,
                     "Ready to continue",
                     "Please open Steam and log in before continuing."))
show_stack(STACK)


for steamapp in STEAM_APPIDS:
    instruct_app_installation(steamapp)


STACK.append(partial(oneshot_window,
                     "Ready to continue",
                     "All Steam requirements are now installed."))
STACK.append(partial(oneshot_window,
                     "Ready to generate Hammer configs",
                     "Next, the tool will generate the required GameInfo/GameConfig configs.\n"
                     "Please back these up if you need to; we will overwrite them otherwise."))
show_stack(STACK)
generate_hammer_config()
STACK.append(partial(oneshot_window,
                     "Finish",
                     "All done! To launch Hammer, please open Source SDK from Steam library's "
                     'Tools section.\nIn the "Engine version" section, select "Source SDK 2006".\n'
                     'In the "Current Game" section, select "NEOTOKYO".\n\n'
                     'If you ran into any bugs/issues when using this tool, '
                     'please report them at:\n'
                     f'{TOOL_HOMEPAGE}'))
show_stack(STACK)
