import numpy as np
import pandas as pd
from sklearn.discriminant_analysis import StandardScaler

from utils import musical_key_to_numeric_value, spotify_key_to_musical_key_notation
from weights import AUDIO_FEATURE_WEIGHTS


def standardize_audio_features(df: pd.DataFrame) -> pd.DataFrame:
  # convert numeric keys to musical notation and then to numeric values
  df["key"] = df["key"].apply(spotify_key_to_musical_key_notation)
  df["key"] = df["key"].apply(musical_key_to_numeric_value)

  # standardize the audio features
  features = list(AUDIO_FEATURE_WEIGHTS.keys())
  scaler = StandardScaler()
  df[features] = scaler.fit_transform(df[features])

  return df


def weighted_euclidean_distance(track_1_features, track_2_features) -> float:
  weights = np.array(list(AUDIO_FEATURE_WEIGHTS.values()))
  return np.sqrt(np.sum(weights * (track_1_features - track_2_features) ** 2))


# function to compute the combined transition score
def calculate_song_pair_score(song_1, song_2) -> float:
  features = list(AUDIO_FEATURE_WEIGHTS.keys())

  song_1_features = song_1[features].values
  song_2_features = song_2[features].values

  # calculate weighted euclidean distance between the two songs
  distance = weighted_euclidean_distance(song_1_features, song_2_features)

  # calculate similarity score (higher is better)
  score = 1 / (1 + distance)

  return score

  """
  transition_score = 0.0

  # sum the weighted differences for each feature, lower score means they are more similar
  for (feature_key, feature_weight) in AUDIO_FEATURE_WEIGHTS.items():
    feature_difference = abs(song_1[feature_key] - song_2[feature_key])
    feature_score = feature_difference * ((1 - feature_weight) ** 0.5)

    # print(f'{feature_key}: {song1[feature_key]} -> {song2[feature_key]}: {feature_score}')

    transition_score += feature_score

  # print(f'{song1["song"]} -> {song2["song"]}: {transition_score}')

  return transition_score
  """


# calculate combined score for transitions and create a dataframe
def calculate_transition_scores(df: pd.DataFrame) -> pd.DataFrame:
  transitions = []
  for i in range(len(df)):
    for j in range(len(df)):
      if i != j:
        song_1, song_2 = df.loc[i], df.loc[j]
        score = calculate_song_pair_score(song_1, song_2)

        # add transition to the list
        transitions.append((df.loc[i, "song_id"], df.loc[j, "song_id"], score))
  transitions_df = pd.DataFrame(transitions, columns=["from_song", "to_song", "score"])

  return transitions_df


def optimize_playlist(df: pd.DataFrame) -> pd.DataFrame:
  # calculate the transition scores between songs
  transitions_df = calculate_transition_scores(df)

  # pick a random start song for now
  start_song_id = df.sample(random_state=1)["song_id"].values[-1]
  
  # calculate the best transition for each song pair
  song_ids = [start_song_id]
  current_song_id = start_song_id
  while len(song_ids) < len(df):
    next_transition = transitions_df[transitions_df["from_song"] == current_song_id]
    next_transition = next_transition[~next_transition["to_song"].isin(song_ids)]
    next_song_id = next_transition.sort_values(by="score").iloc[0]["to_song"]
    song_ids.append(next_song_id)
    current_song_id = next_song_id

  # create dataframe with optimal playlist
  optimal_playlist_data = []
  for song_id in song_ids:
    song = df[df["song_id"] == song_id].values[0]
    optimal_playlist_data.append(song)
  optimal_playlist_df = pd.DataFrame(optimal_playlist_data, columns=df.columns)
  
  # print the optimal playlist dataframe, without the 'song_id' column
  print(optimal_playlist_df.drop(columns=["song_id"]))

  return optimal_playlist_df
