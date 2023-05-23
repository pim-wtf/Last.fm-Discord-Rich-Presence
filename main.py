import sys
import os
import threading
import asyncio
import argparse
import time
import tkinter
from tkinter import messagebox
from PIL import Image
from pystray import Icon, Menu, MenuItem as item
from Last_fm_api import LastFmUser
import DiscordRPC

rpc_state = True
button_state = True

parser = argparse.ArgumentParser(description='Share your Last.fm status on Discord.')
parser.add_argument('--no-gui', dest='gui', action='store_false',
                    help='Run the program without the system tray interface.')
parser.add_argument('--hide-profile-button', dest='profile_button', action='store_true',
                    help='Hide the Last.fm profile button from the Discord presence.')

args = parser.parse_args()

def toggle_rpc(Icon, item):
    global rpc_state
    rpc_state = not item.checked

def toggle_button(Icon, item):
    global button_state
    button_state = not item.checked
    print("Last.fm profile button:", button_state)

def exit(Icon, item):
    icon_tray.stop()

if getattr(sys, 'frozen', False):
    directory = os.path.dirname(sys.executable)
elif __file__:
    directory = os.path.dirname(__file__)

if args.gui:
    imageDir = os.path.join(directory, "assets/icon.png")
    root = tkinter.Tk()
    root.withdraw()

    try:
        im = Image.open(imageDir)
    except FileNotFoundError as identifier:
        messagebox.showerror('Error','Assets folder not found!')

try:
    f = open('username.txt', 'r')
except FileNotFoundError as identifier:
    messagebox.showerror('Error','File "username.txt" not found!')

username = f.read().rstrip()
print("Last.fm username: "+ username)
User = LastFmUser(username, 2)

if args.gui:
    menu_icon = Menu(item('User: '+username, None),
                     item('Enable Rich Presence', toggle_rpc,
                          checked=lambda item: rpc_state), Menu.SEPARATOR,
                     item('Enable Profile Button', toggle_button,
                          checked=lambda item: button_state), Menu.SEPARATOR,
                     item('Exit', exit))

    icon_tray = Icon('Last.fm Discord Rich Presence', icon=im,
                     title="Last.fm Discord Rich Presence", menu=menu_icon)

def RPCFunction(loop):
    print("Starting RPC")
    asyncio.set_event_loop(loop)
    while True:
        if rpc_state == True:
            if args.profile_button:
                button_state = False
            else:
                button_state = True
            User.now_playing(button_state)
        else:
            DiscordRPC.disconnect()
            time.sleep(2)

loop = asyncio.new_event_loop()
RPCThread = threading.Thread(target=RPCFunction, args=(loop,))
RPCThread.daemon = True

if args.gui:
    RPCThread.start()
else:
    RPCThread.run()

if args.gui:
    icon_tray.run()
