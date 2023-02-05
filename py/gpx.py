import json
import os

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Union
from urllib.parse import urlencode
from zoneinfo import ZoneInfo

import exif
import gpxpy
import matplotlib.pyplot as plt
import pandas as pd
import requests

from geographiclib.geodesic import Geodesic
from gpxpy.gpx import GPXTrack, GPXTrackSegment, GPXTrackPoint, GPX

from .config import ARC_GIS_API_KEY

PathLike = Union[Path, str]


@dataclass
class Image:
    name: str
    ts: datetime
    lat: Optional[float] = None
    lon: Optional[float] = None

    def __str__(self):
        return self.name


def list_image_timestamps(
    directory: PathLike,
    ext: str = ".jpg",
    tz: ZoneInfo = ZoneInfo("US/Hawaii"),
) -> List[Image]:
    rv = []
    path = Path(directory)
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
    return sorted(rv, key=lambda img: img.ts)


def gpx_segment_to_df(seg: GPXTrackSegment):
    return pd.DataFrame.from_records(
        [
            dict(
                ts=point.time.replace(tzinfo=ZoneInfo("UTC")),
                lat=point.latitude,
                lon=point.longitude,
                elevation=point.elevation,
            )
            for point in seg.points
        ],
        index="ts",
    )


def gpx_track_to_df(track: GPXTrack):
    df_segs = []
    for seg in track.segments:
        df_segs.append(gpx_segment_to_df(seg))

    return pd.concat(df_segs).sort_index()


def gpx_tracks_to_df(directory: PathLike, ext: str = ".gpx") -> pd.DataFrame:
    path = Path(directory)
    df_segs = []
    for filename in os.listdir(path):
        filename: str
        if not filename.lower().endswith(ext.lower()):
            continue

        for track in load_gpx(path / filename).tracks:
            df_segs.append(gpx_track_to_df(track))

    df = pd.concat(df_segs)
    return df.sort_index()


def load_gpx(filepath: PathLike) -> GPX:
    with open(filepath) as f:
        return gpxpy.parse(f)


def lat_lon_dist(point0: GPXTrackPoint, point1: GPXTrackPoint):
    """
    Returns the distance between two points in meters
    """
    lat0, lon0 = point0.latitude, point0.longitude
    lat1, lon1 = point1.latitude, point1.longitude
    return Geodesic.WGS84.Inverse(lat0, lon0, lat1, lon1)["s12"]  # meters


def dist_speed_elevation(p0: GPXTrackPoint, p1: GPXTrackPoint):
    dist_m = lat_lon_dist(p0, p1)
    speed_m_per_s = dist_m / (p1.time - p0.time).total_seconds()
    elevation_m = p1.elevation - p0.elevation
    return dist_m, speed_m_per_s, elevation_m


def meters_to_feet(dist_m):
    return dist_m * 3.28084


def feet_to_miles(dist_ft):
    return dist_ft / 5280


def meters_to_miles(m):
    return feet_to_miles(meters_to_feet(m))


def meters_per_sec_to_miles_per_hour(mps):
    return mps * 2.236936


def analyze_segment(seg: GPXTrackSegment, metric: bool = False):
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


def plot_segment(seg: GPXTrackSegment, metric: bool = False):
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


def gpx_stats():
    pass


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
