<script setup>
import MapWrapper from "@/components/MapWrapper.vue";

const WindyToken = 'zqPWHzq2Rai9frfxQp6gczIGDkYk6VzS';
import {ref, onMounted, watch} from 'vue';
import { loadScript } from "vue-plugin-load-script";

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

let current_time = Date.now();

let windy_store = null;
let windy_map = null;

function get_map_view() {
  return {
    center: windy_map.getCenter(),
    zoom: windy_map.getZoom(),
  };
}

function set_map_view(view) {
  windy_map.setView(view.center, view.zoom);
}

defineExpose({
  get_map_view,
  set_map_view,
});

watch(() => props.five_min, (val) => {
  current_time = Date.now() + val * 5 * 60 * 1000;
  windy_store.set('timestamp', current_time);
});

loadScript("https://unpkg.com/leaflet@1.4.0/dist/leaflet.js")
.then(() => {
  loadScript("https://api.windy.com/assets/map-forecast/libBoot.js")
  .then(() => {
    const options = {
      // Required: API key
      key: WindyToken,

      // Put additional console output
      verbose: false,

      // Optional: Initial state of the map
      lat: props.initial_view.center[0],
      lon: props.initial_view.center[1],
      zoom: props.initial_view.zoom,

      timestamp: current_time.value,
    };

    // Initialize Windy API
    windyInit(options, windyAPI => {
      // windyAPI is ready, and contain 'map', 'store',
      // 'picker' and other usefull stuff

      const { map, picker, utils, broadcast, store } = windyAPI;
      windy_store = store;
      windy_map = map;
      // .map is instance of Leaflet map

      map.setMinZoom(8);
      map.setMaxZoom(11);
      map.setMaxBounds([[45.398181, 5.140242], [48.230651, 11.47757]]);

      picker.on('pickerOpened', ({ lat, lon, values, overlay }) => {
        // -> 48.4, 14.3, [ U,V, ], 'wind'
        console.log('opened', lat, lon, values, overlay);

        const windObject = utils.wind2obj(values);
        console.log(windObject);
      });

      picker.on('pickerMoved', ({ lat, lon, values, overlay }) => {
        // picker was dragged by user to latLon coords
        console.log('moved', lat, lon, values, overlay);
      });

      picker.on('pickerClosed', () => {
        // picker was closed
      });

      store.on('pickerLocation', ({ lat, lon }) => {
        console.log(lat, lon);

        const { values, overlay } = picker.getParams();
        console.log('location changed', lat, lon, values, overlay);
      });

      // Wait since wather is rendered
      broadcast.once('redrawFinished', () => {
        // Opening of a picker (async)
        picker.open({ lat: 46.791793, lon: 8.095723 });
      });
    });
  })
})
</script>

<template>
<MapWrapper :five_min="props.five_min">
  <div id="windy"></div>
  <template #caption>
    Note that windy only updates it's map every hour.
  </template>
</MapWrapper>
</template>

<style scoped>

</style>

<style>
#windy #logo-wrapper #logo {
  left: 80px;
}

#windy #progress-bar {
  display: none !important;
}

#windy #mobile-ovr-select {
  display: none !important;
}

#windy #embed-zoom {
  top: 0 !important;
}
</style>
