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

const fiveMinutesInADay = 288;
</script>

<template>
<v-window v-model="tab" class="h-100">
  <v-window-item value="windy" class="h-100">
    <WindyMap ref="windy" :five_min="dateSlider" :initial_view="map_view"></WindyMap>
  </v-window-item>
  <v-window-item value="rain" class="h-100">
    <RainMap ref="rain" :five_min="dateSlider" :initial_view="map_view"></RainMap>
  </v-window-item>
  <v-window-item value="danger" class="h-100">
    <DangerMap ref="danger" :five_min="dateSlider" :initial_view="map_view"></DangerMap>
  </v-window-item>
</v-window>
            <!--<v-col cols="12" class="pt-0 mt-0">
              <v-slider
                color="primary"
                thumb-color="white"
                track-color="grey-darken-2"
                v-model="dateSlider"
                :max="fiveMinutesInADay"
                :min="0"
                step="1"
              >
              </v-slider>
            </v-col>-->
      <!--<v-sheet
        color="grey-darken-4"
        rounded
        class="pa-6"
        :elevation="5"
      >
        <v-tabs
          v-model="tab"
          direction="vertical"
        >
          <v-tab value="windy">
            Windy
          </v-tab>
          <v-tab value="rain">
            Rain
          </v-tab>
          <v-tab value="danger">
            Danger
          </v-tab>
        </v-tabs>
      </v-sheet>-->
</template>

<style scoped>

</style>
