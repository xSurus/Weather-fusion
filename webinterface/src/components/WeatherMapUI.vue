<script setup>
import { ref } from 'vue'
import Map from './Map.vue'
import WindyMap from "@/components/WindyMap.vue";

const tab = ref('');
</script>

<template>
<v-container>
  <v-row>
    <v-col cols="10">
      <v-sheet
        color="grey-darken-4"
        rounded
        class="pa-6"
      >
        <v-window v-model="tab">
          <v-window-item value="option-1">
            <WindyMap></WindyMap>
          </v-window-item>
          <v-window-item value="option-2">
            <Map></Map>
          </v-window-item>
        </v-window>
      </v-sheet>
    </v-col>
    <v-col cols="2">
      <v-sheet
        color="grey-darken-4"
        rounded
        class="pa-6"
      >
        <v-tabs
          v-model="tab"
          direction="vertical"
        >
          <v-tab value="option-1">
            Option 1
          </v-tab>
          <v-tab value="option-2">
            Option 2
          </v-tab>
        </v-tabs>
      </v-sheet>
    </v-col>
  </v-row>
</v-container>
</template>

<style scoped>

</style>
