# Adventure Log

A travel log and interactive map for multi-day long distance adventures.

## Quickstart

```bash
git clone git@github.com:briancappello/biking-the-big-islang.git
npm install
npm run start
```

## Project Layout

### Sources

* `src/index.js`: Main entry point. Renders the content of `src/data.js`.
* `src/main.css`

### src/data.js

A JS object representing a multi-day trip.

```javascript
export const data = {
  title: "content for <title> tag",
  days: [
    // overview "day 0"
    {
      title: "Introduction",
      content: `<p>Hello World!</p>`,
    },
    
    // any number of dated days
    {
      date: "2023-01-01",  // isoformat
      title: "Day One!",
      miles: 3.14,
      ascent: 1000,  // feet
      descent: 1000, // feet
      gpxFilename: "a filename inside the public/gpx-tracks folder.gpx",
    },
    
    // trip summary
    {
      title: "Conclusion",
      content: `<p>Excellent adventure!</p>`,
    },
  ],
}
```

### src/images.js

A JS object of pictures taken on the trip.

```javascript
export const images = {
  // keyed by isoformat date, value is list of objects
  "2023-01-01": [
    {
      filename: "a filename inside the public/images folder.png",
      lat: "latitude as a float",
      lon: "longitude as a float",
      ts: "isoformat timestamp",
      caption: "an optional caption for the picture",
    },
  ],
}
```

## Development Tools

[leaflet](https://leafletjs.com/) was chosen as the mapping tool.

[esbuild](https://esbuild.github.io/) was chosen as the bundler, mostly just to experiment with it. However, its documentation is a little lacking, especially with how it handles static assets (especially images and stylesheets from 3rd-party node modules)

There are no UI frameworks, either for JS or styling. No good.

## Future Improvements

* Switch to React (or similar), probably drop `esbuild` in favor of [create-react-app](https://create-react-app.dev/)
  * Maybe as a SPA?

* Add a backend server:
  * Support multiple trips
  * Serve trip data and images over REST API
  * Support multiple users
    * Authentication and Admin interface for their account / trips
