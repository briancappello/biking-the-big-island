import json
import os
import re
import shutil

from py.gpx import gpx_tracks_to_df, list_image_timestamps, load_gpx, plot_segment


img_dir = "public/images"
gpx_dir = "public/gpx-tracks"


def name_images_by_gps_coords():
    images = list_image_timestamps(img_dir)
    gpx_df = gpx_tracks_to_df(gpx_dir)

    nearest_ts_indexes = gpx_df.index.get_indexer([img.ts for img in images], method="nearest")
    images_df = gpx_df.iloc[nearest_ts_indexes].copy()
    images_df["filename"] = [image.name for image in images]

    for ts, row in images_df.iterrows():
        new_filename = f"({row.lat:.10})[{row.lon:10}]"
        suffix = 0
        while True:
            new_path = f"/public/processed-images/{new_filename}_{suffix}.jpg"
            if not os.path.exists(new_path):
                break
            suffix += 1
        shutil.copy2(f"{img_dir}/{row.filename}", new_path)


def group_images_by_day():
    d = {}
    images = list_image_timestamps('/public/processed-images')
    dt = None
    for img in images:
        d.setdefault(img.ts.date().isoformat(), []).append(dict(
            filename=img.name,
            lat=img.name[1:img.name.find(')')],
            lon=img.name[img.name.find('[')+1:img.name.find(']')],
            ts=img.ts.isoformat(),
        ))

    with open('/src/images.js', 'w') as f:
        json.dump(d, f, indent=2)

if __name__ == "__main__":
    group_images_by_day()
