<script setup>
import { loadScript } from "vue-plugin-load-script";
import swiss_boundries from "@/assets/swiss_boundries";
import kanton_boundries from "@/assets/kanton_boundries";
import MapWrapper from "@/components/MapWrapper.vue";
import {computed} from "vue";

const props = defineProps({
  five_min: {
    type: Number,
    default: 0,
  },
  initial_view: {
    type: Object,
    default: () => {
      return {
        center: [46.791793, 8.095723],
        zoom: 8,
      };
    },
  },
});

const emit = defineEmits(['update:five_min']);

const five_minutes = computed({
  get() {
    return props.five_min;
  },
  set(value) {
    emit('update:five_min', value);
  },
});

let leaflet_map = null;

function get_map_view() {
  return {
    center: leaflet_map.getCenter(),
    zoom: leaflet_map.getZoom(),
  };
}

function set_map_view(view) {
  leaflet_map.setView(view.center, view.zoom);
  this.$forceUpdate();
}

defineExpose({
  get_map_view,
  set_map_view,
});

loadScript("https://unpkg.com/leaflet@1.4.0/dist/leaflet.js")
.then(() => {
  var map = L.map('rain')
  leaflet_map = map;

  map.setView(props.initial_view.center, props.initial_view.zoom);
  map.setMinZoom(8);
  map.setMaxZoom(11);
  map.setMaxBounds([[45.398181, 5.140242], [48.230651, 11.47757]]);

  // L.tileLayer('https://wmts.geo.admin.ch/1.0.0/ch.swisstopo.pixelkarte-grau/default/current/3857/{z}/{x}/{y}.jpeg', {
  //   attribution: '&copy; <a href="https://www.swisstopo.admin.ch/">swisstopo</a>',
  //   minZoom: 8,
  //   maxZoom: 11,
  //   bounds: [[45.398181, 5.140242], [48.230651, 11.47757]]
  // }).addTo(map);

  map.createPane('labels');
  map.getPane('labels').style.zIndex = 650;
  map.getPane('labels').style.pointerEvents = 'none';



  var hillshade = L.tileLayer('https://api.maptiler.com/tiles/hillshade/{z}/{x}/{y}.{ext}?key=vTloRxftNUtxWqKm2U6S', {
    pane: 'labels',
    ext: 'webp'
  });

  hillshade.addTo(map);

  var positronLabels = L.tileLayer('https://tiles.stadiamaps.com/tiles/stamen_terrain_labels/{z}/{x}/{y}{r}.{ext}', {
    pane: 'labels',
    ext: 'png'
  });

  positronLabels.addTo(map);

  function cloud_style(feature) {
    return {
      fillColor: feature.properties.color,
      weight: 0,
      fillOpacity: 1
    };
  }

  fetch('/api-v1/get-rain-data?' + new URLSearchParams({
    five_minutes: five_minutes.value,
  }), {
    method: 'GET'
  }).then((response) => {
    if (response.ok) {
      try {
        return response.json();
      } catch (e) {
        throw new Error('Something went wrong decoding the response');
      }
    } else {
      throw new Error('Something went wrong with the request');
    }
  }).then(data => {
    let clouds = L.geoJSON(data, {style: cloud_style});

    clouds.addTo(map);
  }).catch(error => {
    console.error(error);
  });
  L.geoJSON(swiss_boundries, {
    style: {
      color: '#000',
      weight: 2,
      fillOpacity: 0
    }
  }).addTo(map);

  L.geoJSON(kanton_boundries, {
    style: {
      color: '#000',
      weight: 1,
      fillOpacity: 0
    }
  }).addTo(map);
});
</script>

<template>
<MapWrapper v-model:five_min="five_minutes">
  <div id="rain"></div>
  <template #caption>
    &copy; <a href="https://www.stadiamaps.com/" target="_blank">Stadia Maps</a> &copy; <a href="https://www.stamen.com/" target="_blank">Stamen Design</a> &copy; <a href="https://openmaptiles.org/" target="_blank">OpenMapTiles</a> &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://www.maptiler.com/copyright/" target="_blank"> MapTiler</a> &copy; <a href="http://leafletjs.com" title="A JS library for interactive maps">Leaflet</a>
  </template>
</MapWrapper>
</template>

<style scoped>
#rain {
  background-color: #FFFFFF;
}
/* required styles */

