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
  import axios from 'axios';
  import Plotly from 'plotly.js-dist-min';

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
      items: [],
      table: [],
      colorway: ['#003f5c', '#2f4b7c', '#665191', '#a05195', '#d45087', '#f95d6a', '#ff7c43', '#ffa600']
    }),
    methods: {
      upload() {
        if (this.file) {
          let formData = new FormData();
          formData.append('file', this.file);
          this.loading = true;
          axios.post(`${process.env.VUE_APP_API_ROOT}csv`,
            formData,
            {
              headers: {
                'Content-Type': 'multipart/form-data'
              }
            }
          ).then(response => {
            if (response.status == 200) {
              this.items = JSON.parse(response.data.records);
              this.table = JSON.parse(response.data.table);

              this.loading = false;
              this.clustering();
            }
          })
          .catch(error => {
            console.error(error.message);
            this.loading = false;
          });
        }
      },
      
      clustering() {
        var traces = []

        var clusters = [...(new Set(this.items.map(x => x.cluster)))].sort();
        var segments = [...(new Set(this.items.map(x => x.Segment)))].sort();
        
        segments.forEach(segment => {
          let segment_clasters = []
          
          clusters.forEach(cluster => {
            segment_clasters.push(this.items.filter(d => d.cluster == cluster && d.Segment == segment).length)
          });

          traces.push({
            x: clusters,
            y: segment_clasters,
            name: segment,
            type: 'bar'
          });
        });

        var layout = { barmode: 'stack', colorway : this.colorway };
        Plotly.newPlot("segment-clusters", traces, layout, { responsive: true })

        let clusters_counts = [];
        clusters.forEach(cluster => {
          clusters_counts.push(this.items.filter(d => d.cluster == cluster).length)
        });

        var data = [{
          values: clusters_counts,
          labels: clusters,
          domain: {column: 0},
          name: 'Кластер',
          hoverinfo: 'label+percent+name',
          hole: .6,
          type: 'pie'
        }];

        layout = {
          margin: {
            l: 60,
            r: 10,
            b: 0,
            t: 10,
            pad: 4
          },
          showlegend: false,
          colorway : this.colorway
        };
        Plotly.newPlot('clusters-counts', data, layout, { responsive: true });

        this.file = undefined;
      }
    },
    mounted() {
      if (this.items.length == 0) {
        this.loading = true;
        axios.get(`${process.env.VUE_APP_API_ROOT}static/demo.json`).then(response => {
          this.items = response.data.records;
          this.table = response.data.table;
          this.loading = false;
          this.clustering();
        });
      }
    }
  }
</script>
