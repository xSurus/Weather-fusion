<script setup>
import {computed, ref, watch} from "vue";

const dayNames = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];

const props = defineProps({
  five_min: {
    type: Number,
    default: 0,
  },
});

const five_minutes = computed(() => {
  return props.five_min;
});
function is_today(date) {
  const today = new Date();
  return date.getDate() === today.getDate() &&
    date.getMonth() === today.getMonth() &&
    date.getFullYear() === today.getFullYear();
}

function date_string_from_slider_value(five_min) {
  const date = new Date();

  // Add slider value in minutes to date
  date.setMinutes(Math.round(date.getMinutes() / 5) * 5 + five_min * 5);

  return `${is_today(date) ? 'Today' : 'Tomorrow'}, ${dayNames[date.getDay()]} - ${date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}`;
}


const date_string = ref('');

date_string.value = date_string_from_slider_value(props.five_min);

watch(five_minutes, (newValue) => {
  date_string.value = date_string_from_slider_value(newValue);
});
</script>

<template>
<div class="map_wrapper">
  <slot></slot>
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

.date_wrapper {
  display: flex;
  justify-content: center;
}

.date {
  width: max-content;
}

:deep(#windy), :deep(#rain), :deep(#danger){
  width: 100%;
  height: inherit;
  overflow: hidden;
}

.text-caption :deep(a) {
  color: #fff;
  text-decoration: none;
}

.text-caption :deep(a:hover) {
  text-decoration: underline;

}
</style>
