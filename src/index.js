import "./main.css"
import "leaflet/dist/leaflet.css"

import L from "leaflet";

let map = L.map('map').setView([19.7, -155.5], 9);

L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
}).addTo(map);
