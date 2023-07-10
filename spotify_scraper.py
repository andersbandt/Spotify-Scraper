
# spotify_scraper.py
#   this file is good for scraping and cleaning up the data
#   provided by Spotify when you download your "Extended Streaming History"
#   which is files in JSON format

# written by Anders Bandt
# Summer 2023

# import needed modules
import json
import pandas as pd
import os


def extract_data(file_dir):
    # Get all file names in the directory
    file_names = os.listdir(file_dir)
    # file_names = [file for file in file_names if os.path.isfile(os.path.join(file_dir, file))]
    file_names = [file for file in os.listdir(file_dir) if file.endswith(".json")]
    print(file_names)

    # METHOD 2: leveraging pandas
    df = []  # array to track all the loaded JSON data

    for file in file_names:
        df.append(pd.read_json(file_dir+file))

    # print out some information about the first file
    # print("Head information of a particular file below")
    # print(df[0].head(2))
    # print("Tail information of a particular file below")
    # print(df[0].tail(2))

    # concatenate the data
    spotify_df = pd.concat(df, ignore_index=True)  # apparently the warning is ok?

    # export to .csv
    # spotify_df.to_csv(file_dir + "spotify_data.csv")

    return spotify_df


def clean_data(sp_data):
    # add a 'Count' column
    sp_data["Count"] = 1

    # add a datetime column
    # creating a new column with datetime format
    sp_data["datetime"] = pd.to_datetime(sp_data["ts"])

    # finally print some info about our full data set
    # print(sp_data.describe())
    print("INFO: Printing shape information of dataset below")
    print(sp_data.shape)
    # print(spotify_df.info())
    print("INFO: Printing number of unique column info below")
    print(sp_data.nunique())

    return sp_data
