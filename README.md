# mix-optimizer
My tool will automatically compute an optimal DJ mix (transitions) for your Spotify playlist.

Initially, I was only using least BPM differences and least musical key differences between songs, but now the tool also makes use of several other audio feature datapoints available through the Spotify track API, including: 
- tempo (BPM)
- key
- danceability
- energy
- loudness
- valence
- mode
- time_signature

More info on the audio features and what they represent can be found here: https://developer.spotify.com/documentation/web-api/reference/get-audio-features

## Instructions
- Generate a Spotify client ID and secret [here](https://developer.spotify.com/dashboard)
- Create a `.env` file in the same directory as `main.py` and add the ID/secret there (see `.env.example`)
- Install the required Python modules (run `pip install -r requirements.txt`)[^1]
- Run `python main.py` and enter your playlist ID when asked

[^1]: Using a Python virtual environment is optional but recommended

## License
MIT
