<script setup>
import {ref, watch} from 'vue'
import WindyMap from "@/components/WindyMap.vue";
import RainMap from "@/components/RainMap.vue";
import DangerMap from "@/components/DangerMap.vue";

const props = defineProps({
  map: {
    type: String,
    default: 'windy',
  },
});

watch(() => props.map, (val) => {
  tab.value = val;
});

const tab = ref('');

const windy = ref(null);
const rain = ref(null);
const danger = ref(null)

const map_view = ref({
  center: [46.791793, 8.095723],
  zoom: 8,
});

watch(tab, (newVal, OldVal) => {
  let view = null;
  switch(OldVal) {
    case 'windy':
      view = windy.value.get_map_view();
      break;
    case 'rain':
      view = rain.value.get_map_view();
      break;
    case 'danger':
      view = danger.value.get_map_view();
      break;

  }

  if (view === null) {
    return;
  }

  map_view.value = view;

  switch(newVal) {
    case 'windy':
      if (windy.value === null) {
        return;
      }
      windy.value.set_map_view(view);
      break;
    case 'rain':
      if (rain.value === null) {
        return;
      }
      rain.value.set_map_view(view);
      break;
    case 'danger':
      if (danger.value === null) {
        return;
      }
      danger.value.set_map_view(view);
      break;
  }


});

const dateSlider = ref(0);

function date_slider_change(val) {
  dateSlider.value = val;
}
</script>

<template>
<v-window v-model="tab" class="h-100">
  <v-window-item value="windy" class="h-100">
    <WindyMap ref="windy" v-model:five_min="dateSlider" :initial_view="map_view"></WindyMap>
  </v-window-item>
  <v-window-item value="rain" class="h-100">
    <RainMap ref="rain" v-model:five_min="dateSlider" :initial_view="map_view"></RainMap>
  </v-window-item>
  <v-window-item value="danger" class="h-100">
    <DangerMap ref="danger" v-model:five_min="dateSlider" :initial_view="map_view"></DangerMap>
  </v-window-item>
</v-window>
</template>

<style scoped>

</style>
