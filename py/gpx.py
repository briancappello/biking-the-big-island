import json
import os
import pathlib

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional
from urllib.parse import urlencode
from zoneinfo import ZoneInfo

import exif
import gpxpy
import matplotlib.pyplot as plt
import pandas as pd
import requests

from geographiclib.geodesic import Geodesic

from .config import ARC_GIS_API_KEY


@dataclass
class Image:
    name: str
    ts: datetime
    lat: Optional[float] = None
    lon: Optional[float] = None


def list_image_timestamps(
    directory: str,
    ext: str = ".jpg",
    tz: ZoneInfo = ZoneInfo("US/Hawaii"),
) -> List[Image]:
    rv = []
    path = pathlib.Path(directory)
    for filename in os.listdir(path):
        filename = str(filename)
        if not filename.lower().endswith(ext.lower()):
            continue
        with open(path / filename, "rb") as f:
            img = exif.Image(f)

        rv.append(
            Image(
                name=filename,
                ts=datetime(
                    *[int(x) for x in img.datetime_original.replace(" ", ":").split(":")],
                    tzinfo=tz,
                ),
            )
        )
    return rv


def gpx_segment_to_df(seg):
    return pd.DataFrame.from_records(
        [
            dict(
                ts=point.time.replace(tzinfo=ZoneInfo("UTC")),
                lat=point.latitude,
                lon=point.longitude,
            )
            for point in seg.points
        ],
        index="ts",
    )


def gpx_tracks_to_df(directory: str, ext: str = ".gpx") -> pd.DataFrame:
    path = pathlib.Path(directory)
    df_segs = []
    for filename in os.listdir(path):
        filename: str
        if not filename.lower().endswith(ext.lower()):
            continue

        for track in load_gpx(path / filename).tracks:
            for seg in track.segments:
                df_segs.append(gpx_segment_to_df(seg))

    df = pd.concat(df_segs)
    return df.sort_index()


def load_gpx(filepath):
    with open(filepath) as f:
        return gpxpy.parse(f)


def lat_lon_dist(point0, point1):
    """
    Returns the distance between two points in meters
    """
    if isinstance(point0, (list, tuple)):
        lat0, lon0 = point0[0], point0[1]
        lat1, lon1 = point1[0], point1[1]
    else:
        lat0, lon0 = point0.latitude, point0.longitude
        lat1, lon1 = point1.latitude, point1.longitude
    return Geodesic.WGS84.Inverse(lat0, lon0, lat1, lon1)["s12"]  # meters


def dist_speed_elevation(p0, p1):
    dist_m = lat_lon_dist(p0, p1)
    speed_m_per_s = dist_m / (p1.time - p0.time).total_seconds()
    elevation = p1.elevation - p0.elevation
    return dist_m, speed_m_per_s, elevation


def meters_to_feet(dist_m):
    return dist_m * 3.28084


def feet_to_miles(dist_ft):
    return dist_ft / 5280


def meters_to_miles(m):
    return feet_to_miles(meters_to_feet(m))


def meters_per_sec_to_miles_per_hour(mps):
    return mps * 2.236936


def analyze_segment(seg, metric=True):
    distances = [0]
    speeds = [0]
    elevations = [seg.points[0].elevation]

    for i in range(0, len(seg.points) - 1):
        p0 = seg.points[i]
        p1 = seg.points[i + 1]
        d, s, e = dist_speed_elevation(p0, p1)
        distances.append(distances[-1] + d)
        speeds.append(s)
        elevations.append(elevations[-1] + e)

    if not metric:
        distances = [meters_to_miles(x) for x in distances]
        speeds = [meters_per_sec_to_miles_per_hour(x) for x in speeds]
        elevations = [meters_to_feet(x) for x in elevations]

    return distances, speeds, elevations


def plot_segment(seg, metric=True):
    distances, speeds, elevations = analyze_segment(seg, metric=metric)

    fig, (ax0, ax1) = plt.subplots(2, 1)

    dist_l, speed_l, el_l = "m", "m/s", "m"
    if not metric:
        dist_l, speed_l, el_l = "miles", "mph", "ft"

    ax0.plot(distances, speeds)
    ax0.set_xlabel(f"Distance ({dist_l})")
    ax0.set_ylabel(f"Speed ({speed_l})")
    ax0.grid(True)

    ax1.plot(distances, elevations)
    ax1.set_xlabel(f"Distance ({dist_l})")
    ax1.set_ylabel(f"Elevation ({el_l})")
    ax1.grid(True)

    plt.show()


def reverse_geocode(lat, lon):
    # https://developers.arcgis.com/rest/geocode/api-reference/geocoding-reverse-geocode.htm

    reverse_geocode_url = (
        "https://geocode.arcgis.com/arcgis/rest/services/World/GeocodeServer/reverseGeocode"
    )

    query = dict(
        token=ARC_GIS_API_KEY,
        f="json",
        location=json.dumps(dict(x=lon, y=lat)),
        featureTypes=",".join(
            [
                "StreetAddress",
                "POI",
            ]
        ),
    )
    return requests.get(f"{reverse_geocode_url}?{urlencode(query)}").json()
