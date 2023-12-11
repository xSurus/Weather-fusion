<script setup>
import {ref, watch} from 'vue'
import Map from './Map.vue'
import WindyMap from "@/components/WindyMap.vue";
import RainMap from "@/components/RainMap.vue";

const tab = ref('');

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
                <v-window-item value="option-1">
                  <WindyMap :five_min="dateSlider"></WindyMap>
                </v-window-item>
                <v-window-item value="option-2">
                  <RainMap :five_min="dateSlider"></RainMap>
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
