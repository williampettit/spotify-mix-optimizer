# function to convert spotify key to musical notation
def spotify_key_to_musical_key_notation(key: int) -> str:
  # https://en.wikipedia.org/wiki/Pitch_class
  key_map = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
  return key_map[key]


# function to convert musical key to a numeric value
def musical_key_to_numeric_value(key: str) -> int:
  key_map = {
    "C": 0, "C#": 1, "Db": 1, "D": 2, "D#": 3, "Eb": 3, "E": 4, "F": 5,
    "F#": 6, "Gb": 6, "G": 7, "G#": 8, "Ab": 8, "A": 9, "A#": 10, "Bb": 10, "B": 11,
    "Cm": 12, "C#m": 13, "Dbm": 13, "Dm": 14, "D#m": 15, "Ebm": 15, "Em": 16, "Fm": 17,
    "F#m": 18, "Gbm": 18, "Gm": 19, "G#m": 20, "Abm": 20, "Am": 21, "A#m": 22, "Bbm": 22, "Bm": 23
  }
  return key_map[key]
