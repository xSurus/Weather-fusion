<script setup>
import WeatherMapUI from "@/components/WeatherMapUI.vue";
import {ref} from "vue";

const views = ref([
  {
    name: 'windy',
    title: 'Wind',
  },
  {
    name: 'rain',
    title: 'Rain',
  },
  {
    name: 'danger',
    title: 'Danger',
  },
]);

const selected_view = ref('windy');
function select_map(name) {
  selected_view.value = name;
}

</script>


<template>
  <v-app-bar
    color="grey-darken-4"
    density="compact"
  >
    <v-avatar
      size="36"
      class="ml-4"
    >
      <v-img
        src="/logo_white.png"
        max-height="48"
        max-width="48"
      ></v-img>
    </v-avatar>
    <v-app-bar-title>Weather Fusion</v-app-bar-title>
    <v-spacer></v-spacer>
    <v-toolbar-items>
      <v-btn
        v-for="item in views"
        :key="item.name"
        @click="select_map(item.name)"
        :variant="item.name === selected_view ? 'tonal' : 'text'"
      >
        {{ item.title }}
      </v-btn>
    </v-toolbar-items>
  </v-app-bar>
  <v-main class="bg-grey-darken-3">
    <WeatherMapUI :map="selected_view"/>
  </v-main>
</template>

<style scoped>
</style>
