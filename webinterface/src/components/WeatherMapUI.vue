<script setup>
import {ref, watch} from 'vue'
import WindyMap from "@/components/WindyMap.vue";
import RainMap from "@/components/RainMap.vue";

const tab = ref('');

const windy = ref(null);
const rain = ref(null);

watch(tab, (newVal, OldVal) => {
  let view = null;
  switch(OldVal) {
    case 'windy':
      view = windy.value.get_map_view();
      break;
    case 'rain':
      view = rain.value.get_map_view();
      break;
  }
  console.log(view)

  if (view === null) {
    return;
  }
  // switch(newVal) {
  //   case 'windy':
  //     windy.value.set_map_view(view);
  //     break;
  //   case 'rain':
  //     rain.value.set_map_view(view);
  //     break;
  // }
});

const dateSlider = ref(0);

const fiveMinutesInADay = 288;
</script>

<template>
<v-container>
  <v-row>
    <v-col cols="10">
      <v-sheet
        color="grey-darken-4"
        rounded
        :elevation="5"
      >
        <v-container>
          <v-row>
            <v-col cols="12">
              <v-window v-model="tab">
                <v-window-item value="windy">
                  <WindyMap ref="windy" :five_min="dateSlider"></WindyMap>
                </v-window-item>
                <v-window-item value="rain">
                  <RainMap ref="rain" :five_min="dateSlider"></RainMap>
                </v-window-item>
              </v-window>
            </v-col>
          </v-row>
          <v-row>
            <v-col cols="12" class="pt-0 mt-0">
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
            </v-col>
          </v-row>
        </v-container>
      </v-sheet>
    </v-col>
    <v-col cols="2">
      <v-sheet
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
        </v-tabs>
      </v-sheet>
    </v-col>
  </v-row>
</v-container>
</template>

<style scoped>

</style>
