import dotenv
dotenv.load_dotenv()

import spotipy
from spotipy.oauth2 import SpotifyOAuth
import pandas as pd
import os
from sklearn.preprocessing import StandardScaler

#
# constants
#

# TODO
# SAME_ARTIST_WEIGHT = 0.1
# SAME_ALBUM_WEIGHT = 0.1

# weights for audio features (0.0 - 1.0)
# where a higher weight means to care more about that feature being similar between songs
AUDIO_FEATURE_WEIGHTS = {
  'tempo':            0.90,
  'key':              0.45,
  'danceability':     0.65,
  'energy':           0.60,
  'loudness':         0.35,
  'valence':          0.85,
  'mode':             0.10,
  'time_signature':   0.15,

  # don't care about these audio features for now
  # 'speechiness':      0.0,
  # 'acousticness':     0.0,
  # 'instrumentalness': 0.0,
  # 'liveness':         0.0,
}

#
# helper functions
#


# function to set up spotify api credentials
def init_spotify():
  client_id = os.getenv('SPOTIFY_CLIENT_ID')
  client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')
  redirect_uri = 'http://localhost:3000'
  scope = 'playlist-modify-public playlist-modify-private'
  sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id,
                                                 client_secret=client_secret,
                                                 redirect_uri=redirect_uri,
                                                 scope=scope))
  return sp


# function to convert spotify key to musical notation
def spotify_key_to_musical_key_notation(key: int) -> str:
  # https://en.wikipedia.org/wiki/Pitch_class
  key_map = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
  return key_map[key]


# function to convert musical key to a numeric value
def musical_key_to_numeric_value(key: str) -> int:
  key_map = {
    'C': 0, 'C#': 1, 'Db': 1, 'D': 2, 'D#': 3, 'Eb': 3, 'E': 4, 'F': 5,
    'F#': 6, 'Gb': 6, 'G': 7, 'G#': 8, 'Ab': 8, 'A': 9, 'A#': 10, 'Bb': 10, 'B': 11,
    'Cm': 12, 'C#m': 13, 'Dbm': 13, 'Dm': 14, 'D#m': 15, 'Ebm': 15, 'Em': 16, 'Fm': 17,
    'F#m': 18, 'Gbm': 18, 'Gm': 19, 'G#m': 20, 'Abm': 20, 'Am': 21, 'A#m': 22, 'Bbm': 22, 'Bm': 23
  }
  return key_map[key]


# function to generate the optimal playlist
def generate_playlist(df, transitions_df, start_song_id):
  playlist = [start_song_id]
  current_song_id = start_song_id
  while len(playlist) < len(df):
    next_transition = transitions_df[transitions_df['from_song'] == current_song_id]
    next_transition = next_transition[~next_transition['to_song'].isin(playlist)]
    next_song_id = next_transition.sort_values(by='score').iloc[0]['to_song']
    playlist.append(next_song_id)
    current_song_id = next_song_id
  return playlist


# function to create a spotify playlist and add tracks
def create_spotify_playlist(sp, user_id, playlist_name, track_ids):
  # create a new playlist
  playlist = sp.user_playlist_create(user=user_id, name=playlist_name, public=False)
  playlist_id = playlist['id']
  
  # add tracks to the playlist (spotify allows adding up to 100 tracks at a time)
  for i in range(0, len(track_ids), 100):
    sp.playlist_add_items(playlist_id, track_ids[i:i+100])
  
  return playlist_id


# function to compute the combined transition score
def compute_transition_score(song1, song2):
  if song1['song_id'] == song2['song_id']:
    return 0.0

  transition_score = 0.0

  # sum the weighted differences for each feature, lower score means they are more similar
  for (feature_key, feature_weight) in AUDIO_FEATURE_WEIGHTS.items():
    feature_difference = abs(song1[feature_key] - song2[feature_key])
    feature_score = feature_difference * ((1 - feature_weight) ** 0.5)

    # print(f'{feature_key}: {song1[feature_key]} -> {song2[feature_key]}: {feature_score}')

    transition_score += feature_score

  # print(f'{song1["song"]} -> {song2["song"]}: {transition_score}')

  return transition_score


