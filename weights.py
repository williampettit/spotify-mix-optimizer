# TODO
# SAME_ARTIST_WEIGHT = 0.1
# SAME_ALBUM_WEIGHT = 0.1

# weights for audio features (0.0 - 1.0)
# where a higher weight means to care more about that feature being similar between songs
AUDIO_FEATURE_WEIGHTS = {
  "tempo":            0.90,
  "key":              0.45,
  "danceability":     0.65,
  "energy":           0.60,
  "loudness":         0.35,
  "valence":          0.85,
  "mode":             0.10,
  "time_signature":   0.15,

  # don't care about these audio features for now
  # "speechiness":      0.0,
  # "acousticness":     0.0,
  # "instrumentalness": 0.0,
  # "liveness":         0.0,
}
