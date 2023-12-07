<script setup>
import { ref } from 'vue'

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
            Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed ac erat eget nisl euismod aliquet. Nullam
            sodales euismod leo, quis euismod libero tincidunt sed. Nulla facilisi. Nulla facilisi. Nulla facilisi.
          </v-window-item>
          <v-window-item value="option-2">
            Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed ac erat eget nisl euismod aliquet. Nullam
            sodales euismod leo, quis euismod libero tincidunt sed. Nulla facilisi. Nulla facilisi. Nulla facilisi.
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
