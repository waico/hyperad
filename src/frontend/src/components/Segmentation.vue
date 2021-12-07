<template>
  <div>
    <v-row class="mb-3">
      <v-file-input
        v-model="file"
        accept=".csv"
        show-size
        counter
        label="Выберите файл .csv">
      </v-file-input>
      <v-btn
        :disabled="!file"
        color="blue-grey"
        class="ma-2 white--text"
        @click="upload">
        Загрузить
        <v-icon right dark> mdi-cloud-upload </v-icon>
      </v-btn>
    </v-row>
    <v-row class="mb-3">
      <v-layout child-flex>
          <v-data-table
          :headers="headers"
          :items="items"
          :items-per-page="15"
          :loading='loading'
          class="elevation-1"
        ></v-data-table>
      </v-layout>
    </v-row>
    <v-row>
      <v-col cols="12" md="4">
        <h3 class="font-weight-thin text-center">Распределение данных по кластерам</h3>
        <div id="clusters-counts"></div>
      </v-col>
      <v-col cols="12" md="8" >
        <h3 class="font-weight-thin text-center">Распределение сегментов по кластерам</h3>
        <div id="segment-clusters"></div>
      </v-col>
    </v-row>
  </div>
</template>

<script>
  export default {
    name: 'segmentation',

    data: () => ({
      file: undefined,
      loading: false,
      headers: [
        { text: 'Категория', value: 'gamecategory' },
        { text: 'Регион', value: 'oblast' },
        { text: 'Система', value: 'os' },
        { text: 'Версия', value: 'osv' },
        { text: 'Сегмент', value: 'Segment' },
        { text: 'Кластер', value: 'cluster' }
      ],
      items: []
    }),
    methods: {
      upload() {

      },
      
      clustering() {

      }
    },
    mounted() {

    }
  }
</script>
