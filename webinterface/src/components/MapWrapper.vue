<script setup>
import {computed, ref, watch} from "vue";

const dayNames = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];

const props = defineProps({
  five_min: {
    type: Number,
    default: 0,
  },
});

const emit = defineEmits(['update:five_min']);

const five_minutes = computed({
  get() {
    return props.five_min;
  },
  set(value) {
    emit('update:five_min', value);
  },
});
function is_today(date) {
  const today = new Date();
  return date.getDate() === today.getDate() &&
    date.getMonth() === today.getMonth() &&
    date.getFullYear() === today.getFullYear();
}

function date_string_from_slider_value(date) {
  return `${is_today(date) ? 'Today' : 'Tomorrow'}, ${dayNames[date.getDay()]} - ${date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}`;
}

// Map date hours into actual number words "one", "two", ... "twelve"
function twelve_hour_string_from_date(date) {
  const numbers = ['twelve', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten',
    'eleven'];
  const hour = date.getHours() % 12;
  return numbers[hour]
}

const date_string = ref('');
const twelve_hour_string = ref('');

function updates_strings (mins) {


  const date = new Date();

  // Add slider value in minutes to date
  date.setMinutes(Math.floor(date.getMinutes() / 5) * 5 + mins * 5);

  twelve_hour_string.value = twelve_hour_string_from_date(date);

  if (mins === 0) {
    date_string.value = 'Now';
    return;
  }

  date_string.value = date_string_from_slider_value(date);
}
watch(five_minutes, updates_strings);

updates_strings(five_minutes.value);
</script>

<template>
<div class="map_wrapper">
  <slot></slot>
  <v-btn
    :prepend-icon="`mdi-clock-time-${twelve_hour_string}-outline`"
    class="time_selector ma-4"
  >
    {{ date_string }}
  </v-btn>
  <div
    class="time_slider ma-4 w-50"
  >
    <v-slider
      v-model="five_minutes"
      :min="0"
      :max="288"
      step="1"
      class="pa-0 ma-0"
      hide-details="true"
      track-color="grey-darken-4"
      color="white"
    ></v-slider>
  </div>
  <div class="text-caption map_caption mx-4 my-1">
    <slot name="caption"></slot>
  </div>
  <v-sheet
    class="legend ma-4"
    color=""
    rounded
    elevation="4"
  >
    Hello
  </v-sheet>
</div>
  <!--<slot name="caption"></slot>-->
  <!--<div class="date bg-primary pa-2">
    {{ date_string }}
  </div>-->
</template>

<style scoped>
.map_wrapper {
  position: relative;
  width: 100%;
  height: 100%;
}

.time_selector {
  position: absolute;
  bottom: 0;
  left: 0;
  z-index: 1000;
}

.time_slider {
  position: absolute;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  z-index: 1000;
}

.legend {
  position: absolute;
  bottom: 1rem;
  right: 0;
  z-index: 1000;
}

:deep(#windy), :deep(#rain), :deep(#danger){
  width: 100%;
  height: inherit;
  overflow: hidden;
}

.map_caption {
  position: absolute;
  bottom: 0;
  right: 0;
  z-index: 1000;
  color: white;
  mix-blend-mode: difference;
}

.text-caption :deep(a) {
  color: white;
  mix-blend-mode: difference;
  text-decoration: none;
}

.text-caption :deep(a:hover) {
  text-decoration: underline;
}
</style>
