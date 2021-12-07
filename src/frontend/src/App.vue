<template>
  <v-app>
    <v-app-bar app>
      <v-container>
        <img :src="require('./assets/waico.svg')">
        <div class="float-right">
          <v-btn color="success" href="api/doc" small>
            SWAGGER
          </v-btn>
        </div>
      </v-container>
    </v-app-bar>

    <v-main>
      <v-container>
        <v-row>
          <v-col>
            <h1 class="font-weight-thin mb-2 mt-6">Классификация</h1>
            <classification />
          </v-col>
        </v-row>
        <v-row>
          <v-col>
            <h1 class="font-weight-thin mb-2 mt-6">Сегментация</h1>
            <segmentation />
          </v-col>
        </v-row>
      </v-container>
    </v-main>
  </v-app>
</template>

<script>
import Classification from './components/Classification';
import Segmentation from './components/Segmentation';

export default {
  name: 'App',

  components: {
    Classification,
    Segmentation
  }
};
</script>
