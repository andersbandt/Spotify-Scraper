

# import needed modules
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns


##############################################################################
####      ARTIST/SONG ANALYSIS           #####################################
##############################################################################

def uniq_artist(spotify_stream_df):
    unique_artists = spotify_stream_df["master_metadata_album_artist_name"].nunique()  # Count number of unique artist in dataset

    total_artists = spotify_stream_df["master_metadata_album_artist_name"].count()
    # Count total artist in dataset
    unique_artist_percentage = unique_artists / total_artists * 100

    print(unique_artist_percentage)

    unique_artist_list = np.array([unique_artists, total_artists - unique_artists])
    unique_artist_list_labels = [" Unique Artists", "Non Unique Artists"]
    fig, ax = plt.subplots(figsize=(12, 6))

    ax.pie(unique_artist_list, labels=unique_artist_list_labels, autopct='%1.1f%% ', explode=[0.05, 0.05], startangle=180, shadow=True)

    plt.title("Unique Artist Percentage")
    plt.show()

    # top_10_artist_df = spotify_stream_df.groupby(["master_metadata_album_artist_name"])[["Listening Time(Hours)", "Listening Time(Minutes)", "Count"]].sum().sort_values(by="Listening Time(Minutes)", ascending=False)
    #
    # print("Top 10 unique artists below")
    # print(top_10_artist_df.head(10))


# uniq_song_from_artist: gets a collection of unique songs from a collection of artists
def uniq_song_from_artist(sp_df, num, type="ms_played"):

    # extract array of top artists. This will form the basis for our search for unique songs from these artists
    top_artists = sp_df.groupby(["master_metadata_album_artist_name"])[[type]].sum().sort_values(by=type, ascending=False)
    top_artists = top_artists[0:num]
    top_artists = top_artists.index.tolist()

    num_unique = []
    for artist in top_artists:
        print("INFO: examining artist - "+ artist)

        # get list of unique songs
        artist_songs = sp_df[sp_df["master_metadata_album_artist_name"] == artist]  # Count number of unique artist in dataset
        a_un = artist_songs["master_metadata_track_name"].nunique()
        print(a_un)
        num_unique.append(a_un)

    # now generate a plot
    plt.bar(top_artists, num_unique, color="green") # NOTE the conversion from ms to hours
    plt.xlabel("Artist")
    plt.ylabel("Number of unique songs")
    plt.subplots_adjust(bottom=0.6)
    plt.tick_params(labelrotation=75)
    plt.title("Number of unique songs from top artists")
    plt.show()



# gets the top 'num' songs based on type (# of times played vs. playtime)
def uniq_song(sp_df, num, type="ms_played"):
    # extract array of top songs by type selected [either "Count" or playtime/"ms_played"]
    top_songs_time_df = sp_df.groupby(["master_metadata_track_name"])[[type]].sum().sort_values(by=type, ascending=False)

    print("Top 10 songs below")
    print(top_songs_time_df[0:20])

    if type == "ms_played":
        plt.bar(top_songs_time_df.head(num).head(num).index, top_songs_time_df[type].head(num)*2.77E-7, color="green") # NOTE the conversion from ms to hours
    elif type == "Count":
        plt.bar(top_songs_time_df.head(num).head(num).index, top_songs_time_df[type].head(num), color="green")
    plt.xlabel("Song")
    plt.ylabel(type)
    plt.subplots_adjust(bottom=0.6)
    plt.tick_params(labelrotation=75)
    plt.title("Top Songs by " + type)
    # plt.tight_layout() # kind of helps the labels from getting cutoff but also sucks
    plt.show()






##############################################################################
####      PLAYTIME ANALYSIS              #####################################
##############################################################################

# gets usage for when I'm listening to music across day (hours 0 to 24)
# STATUS: not functional?
def daytime_usage(sp_df):
    fig, ax = plt.subplots(figsize=(12, 8))
    ax.set(title="Average Distribution of Streaming Over Day Hours", xlabel="Hours (in 24 hour format)",
           ylabel="Songs Played")
    sns.histplot(sp_df["ts"], bins=24, kde=True, color="darkgreen")
    plt.show()


# year_usage: gets aggregate usage across months (00 to 12)
def year_usage(sp_df):
    fig, ax = plt.subplots(figsize=(12, 6))
    sp_df["month"] = pd.DatetimeIndex(sp_df["datetime"]).month
    ax = sns.countplot(y=sp_df["month"], ax=ax)
    ax.set(title="Average Spotify Usage across a Year", xlabel="Songs Played in Counts", ylabel="Months(1 - 12)")
    plt.show()


# gets the number of songs I play in a day
def max_song_day(sp_df):
    # creating a new column with datetime format
    sp_df["date"] = sp_df["datetime"].dt.date

    most_songs = sp_df.groupby(["date"])[["Count"]].sum().sort_values(by="Count", ascending=False)
    print("Dates I played the most songs below")
    print(most_songs.head(5))

    fig, ax = plt.subplots(figsize=(15, 8))
    ax.scatter(most_songs.index, most_songs["Count"]);
    ax.set(title="Maximum number of songs played in a day", xlabel="Date", ylabel="Count");
    ax.axhline(most_songs["Count"].mean(), linestyle="-", color="r");

    plt.show()


