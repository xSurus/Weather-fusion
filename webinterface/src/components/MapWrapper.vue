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

function date_string_from_slider_value(five_min) {
  const date = new Date();

  if (five_min === 0) {
    return 'Now';
  }

  // Add slider value in minutes to date
  date.setMinutes(Math.round(date.getMinutes() / 5) * 5 + five_min * 5);

  return `${is_today(date) ? 'Today' : 'Tomorrow'}, ${dayNames[date.getDay()]} - ${date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}`;
}


const date_string = ref('');

date_string.value = date_string_from_slider_value(props.five_min);

watch(five_minutes, (newValue) => {
  date_string.value = date_string_from_slider_value(newValue);
});

const show_time_slider = ref(false);

function toggle_time_slider() {
  show_time_slider.value = !show_time_slider.value;
}
</script>

<template>
<div class="map_wrapper">
  <slot></slot>
  <v-btn
    prepend-icon="mdi-clock-time-seven-outline"
    class="time_selector ma-4"
    @click="toggle_time_slider"
  >
    {{ date_string }}
  </v-btn>
  <v-sheet
    v-show="show_time_slider"
    class="time_slider ma-4 pa-2 w-50"
    elevation="4"
    rounded
  >
    <v-slider
      v-model="five_minutes"
      :min="0"
      :max="288"
      step="1"
    ></v-slider>
  </v-sheet>
  <div class="text-caption map_caption mx-4 my-1">
    <slot name="caption"></slot>
  </div>
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
}

.text-caption :deep(a) {
  color: #fff;
  text-decoration: none;
}

.text-caption :deep(a:hover) {
  text-decoration: underline;
}
</style>
