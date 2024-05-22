import sys

from algorithm import optimize_playlist, standardize_audio_features
from spotify import init_spotify, fetch_playlist, save_playlist


def main() -> None:
  # init spotify api
  sp = init_spotify()

  # get playlist id from user
  if len(sys.argv) > 1:
    playlist_id = sys.argv[1]
  else:
    playlist_id = input("Enter your playlist ID or URL: ")
  if playlist_id.startswith("https://open.spotify.com/playlist/"):
    playlist_id = playlist_id.split("/")[-1]
    playlist_id = playlist_id.split("?")[0]

  # fetch playlist tracks + audio features
  df = fetch_playlist(sp, playlist_id)
  
  # standardize the audio features
  df = standardize_audio_features(df)

  # determine optimal song order
  optimized_playlist_df = optimize_playlist(df)

  # save optimal playlist to user's account
  save_playlist(sp, optimized_playlist_df, playlist_id)


if __name__ == "__main__":
  main()