# function to fetch playlist tracks
def fetch_playlist_tracks(sp, playlist_id):
  tracks = []
  results = sp.playlist_tracks(playlist_id)
  while results:
    tracks.extend(results['items'])
    if results['next']:
      results = sp.next(results)
    else:
      results = None
  return tracks


# function to fetch audio features for a list of track ids
def fetch_audio_features(sp, track_ids):
  audio_features = []
  for i in range(0, len(track_ids), 100):
    audio_features.extend(sp.audio_features(track_ids[i:i+100]))
  return audio_features


# main
def main() -> None:
  # initialize spotify api
  sp = init_spotify()

  # get playlist id from user
  playlist_id = input('enter your playlist id: ')

  # fetch playlist tracks and audio features
  tracks = fetch_playlist_tracks(sp, playlist_id)
  input(f'Press Enter to continue with {len(tracks)} tracks in the playlist')
  track_ids = [track['track']['id'] for track in tracks]
  audio_features = fetch_audio_features(sp, track_ids)

  # extract relevant data and create a dataframe
  songs_data = []
  for (track, features) in zip(tracks, audio_features):
    # extract audio features and add song data to the list
    song_data = {
      'song': track['track']['name'],
      'song_id': track['track']['id'],
      'artist': track['track']['artists'][0]['name'],
      'album': track['track']['album']['name'],
    }
    for feature in AUDIO_FEATURE_WEIGHTS:
      song_data[feature] = features[feature]
    
    songs_data.append(song_data)
  df = pd.DataFrame(songs_data)

  # convert numeric keys to musical notation and then to numeric values
  df['key'] = df['key'].apply(spotify_key_to_musical_key_notation)
  df['key'] = df['key'].apply(musical_key_to_numeric_value)

  # standardize the audio features
  features = list(AUDIO_FEATURE_WEIGHTS.keys())
  scaler = StandardScaler()
  df[features] = scaler.fit_transform(df[features])

  # calculate combined score for transitions and create a dataframe
  transitions = []
  for i in range(len(df)):
    for j in range(len(df)):
      if i != j:
        song1 = df.loc[i]
        song2 = df.loc[j]
        score = compute_transition_score(song1, song2)

        # add transition to the list
        transitions.append((df.loc[i, 'song_id'], df.loc[j, 'song_id'], score))
  transitions_df = pd.DataFrame(transitions, columns=['from_song', 'to_song', 'score'])

  # sort transitions by score
  # sorted_transitions = transitions_df.sort_values(by='score')
  # print(sorted_transitions)

  # generate the optimal playlist, pick a random start song for now
  start_song_id = df.sample(random_state=1)['song_id'].values[-1]
  # start_song_name = df[df['song_id'] == start_song_id]['song'].values[0]
  # print(f'{start_song_id = }')
  # print(f'{start_song_name = }')
  optimal_track_id_order = generate_playlist(df, transitions_df, start_song_id)
  
  # create a dataframe with the optimal playlist including song and artist names
  optimal_playlist_data = []
  for song_id in optimal_track_id_order:
    song = df[df['song_id'] == song_id].values[0]
    optimal_playlist_data.append(song)
  optimal_playlist_df = pd.DataFrame(optimal_playlist_data, columns=df.columns)
  
  # print the optimal playlist dataframe, without the 'song_id' column
  print(optimal_playlist_df.drop(columns=['song_id']))

  # ask for confirmation before saving the playlist
  input('Press Enter to save the playlist to your Spotify account')

  # fetch original playlist name
  playlist_metadata = sp.playlist(playlist_id)
  assert playlist_metadata is not None, 'Playlist not found'
  original_playlist_name = playlist_metadata['name']

  # save the optimal playlist to the user's spotify account
  current_user = sp.current_user()
  assert current_user is not None, 'User not found'
  user_id = current_user['id']
  playlist_name = f'Mixed: {original_playlist_name}'
  
  # select track ids from the optimal playlist dataframe
  track_ids = optimal_playlist_df['song_id'].values
  assert len(track_ids) == len(optimal_track_id_order), 'Error in generating the playlist'
  assert len(track_ids) > 0, 'No tracks found in the playlist'

  # create a new playlist and add tracks
  playlist_id = create_spotify_playlist(sp, user_id, playlist_name, track_ids)
  print(f'Playlist created with ID: {playlist_id}')


if __name__ == '__main__':
  main()