:deep(.leaflet-pane),
:deep(.leaflet-tile),
:deep(.leaflet-marker-icon),
:deep(.leaflet-marker-shadow),
:deep(.leaflet-tile-container),
:deep .leaflet-pane > svg,
:deep .leaflet-pane > canvas,
:deep .leaflet-zoom-box,
:deep .leaflet-image-layer,
:deep .leaflet-layer {
  position: absolute;
  left: 0;
  top: 0;
}
:deep .leaflet-container {
  overflow: hidden;
}
:deep .leaflet-tile,
:deep .leaflet-marker-icon,
:deep .leaflet-marker-shadow {
  -webkit-user-select: none;
  -moz-user-select: none;
  user-select: none;
  -webkit-user-drag: none;
}
/* Safari renders non-retina tile on retina better with this, but Chrome is worse */
:deep .leaflet-safari .leaflet-tile {
  image-rendering: -webkit-optimize-contrast;
}
/* hack that prevents hw layers "stretching" when loading new tiles */
:deep .leaflet-safari .leaflet-tile-container {
  width: 1600px;
  height: 1600px;
  -webkit-transform-origin: 0 0;
}
:deep .leaflet-marker-icon,
:deep .leaflet-marker-shadow {
  display: block;
}
/* .leaflet-container svg: reset svg max-width decleration shipped in Joomla! (joomla.org) 3.x */
/* .leaflet-container img: map is broken in FF if you have max-width: 100% on tiles */
:deep .leaflet-container .leaflet-overlay-pane svg,
:deep .leaflet-container .leaflet-marker-pane img,
:deep .leaflet-container .leaflet-shadow-pane img,
:deep .leaflet-container .leaflet-tile-pane img,
:deep .leaflet-container img.leaflet-image-layer,
:deep .leaflet-container .leaflet-tile {
  max-width: none !important;
  max-height: none !important;
}

:deep .leaflet-container.leaflet-touch-zoom {
  -ms-touch-action: pan-x pan-y;
  touch-action: pan-x pan-y;
}
:deep .leaflet-container.leaflet-touch-drag {
  -ms-touch-action: pinch-zoom;
  /* Fallback for FF which doesn't support pinch-zoom */
  touch-action: none;
  touch-action: pinch-zoom;
}
:deep .leaflet-container.leaflet-touch-drag.leaflet-touch-zoom {
  -ms-touch-action: none;
  touch-action: none;
}
:deep .leaflet-container {
  -webkit-tap-highlight-color: transparent;
}
:deep .leaflet-container a {
  -webkit-tap-highlight-color: rgba(51, 181, 229, 0.4);
}
:deep .leaflet-tile {
  filter: inherit;
  visibility: hidden;
}
:deep .leaflet-tile-loaded {
  visibility: inherit;
}
:deep .leaflet-zoom-box {
  width: 0;
  height: 0;
  -moz-box-sizing: border-box;
  box-sizing: border-box;
  z-index: 800;
}
/* workaround for https://bugzilla.mozilla.org/show_bug.cgi?id=888319 */
:deep .leaflet-overlay-pane svg {
  -moz-user-select: none;
}

:deep .leaflet-pane         { z-index: 400; }

:deep .leaflet-tile-pane    { z-index: 200; }
:deep .leaflet-overlay-pane { z-index: 400; }
:deep .leaflet-shadow-pane  { z-index: 500; }
:deep .leaflet-marker-pane  { z-index: 600; }
:deep .leaflet-tooltip-pane   { z-index: 650; }
:deep .leaflet-popup-pane   { z-index: 700; }

:deep .leaflet-map-pane canvas { z-index: 100; }
:deep .leaflet-map-pane svg    { z-index: 200; }

