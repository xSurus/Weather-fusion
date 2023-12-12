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
});

let current_time = Date.now();

let windy_store = null;

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
      lat: 46.791793,
      lon: 8.095723,
      zoom: 8,

      timestamp: current_time.value,
    };

    // Initialize Windy API
    windyInit(options, windyAPI => {
      // windyAPI is ready, and contain 'map', 'store',
      // 'picker' and other usefull stuff

      const { map, store } = windyAPI;
      windy_store = store;
      // .map is instance of Leaflet map

      map.setMinZoom(8);
      map.setMaxZoom(11);
      map.setMaxBounds([[45.398181, 5.140242], [48.230651, 11.47757]]);

      // Print Zoom level when user triggers zoom change
      map.on("zoom", () => {
        console.log(`Zoom level: ${map.getZoom()}`);
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
