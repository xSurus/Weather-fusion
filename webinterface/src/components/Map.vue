<script setup>
const MAPBOX_TOKEN = 'pk.eyJ1IjoiaXFpc215c2VucGFpIiwiYSI6ImNscHdtNHhnbzBoOGIybHA5cXB6OXBqYTgifQ.qvhDbZQkOTNCBqgSnKNANw';
import {ref, onMounted} from 'vue';
import { createMap } from 'mapbox-composition';

const mapCenter = ref([8.095723, 46.791793]);
const map = ref(null);

onMounted(() => {
  const mapBox = createMap(map.value, {
    style: 'mapbox://styles/mapbox/light-v11',
    center: mapCenter.value,
    zoom: 6.8,
    minZoom: 6.8,
    maxZoom: 12,
    maxBounds: [[5.2559111595, 45.4179931641], [11.2920501709, 48.208380127]],
    accessToken: MAPBOX_TOKEN,
  });
});
</script>

<template>
  <div class="map" ref="map"></div>
</template>

<style scoped>
.map {
  height: 500px;
  width: 100%;
}

</style>
