import sys
import os
import threading
import asyncio
import time
from configparser import ConfigParser
import tkinter
from tkinter import messagebox
from PIL import Image
from pystray import Icon, Menu, MenuItem as item
from Last_fm_api import LastFmUser
import DiscordRPC

rpc_state = True

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

imageDir = os.path.join(directory, "assets/icon.png")

root = tkinter.Tk()
root.withdraw()

try:
    im = Image.open(imageDir)
except FileNotFoundError as identifier:
    messagebox.showerror('Error','Assets folder not found!')

try:
    config = ConfigParser()
    config.read('settings.ini')
except FileNotFoundError as identifier:
    messagebox.showerror('Error','File "settings.ini" not found!')

try:
    button_state = config['Defaults']['profileButtonIsEnabled']
    if button_state.lower() == 'true':
        button_state = True
    elif button_state.lower() == 'false':
        button_state = False
    else:
        raise ValueError
except ValueError as identifier:
    messagebox.showerror('Error', 'Invalid setting for "profileButtonIsEnabled" in "settings.ini"; Please set it to "True" or "False".')

username = config['Last.fm']['user']
print("Last.fm username: "+username)
User = LastFmUser(username, 2)

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
            User.now_playing(button_state)
        else:
            DiscordRPC.disconnect()
            time.sleep(2)

loop = asyncio.new_event_loop()
RPCThread = threading.Thread(target=RPCFunction, args=(loop,))

RPCThread.daemon = True
RPCThread.start()

icon_tray.run()
