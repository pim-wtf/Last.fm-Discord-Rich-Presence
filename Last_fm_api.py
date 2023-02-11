import pylast
import time
from configparser import ConfigParser
from tkinter import messagebox
import DiscordRPC as RPC

config = ConfigParser()
try:
    config.read('settings.ini')
except FileNotFoundError as identifier:
    messagebox.showerror('Error','Assets folder not found!')

API_KEY = config['Last.fm']['api_key']
API_SECRET = config['Last.fm']['api_secret']


network = pylast.LastFMNetwork(api_key=API_KEY, api_secret=API_SECRET)


class LastFmUser:
    def __init__(self, username, cooldown):
        self.username = username
        self.user = network.get_user(username)
        self.cooldown = cooldown

    def now_playing(self, button_state):
        current_track = None
        try:
            current_track = self.user.get_now_playing()
            pass
        except pylast.WSError:
            print("Connection problem at web serice, retrying connection in " +
                  str(self.cooldown)+" seconds")
            pass
        except pylast.NetworkError:
            print("The app couldn't comunicate with last.fm servers, check your internet connection!")
            pass
        except pylast.MalformedResponseError:
            print("Last.fm internal server error!, retrying connection")
            pass

        if current_track is not None:
            track = current_track
            try:
                album,time_remaining = None, 0
                album = track.get_album()
                title = track.get_title()
                artist = track.get_artist()
                artwork = album.get_cover_image()
                time_remaining = track.get_duration()
            except pylast.WSError:
                pass
            except pylast.NetworkError:
                print(
                    "The app couldn't comunicate with last.fm servers, check your internet connection!")
                pass
            RPC.enable_RPC()
            RPC.update_Status(str(track), str(title), str(artist), str(album), time_remaining, self.username, artwork, button_state)
            time.sleep(self.cooldown+8)
        else:
            print("No song detected, checking again in " +
                  str(self.cooldown)+" seconds")
            RPC.disable_RPC()
        time.sleep(self.cooldown)
