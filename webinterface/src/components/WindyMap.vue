<script setup>
import MapWrapper from "@/components/MapWrapper.vue";

const WindyToken = 'zqPWHzq2Rai9frfxQp6gczIGDkYk6VzS';
import {ref, onMounted, watch, computed} from 'vue';
import { loadScript } from "vue-plugin-load-script";

const min_lat = 45.398181;
const max_lat = 48.230651;
const min_lon = 5.140242;
const max_lon = 11.47757;

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
  this.$forceUpdate();
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

      const { map, store, utils, broadcast, picker  } = windyAPI;
      windy_store = store;
      windy_map = map;
      // .map is instance of Leaflet map

      map.setMinZoom(8);
      map.setMaxZoom(11);
      map.setMaxBounds([[min_lat, min_lon], [max_lat, max_lon]]);
    });
  })
})
</script>

<template>
<MapWrapper v-model:five_min="five_minutes" type="windy">
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

#windy #progress-bar,
#windy #bottom,
#windy #mobile-ovr-select {
  display: none !important;
}

#windy #embed-zoom {
  top: 0 !important;
}
</style>
