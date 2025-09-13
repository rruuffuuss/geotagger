#!/usr/bin/env python
import sys
import pyexiv2
import os
import numpy as np
import pandas as pd
import gpx_to_df
from fractions import Fraction

time_offset = pd.Timedelta(1,'h')
window_length = pd.Timedelta(2,'m')

#im_dir = "/mnt/c/Users/fsb23191/OneDrive - University of Strathclyde/Documents/Programming/Tagger/Images"
#gpx_dir = "/mnt/c/Users/fsb23191/OneDrive - University of Strathclyde/Documents/Programming/Tagger/GPSData"

def main():

    gpx_df = pd.DataFrame(columns={
         "lat":pd.Series(dtype='Float64'), 
         "lon":pd.Series(dtype='Float64'), 
         "ele":pd.Series(dtype='Float64'), 
         "time":pd.Series(dtype='datetime64[ns]'), 
         "src":pd.Series(dtype='string')})

    for file in os.scandir(gpx_dir):
        if(file.is_file() and file.path.endswith("gpx")):
             concatval = gpx_to_df.gpx_to_df(file.path)
             gpx_df = pd.concat([gpx_df, concatval]).sort_values(by="time",ignore_index="true")

    print(gpx_df.head(5))
    print(gpx_df.info())
            

    for file in os.scandir(im_dir):
        if(file.is_file() and file.path.lower().endswith("jpg")):

            exiv_metadata = pyexiv2.ImageMetadata(file.path)
            exiv_metadata.read()
            
            closest, in_window = get_gpx_entry_by_time(exiv_metadata, gpx_df, time_offset)
            
            if in_window:

                lat, lon = closest['lat'], closest['lon']

                print("geotagging " + file.path + " with coords " + lat + ", " + lon )

                set_gps_location(exiv_metadata, float(lat), float(lon))
                exiv_metadata.write()

            else:
                print("no gpx data found close enough to the image creation time")


        
    #set_gps_location(sys.argv[1], float(sys.argv[2]), float(sys.argv[3]))

def get_gpx_entry_by_time(exiv_metadata, gpx_df, time_offset):
    
    search_timestamp = pd.to_datetime(np.datetime64(exiv_metadata["Exif.Photo.DateTimeOriginal"].value) + time_offset, utc=True)
    print(search_timestamp)
    gpx_index = gpx_df['time'].searchsorted(search_timestamp)


    if(gpx_index) != 0 and gpx_index != gpx_df.size:
        front = gpx_df.iloc[gpx_index]
        back = gpx_df.iloc[gpx_index - 1]

        front_delta = abs((front['time'] - search_timestamp).total_seconds())
        
        back_delta = abs((back['time'] - search_timestamp).total_seconds())

        if front_delta < back_delta:
            closest_entry = front
        else:
            closest_entry = back
    
    else:
        closest_entry = gpx_df.iloc[gpx_index]

    if abs((closest_entry['time'] - search_timestamp).total_seconds()) > abs(window_length.total_seconds()):
        return closest_entry, False
    else:
        return closest_entry, True






    print(gpx_df.iloc[gpx_index - 1])
    print(gpx_df.iloc[gpx_index])




def to_deg(value, loc):
        if value < 0:
            loc_value = loc[0]
        elif value > 0:
            loc_value = loc[1]
        else:
            loc_value = ""
        abs_value = abs(value)
        deg =  int(abs_value)
        t1 = (abs_value-deg)*60
        min = int(t1)
        sec = (t1 - min)* 60
        return (deg, min, sec, loc_value)    

def set_gps_location(exiv_image, lat, lng):
    """Adds GPS position as EXIF metadata

    Keyword arguments:
    file_name -- image file 
    lat -- latitude (as float)
    lng -- longitude (as float)

    """
    lat_deg = to_deg(lat, ["S", "N"])
    lng_deg = to_deg(lng, ["W", "E"])

    print(lat_deg)
    print (lng_deg)

    # convert decimal coordinates into degrees, munutes and seconds
    exiv_lat = (
        Fraction(lat_deg[0], 1),
        Fraction(lat_deg[1], 1),
        Fraction(int(lat_deg[2] * 100), 100),
    )
    exiv_lng = (
        Fraction(lng_deg[0], 1),
        Fraction(lng_deg[1], 1),
        Fraction(int(lng_deg[2] * 100), 100),
    )

    exiv_image["Exif.GPSInfo.GPSLatitude"] = exiv_lat
    exiv_image["Exif.GPSInfo.GPSLatitudeRef"] = lat_deg[3]
    exiv_image["Exif.GPSInfo.GPSLongitude"] = exiv_lng
    exiv_image["Exif.GPSInfo.GPSLongitudeRef"] = lng_deg[3]
    exiv_image["Exif.Image.GPSTag"] = 654
    exiv_image["Exif.GPSInfo.GPSMapDatum"] = "WGS-84"
    exiv_image["Exif.GPSInfo.GPSVersionID"] = "2 0 0 0"
     

if __name__ == '__main__':

    try: 
        im_dir = sys.argv[1]
        gpx_dir = sys.argv[2]

        if len(sys.argv) > 3:
            window_length = pd.Timedelta(int(sys.argv[4]),'s')
        
        if len(sys.argv) == 5:
            time_offset = pd.Timedelta(int(sys.argv[3]),'s')
        
        main() 
    except: 
        print("invalid usage")
        print("expected usage:\n" +
              "> python3 geotagger.py [path to images directory] [path to gpx data directory]\n" + 
              "or\n" + 
              "> python3 geotagger.py [path to images directory] [path to gpx data directory] [integer window length in seconds for valid gpx entry]\n" + 
              "or\n" + 
              "> python3 geotagger.py [path to images directory] [path to gpx data directory] [integer window length in seconds for valid gpx entry]  [integer time offset in seconds]")
        