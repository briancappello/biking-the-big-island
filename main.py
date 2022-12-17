from py.gpx import gpx_tracks_to_df, list_image_timestamps

if __name__ == "__main__":
    img_dir = "public/static/images"
    gpx_dir = "public/static/gpx-tracks"

    images = list_image_timestamps(img_dir)
    gpx_df = gpx_tracks_to_df(gpx_dir)

    nearest_ts_indexes = gpx_df.index.get_indexer([img.ts for img in images], method="nearest")
    images_df = gpx_df.iloc[nearest_ts_indexes].copy()
    images_df["filename"] = [image.name for image in images]

    print(images_df)
