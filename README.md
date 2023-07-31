# Spotify-Scraper
Repo for analyzing the extended streaming history from Spotify

Credit to jayeshironside for [his original work on analyzing Spotify data](https://github.com/jayeshironside/Spotify-Streaming-history-analysis). His code served as a great starting point for me.

## Spotify Data Requirements
This repo needs your "extended streaming history" from Spotify. You can request this data on their site. It can take up to 30 days for them to generate it and send you a download link.

The data is pretty much a collection of JSON files representing EVERY time you have played a song through Spotify (or so I believe). Info like time played, how long you played the song for, device used, artist/song, whether you pressed skip or not is gathered.

## Analysis of Data
There's kind of two interesting aspects to analyze in the data

1. Top *artists* and *songs*
2. Listening **habits** (usage throughout a day, amount used between months, daily max songs across time)

There is a third category I see as well

3. Listening *preferences**

but I think that will require some additional datasets. The data Spotify sends you is purely ACCOUNT data, and is missing all the treasure troves of additional data I'm sure they on which they used to actually map your preferences and recommend songs. However, maybe simply a dataset mapping song names to simple genre would be good for some simple analysis

## Usage
Simply clone the repository and change the `file_dir` variable in `main.py`

```
# establish file information
file_dir = "C:/your_path_here"
```
Then run `main.py`. You can comment/uncomment functions to change what plots will get generated
```
python main.py
```
