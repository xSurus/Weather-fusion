<script setup>
const WindyToken = 'zqPWHzq2Rai9frfxQp6gczIGDkYk6VzS';
import {ref, onMounted} from 'vue';
import { loadScript } from "vue-plugin-load-script";

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
        };

        // Initialize Windy API
        windyInit(options, windyAPI => {
          // windyAPI is ready, and contain 'map', 'store',
          // 'picker' and other usefull stuff

          const { map } = windyAPI;
          // .map is instance of Leaflet map

          // Print Zoom level when user triggers zoom change
          map.on("zoom", () => {
            console.log(`Zoom level: ${map.getZoom()}`);
          });
        });
      })
  })
</script>

<template>
<div id="windy"></div>
</template>

<style scoped>
#windy {
  width: 100%;
  height: 500px;
}
</style>

<style>
#windy #mobile-ovr-select,
#windy #embed-zoom {
  display: none !important;
}

#windy #logo-wrapper #logo {
  left: 80px;
}
</style>
