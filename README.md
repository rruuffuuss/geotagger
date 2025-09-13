# Geotagger

### <p style="font-size:20px">Geotag JPEG files with GPS Exchange Format tracks</p>

Latitude and Longitude Exif metadata tags are set to the position of the GPX track point recorded closest to the time the image was taken

## Usage

```bash
python3 geotagger.py [path to images directory] [path to gpx data directory] 
```
or
```bash
python3 geotagger.py [path to images directory] [path to gpx data directory] [window length in seconds]
```
or

```bash
python3 geotagger.py [path to images directory] [path to gpx data directory] [window length in seconds] [time offset in seconds]
```

## Arguments

| Argument | Description |
| -------- | ----------- |
| **```[path to images directory]```** | Path to the folder containing images (JPEG) to be geotagged. |
| **```[path to gpx data directory]```** | Path to the folder containing GPX files with recorded GPS track data. |
| **```[window length in seconds] (optional)```** | Integer value specifying the allowed time window (in seconds) when matching an image timestamp to the closest GPX entry. Defaults to 1800 (30 minutes). |
| **```[time offset in seconds] (optional)```** | Integer value (positive or negative) applied to adjust image timestamps before matching (useful if camera clock differs from GPS time). Defaults to 0. |

## Examples

```bash
# tag images with GPX data
python3 geotagger.py ./photos ./gpx

# 5 minutes tolerance for GPX matching
python3 geotagger.py ./photos ./gpx 300

# Apply a -120 second offset to images, with a 2 minute matching window
python3 geotagger.py ./photos ./gpx 120 -7200
```