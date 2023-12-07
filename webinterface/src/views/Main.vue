<script setup>
import WeatherMapUI from "@/components/WeatherMapUI.vue";

</script>


<template>
  <v-app-bar
    color="grey-darken-4"
    density="compact"
  >
    <v-app-bar-title>Weather Fusion</v-app-bar-title>
  </v-app-bar>
  <v-main class="bg-grey-darken-3">
    <v-container>
      <v-row>
        <v-col cols="12">
          <WeatherMapUI />
        </v-col>
      </v-row>
    </v-container>
  </v-main>
</template>

<style scoped>

</style>
