
# this is a script for analyzing extended Spotify streaming activity from GitHub

# import needed modules
import spotify_scraper
import spotify_analysis


# establish file information
file_dir = "C:/Users/ander/OneDrive/Documents/Company Data Exports/Spotify/2023_06_21 Request/my_spotify_data - Extended Streaming History/MyData/"


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    # extract data
    sp_dt = spotify_scraper.extract_data(file_dir)

    # clean data
    sp_dt = spotify_scraper.clean_data(sp_dt)

    # get SOME INFORMATION ABOUT MY LISTENING
    #spotify_analysis.uniq_artist(data)
    spotify_analysis.uniq_song(sp_dt, 50, type="Count")
    # spotify_analysis.daytime_usage(sp_dt)
    # spotify_analysis.year_usage(sp_dt)
    # spotify_analysis.max_song_day(sp_dt)

    # spotify_analysis.uniq_song_from_artist(sp_dt, 50, type="Count")