:deep .leaflet-vml-shape {
  width: 1px;
  height: 1px;
}
:deep .lvml {
  behavior: url(#default#VML);
  display: inline-block;
  position: absolute;
}


/* control positioning */

:deep .leaflet-control {
  position: relative;
  z-index: 800;
  pointer-events: visiblePainted; /* IE 9-10 doesn't have auto */
  pointer-events: auto;
}
:deep .leaflet-top,
:deep .leaflet-bottom {
  position: absolute;
  z-index: 1000;
  pointer-events: none;
}
:deep .leaflet-top {
  top: 0;
}
:deep .leaflet-right {
  right: 0;
}
:deep .leaflet-bottom {
  bottom: 0;
}
:deep .leaflet-left {
  left: 0;
}
:deep .leaflet-control {
  float: left;
  clear: both;
}
:deep .leaflet-right .leaflet-control {
  float: right;
}
:deep .leaflet-top .leaflet-control {
  margin-top: 10px;
}
:deep .leaflet-bottom .leaflet-control {
  margin-bottom: 10px;
}
:deep .leaflet-left .leaflet-control {
  margin-left: 10px;
}
:deep .leaflet-right .leaflet-control {
  margin-right: 10px;
}


/* zoom and fade animations */

:deep .leaflet-fade-anim .leaflet-tile {
  will-change: opacity;
}
:deep .leaflet-fade-anim .leaflet-popup {
  opacity: 0;
  -webkit-transition: opacity 0.2s linear;
  -moz-transition: opacity 0.2s linear;
  transition: opacity 0.2s linear;
}
:deep .leaflet-fade-anim .leaflet-map-pane .leaflet-popup {
  opacity: 1;
}
:deep .leaflet-zoom-animated {
  -webkit-transform-origin: 0 0;
  -ms-transform-origin: 0 0;
  transform-origin: 0 0;
}
:deep .leaflet-zoom-anim .leaflet-zoom-animated {
  will-change: transform;
}
:deep .leaflet-zoom-anim .leaflet-zoom-animated {
  -webkit-transition: -webkit-transform 0.25s cubic-bezier(0,0,0.25,1);
  -moz-transition:    -moz-transform 0.25s cubic-bezier(0,0,0.25,1);
  transition:         transform 0.25s cubic-bezier(0,0,0.25,1);
}
:deep .leaflet-zoom-anim .leaflet-tile,
:deep .leaflet-pan-anim .leaflet-tile {
  -webkit-transition: none;
  -moz-transition: none;
  transition: none;
}

:deep .leaflet-zoom-anim .leaflet-zoom-hide {
  visibility: hidden;
}


/* cursors */

:deep .leaflet-interactive {
  cursor: pointer;
}
:deep .leaflet-grab {
  cursor: -webkit-grab;
  cursor:    -moz-grab;
  cursor:         grab;
}
:deep .leaflet-crosshair,
:deep .leaflet-crosshair .leaflet-interactive {
  cursor: crosshair;
}
:deep .leaflet-popup-pane,
:deep .leaflet-control {
  cursor: auto;
}
:deep .leaflet-dragging .leaflet-grab,
:deep .leaflet-dragging .leaflet-grab .leaflet-interactive,
:deep .leaflet-dragging .leaflet-marker-draggable {
  cursor: move;
  cursor: -webkit-grabbing;
  cursor:    -moz-grabbing;
  cursor:         grabbing;
}

/* marker & overlays interactivity */
:deep .leaflet-marker-icon,
:deep .leaflet-marker-shadow,
:deep .leaflet-image-layer,
:deep .leaflet-pane > svg path,
:deep .leaflet-tile-container {
  pointer-events: none;
}

:deep .leaflet-marker-icon.leaflet-interactive,
:deep .leaflet-image-layer.leaflet-interactive,
:deep .leaflet-pane > svg path.leaflet-interactive {
  pointer-events: visiblePainted; /* IE 9-10 doesn't have auto */
  pointer-events: auto;
}

/* visual tweaks */

:deep .leaflet-container {
  background: #ddd;
  outline: 0;
}
:deep .leaflet-container a {
  color: #0078A8;
}
:deep .leaflet-container a.leaflet-active {
  outline: 2px solid orange;
}
:deep .leaflet-zoom-box {
  border: 2px dotted #38f;
  background: rgba(255,255,255,0.5);
}


/* general typography */
:deep .leaflet-container {
  font: 12px/1.5 "Helvetica Neue", Arial, Helvetica, sans-serif;
}


/* general toolbar styles */

:deep .leaflet-bar {
  box-shadow: 0 1px 5px rgba(0,0,0,0.65);
  border-radius: 4px;
}
:deep .leaflet-bar a,
:deep .leaflet-bar a:hover {
  background-color: #fff;
  border-bottom: 1px solid #ccc;
  width: 26px;
  height: 26px;
  line-height: 26px;
  display: block;
  text-align: center;
  text-decoration: none;
  color: black;
}
:deep .leaflet-bar a,
:deep .leaflet-control-layers-toggle {
  background-position: 50% 50%;
  background-repeat: no-repeat;
  display: block;
}
:deep .leaflet-bar a:hover {
  background-color: #f4f4f4;
}
:deep .leaflet-bar a:first-child {
  border-top-left-radius: 4px;
  border-top-right-radius: 4px;
}
:deep .leaflet-bar a:last-child {
  border-bottom-left-radius: 4px;
  border-bottom-right-radius: 4px;
  border-bottom: none;
}
:deep .leaflet-bar a.leaflet-disabled {
  cursor: default;
  background-color: #f4f4f4;
  color: #bbb;
}

:deep .leaflet-touch .leaflet-bar a {
  width: 30px;
  height: 30px;
  line-height: 30px;
}
:deep .leaflet-touch .leaflet-bar a:first-child {
  border-top-left-radius: 2px;
  border-top-right-radius: 2px;
}
:deep .leaflet-touch .leaflet-bar a:last-child {
  border-bottom-left-radius: 2px;
  border-bottom-right-radius: 2px;
}

/* zoom control */

:deep .leaflet-control-zoom-in,
:deep .leaflet-control-zoom-out {
  font: bold 18px 'Lucida Console', Monaco, monospace;
  text-indent: 1px;
}

:deep .leaflet-touch .leaflet-control-zoom-in, :deep .leaflet-touch .leaflet-control-zoom-out  {
  font-size: 22px;
}


/* layers control */

:deep .leaflet-control-layers {
  box-shadow: 0 1px 5px rgba(0,0,0,0.4);
  background: #fff;
  border-radius: 5px;
}
:deep .leaflet-control-layers-toggle {
  background-image: url(https://unpkg.com/leaflet@1.4.0/dist/images/layers.png);
  width: 36px;
  height: 36px;
}
:deep .leaflet-retina .leaflet-control-layers-toggle {
  background-image: url(https://unpkg.com/leaflet@1.4.0/dist/images/layers-2x.png);
  background-size: 26px 26px;
}
:deep .leaflet-touch .leaflet-control-layers-toggle {
  width: 44px;
  height: 44px;
}
:deep .leaflet-control-layers .leaflet-control-layers-list,
:deep .leaflet-control-layers-expanded .leaflet-control-layers-toggle {
  display: none;
}
:deep .leaflet-control-layers-expanded .leaflet-control-layers-list {
  display: block;
  position: relative;
}
:deep .leaflet-control-layers-expanded {
  padding: 6px 10px 6px 6px;
  color: #333;
  background: #fff;
}
:deep .leaflet-control-layers-scrollbar {
  overflow-y: scroll;
  overflow-x: hidden;
  padding-right: 5px;
}
:deep .leaflet-control-layers-selector {
  margin-top: 2px;
  position: relative;
  top: 1px;
}
:deep .leaflet-control-layers label {
  display: block;
}
:deep .leaflet-control-layers-separator {
  height: 0;
  border-top: 1px solid #ddd;
  margin: 5px -10px 5px -6px;
}

/* Default icon URLs */
:deep .leaflet-default-icon-path {
  background-image: url(https://unpkg.com/leaflet@1.4.0/dist/images/marker-icon.png);
}


/* attribution and scale controls */

:deep .leaflet-container .leaflet-control-attribution {
  display: none;
}

:deep .leaflet-control-scale-line {
  padding: 0 5px;
  color: #333;
}

:deep .leaflet-container .leaflet-control-scale {
  font-size: 11px;
}
:deep .leaflet-left .leaflet-control-scale {
  margin-left: 5px;
}
:deep .leaflet-bottom .leaflet-control-scale {
  margin-bottom: 5px;
}
:deep .leaflet-control-scale-line {
  border: 2px solid #777;
  border-top: none;
  line-height: 1.1;
  padding: 2px 5px 1px;
  font-size: 11px;
  white-space: nowrap;
  overflow: hidden;
  -moz-box-sizing: border-box;
  box-sizing: border-box;

  background: #fff;
  background: rgba(255, 255, 255, 0.5);
}
:deep .leaflet-control-scale-line:not(:first-child) {
  border-top: 2px solid #777;
  border-bottom: none;
  margin-top: -2px;
}
:deep .leaflet-control-scale-line:not(:first-child):not(:last-child) {
  border-bottom: 2px solid #777;
}

:deep .leaflet-touch .leaflet-control-attribution,
:deep .leaflet-touch .leaflet-control-layers,
:deep .leaflet-touch .leaflet-bar {
  box-shadow: none;
}
:deep .leaflet-touch .leaflet-control-layers,
:deep .leaflet-touch .leaflet-bar {
  border: 2px solid rgba(0,0,0,0.2);
  background-clip: padding-box;
}


/* popup */

:deep .leaflet-popup {
  position: absolute;
  text-align: center;
  margin-bottom: 20px;
}
:deep .leaflet-popup-content-wrapper {
  padding: 1px;
  text-align: left;
  border-radius: 12px;
}
:deep .leaflet-popup-content {
  margin: 13px 19px;
  line-height: 1.4;
}
:deep .leaflet-popup-content p {
  margin: 18px 0;
}
:deep .leaflet-popup-tip-container {
  width: 40px;
  height: 20px;
  position: absolute;
  left: 50%;
  margin-left: -20px;
  overflow: hidden;
  pointer-events: none;
}
:deep .leaflet-popup-tip {
  width: 17px;
  height: 17px;
  padding: 1px;

  margin: -10px auto 0;

  -webkit-transform: rotate(45deg);
  -moz-transform: rotate(45deg);
  -ms-transform: rotate(45deg);
  transform: rotate(45deg);
}
:deep .leaflet-popup-content-wrapper,
:deep .leaflet-popup-tip {
  background: white;
  color: #333;
  box-shadow: 0 3px 14px rgba(0,0,0,0.4);
}
:deep .leaflet-container a.leaflet-popup-close-button {
  position: absolute;
  top: 0;
  right: 0;
  padding: 4px 4px 0 0;
  border: none;
  text-align: center;
  width: 18px;
  height: 14px;
  font: 16px/14px Tahoma, Verdana, sans-serif;
  color: #c3c3c3;
  text-decoration: none;
  font-weight: bold;
  background: transparent;
}
:deep .leaflet-container a.leaflet-popup-close-button:hover {
  color: #999;
}
:deep .leaflet-popup-scrolled {
  overflow: auto;
  border-bottom: 1px solid #ddd;
  border-top: 1px solid #ddd;
}

:deep .leaflet-oldie .leaflet-popup-content-wrapper {
  zoom: 1;
}
:deep .leaflet-oldie .leaflet-popup-tip {
  width: 24px;
  margin: 0 auto;

  -ms-filter: "progid:DXImageTransform.Microsoft.Matrix(M11=0.70710678, M12=0.70710678, M21=-0.70710678, M22=0.70710678)";
  filter: progid:DXImageTransform.Microsoft.Matrix(M11=0.70710678, M12=0.70710678, M21=-0.70710678, M22=0.70710678);
}
:deep .leaflet-oldie .leaflet-popup-tip-container {
  margin-top: -1px;
}

:deep .leaflet-oldie .leaflet-control-zoom,
:deep .leaflet-oldie .leaflet-control-layers,
:deep .leaflet-oldie .leaflet-popup-content-wrapper,
:deep .leaflet-oldie .leaflet-popup-tip {
  border: 1px solid #999;
}


/* div icon */

:deep .leaflet-div-icon {
  background: #fff;
  border: 1px solid #666;
}


/* Tooltip */
/* Base styles for the element that has a tooltip */
:deep .leaflet-tooltip {
  position: absolute;
  padding: 6px;
  background-color: #fff;
  border: 1px solid #fff;
  border-radius: 3px;
  color: #222;
  white-space: nowrap;
  -webkit-user-select: none;
  -moz-user-select: none;
  -ms-user-select: none;
  user-select: none;
  pointer-events: none;
  box-shadow: 0 1px 3px rgba(0,0,0,0.4);
}
:deep .leaflet-tooltip.leaflet-clickable {
  cursor: pointer;
  pointer-events: auto;
}
:deep .leaflet-tooltip-top:before,
:deep .leaflet-tooltip-bottom:before,
:deep .leaflet-tooltip-left:before,
:deep .leaflet-tooltip-right:before {
  position: absolute;
  pointer-events: none;
  border: 6px solid transparent;
  background: transparent;
  content: "";
}

/* Directions */

:deep .leaflet-tooltip-bottom {
  margin-top: 6px;
}
:deep .leaflet-tooltip-top {
  margin-top: -6px;
}
:deep .leaflet-tooltip-bottom:before,
:deep .leaflet-tooltip-top:before {
  left: 50%;
  margin-left: -6px;
}
:deep .leaflet-tooltip-top:before {
  bottom: 0;
  margin-bottom: -12px;
  border-top-color: #fff;
}
:deep .leaflet-tooltip-bottom:before {
  top: 0;
  margin-top: -12px;
  margin-left: -6px;
  border-bottom-color: #fff;
}
:deep .leaflet-tooltip-left {
  margin-left: -6px;
}
:deep .leaflet-tooltip-right {
  margin-left: 6px;
}
:deep .leaflet-tooltip-left:before,
:deep .leaflet-tooltip-right:before {
  top: 50%;
  margin-top: -6px;
}
:deep .leaflet-tooltip-left:before {
  right: 0;
  margin-right: -12px;
  border-left-color: #fff;
}
:deep .leaflet-tooltip-right:before {
  left: 0;
  margin-left: -12px;
  border-right-color: #fff;
}
</style>
