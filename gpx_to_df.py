import pandas as pd
from lxml import etree

def gpx_to_df(path):
    tree = etree.parse(path)
    # Define the GPX 1.0 namespace
    ns = {"g": "http://www.topografix.com/GPX/1/0"}

    # Find the first <trkseg>
    trkseg = tree.find(".//g:trkseg", namespaces=ns)

    records = []
    for trkpt in trkseg.findall("g:trkpt", namespaces=ns):
        rec = { 
            "lat": trkpt.get("lat"),
            "lon": trkpt.get("lon"),
            "ele": trkpt.findtext("g:ele", namespaces=ns),
            "time": trkpt.findtext("g:time", namespaces=ns),
            "src": trkpt.findtext("g:src", namespaces=ns),
        }
        records.append(rec)

    df = pd.DataFrame(records)

    df["time"] = pd.to_datetime(df["time"], utc=True)

    return df