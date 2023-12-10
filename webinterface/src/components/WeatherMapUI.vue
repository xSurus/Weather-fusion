<script setup>
import {ref, watch} from 'vue'
import Map from './Map.vue'
import WindyMap from "@/components/WindyMap.vue";
import RainMap from "@/components/RainMap.vue";

const tab = ref('');

const dateSlider = ref(0);

const dayNames = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
const fiveMinutesInADay = 288;

function is_today(date) {
  const today = new Date();
  return date.getDate() === today.getDate() &&
         date.getMonth() === today.getMonth() &&
         date.getFullYear() === today.getFullYear();
}

function date_string_from_slider_value(slider_value) {
  const date = new Date();

  // Add slider value in minutes to date
  date.setMinutes(Math.round(date.getMinutes() / 5) * 5 + slider_value * 5);

  return `${is_today(date) ? 'Today' : 'Tomorrow'}, ${dayNames[date.getDay()]} - ${date.getHours()}:${date.getMinutes()}`;
}


const date_string = ref('');

watch(dateSlider, (newValue, oldValue) => {
  date_string.value = date_string_from_slider_value(newValue);
});
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
                <v-window-item value="option-1">
                  <WindyMap></WindyMap>
                </v-window-item>
                <v-window-item value="option-2">
                  <RainMap></RainMap>
                </v-window-item>
              </v-window>
            </v-col>
          </v-row>
          <v-row justify="center">
            <v-col cols="3">
              <v-sheet
                class="pa-2"
                color="primary text-center"
              >
                {{ date_string }}
              </v-sheet>
            </v-col>
          </v-row>
          <v-row>
            <v-col cols="12">
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
          <v-tab value="option-1">
            Windy
          </v-tab>
          <v-tab value="option-2">
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
