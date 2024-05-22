#
# this file contains my wrapper functions around the spotipy library
#

import dotenv
dotenv.load_dotenv()

import os
import pandas as pd
import spotipy
from spotipy.oauth2 import SpotifyOAuth

from algorithm import AUDIO_FEATURE_WEIGHTS


# function to set up spotify api credentials
def init_spotify():
  client_id = os.getenv("SPOTIFY_CLIENT_ID")
  client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
  redirect_uri = "http://localhost:3000"
  scope = "playlist-modify-public playlist-modify-private"
  sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id,
                                                 client_secret=client_secret,
                                                 redirect_uri=redirect_uri,
                                                 scope=scope))
  return sp


# function to fetch playlist tracks
def fetch_playlist_tracks(sp, playlist_id):
  tracks = []
  results = sp.playlist_tracks(playlist_id)
  while results:
    tracks.extend(results["items"])
    if results["next"]:
      results = sp.next(results)
    else:
      results = None
  return tracks


# function to fetch playlist tracks and audio features
def fetch_playlist(sp, playlist_id):
  # fetch playlist tracks and audio features
  tracks = fetch_playlist_tracks(sp, playlist_id)
  track_ids = [track["track"]["id"] for track in tracks]
  audio_features = []
  for i in range(0, len(track_ids), 100):
    audio_features.extend(sp.audio_features(track_ids[i:i+100]))
  
  # extract relevant data and create a dataframe
  songs_data = []
  for (track, features) in zip(tracks, audio_features):
    # extract audio features and add song data to the list
    song_data = {
      "song": track["track"]["name"],
      "song_id": track["track"]["id"],
      "artist": track["track"]["artists"][0]["name"],
      "album": track["track"]["album"]["name"],
    }
    for feature in AUDIO_FEATURE_WEIGHTS:
      song_data[feature] = features[feature]
    
    songs_data.append(song_data)
  df = pd.DataFrame(songs_data)

  return df


# function to save the optimal playlist to the user's spotify account
def save_playlist(sp, optimal_playlist_df, playlist_id):
  # get current user id
  current_user = sp.current_user()
  assert current_user is not None, "User not found"
  user_id = current_user["id"]
  
  # fetch original playlist name
  playlist_metadata = sp.playlist(playlist_id)
  assert playlist_metadata is not None, "Playlist not found"
  original_playlist_name = playlist_metadata["name"]
  playlist_name = f"Mixed: {original_playlist_name}"
  
  # select track ids from the optimal playlist dataframe
  track_ids = optimal_playlist_df["song_id"].values
  assert len(track_ids) > 0, "No tracks found in the playlist"

  # create a new playlist
  playlist = sp.user_playlist_create(user=user_id, name=playlist_name, public=False)
  playlist_id = playlist["id"]
  
  # add tracks to the playlist (spotify allows adding up to 100 tracks at a time)
  for i in range(0, len(track_ids), 100):
    sp.playlist_add_items(playlist_id, track_ids[i:i+100])
  
  print(f"Playlist created with ID: {playlist_id}")
