<script setup>
const MAPBOX_TOKEN = 'pk.eyJ1IjoiaXFpc215c2VucGFpIiwiYSI6ImNscHdtNHhnbzBoOGIybHA5cXB6OXBqYTgifQ.qvhDbZQkOTNCBqgSnKNANw';
import { ref } from 'vue';
import { MapboxMap } from '@studiometa/vue-mapbox-gl';


const mapCenter = ref([8.095723, 46.791793]);
</script>

<template>
  <MapboxMap
    style="height: 500px"
    :access-token="MAPBOX_TOKEN"
    map-style="mapbox://styles/mapbox/light-v11"
    :center="mapCenter"
    :zoom="6.8"
    :pitch="0"
    :bearing="0"
    :minZoom="6.8"
    :maxZoom="13"
    :maxBounds="[[5.2559111595, 45.4179931641], [11.2920501709, 48.208380127]]"
  />
</template>

<style scoped>

</style>
