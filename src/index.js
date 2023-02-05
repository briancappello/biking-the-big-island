import "./main.css";
import "leaflet/dist/leaflet.css";

import L from "leaflet";
import "leaflet-gpx";

import data from "./data.js";
import images from "./images.js";

window.STATE = {
  dayIndex: 1,
  track: undefined,
  markers: [],
};
let S = window.STATE;

S.map = L.map("map").setView([19.7, -155.5], 7);

L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
  maxZoom: 19,
  attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
}).addTo(S.map);

const clearMap = () => {
  if (S.track) {
    S.track.remove();
    S.track = undefined;
  }
  S.markers.forEach(marker => marker.remove());
  S.markers = [];
}

const defaultZoom = () => {
  clearMap();
  S.map.flyTo([19.7, -155.5], 9);
};
defaultZoom();

const drawGPXTrack = (gpxFilename) => {
  return new L.GPX(`gpx-tracks/${gpxFilename}`, {
    async: true,
    gpx_options: {
      parseElements: ["track"],
    },
  })
    .on("loaded", (e) => {
      S.map.flyToBounds(e.target.getBounds());
    })
    .addTo(S.map);
}

const drawImageMarkers = (date) => {
  images[date].forEach(image => {
    const marker = L.marker([image.lat, image.lon]).addTo(S.map);
    const caption = image.caption ? `<p>${image.caption}</p>` : '';
    marker.bindPopup(`
      <div style="height: 400px; width: 400px;">
        <img src="processed-images/${image.filename}" />
      </div>
        ${caption}
    `);
    S.markers.push(marker);
  });
}

const onPrevDay = () => {
  let dayIndex = S.dayIndex -= 1;
  if (dayIndex <= 0) {
    S.dayIndex = dayIndex = 0;
    defaultZoom();
  }
  render(data.days[dayIndex])
}

const onNextDay = () => {
  let dayIndex = S.dayIndex += 1;
  if (dayIndex === (data.days.length - 1)) {
    defaultZoom();
  } else if (dayIndex > (data.days.length - 1)) {
    S.dayIndex = dayIndex = 0;
    defaultZoom();
  }
  render(data.days[dayIndex])
}

const render = (day) => {
  document.getElementsByTagName('title')[0].text = `${data.title} > ${day.title}`;

  const root = document.getElementById('sidebar');
  root.innerHTML = '';

  appendElement(root, 'h1', day.title)
  if (!day.date) {
    appendElement(root, 'div', day.content)
  } else {
    clearMap();
    S.track = drawGPXTrack(day.gpxFilename);
    drawImageMarkers(day.date);
    // render day metrics
  }

  const prevButton = appendElement(root, 'button', '< Previous');
  prevButton.addEventListener('click', onPrevDay)
  const nextButton = appendElement(root, 'button', 'Next >');
  nextButton.addEventListener('click', onNextDay)
}

const appendElement = (root, el, text) => {
  const newElement = document.createElement(el);
  newElement.innerHTML = text;
  root.appendChild(newElement);
  return newElement;
}

render(data.days[S.dayIndex])
