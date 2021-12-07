<template>
  <v-card :loading="loading">
    <v-card-text>
      <v-form ref="classification" v-model="valid" lazy-validation>
        <v-row>
          <v-col cols="12" md="8" >
            <v-row>
              <v-col cols="12" md="6" >
                <v-text-field
                  v-model="gamecategory"
                  :counter="20"
                  :rules="gamecategoryRules"
                  label="Категория"
                  required></v-text-field>
              </v-col>
              <v-col cols="12" md="6" >
                <v-text-field
                  v-model="subgamecategory"
                  :counter="50"
                  :rules="subgamecategoryRules"
                  label="Подкатегория"
                  required></v-text-field>
              </v-col>
            </v-row>
            
            <v-text-field
              v-model="bundle"
              :counter="150"
              :rules="bundleRules"
              label="Сборка"
              required></v-text-field>

            <v-row class="mb-3">
              <v-col>
                <v-menu
                  v-model="dateMenu"
                  :close-on-content-click="false"
                  :nudge-right="40"
                  transition="scale-transition"
                  offset-y
                  min-width="290px"
                  max-width="290px">
                  <template v-slot:activator="{on}">
                    <v-text-field
                      readonly
                      hide-details
                      :value="created"
                      label="Дата"
                      v-on="on"
                      @focus="focusDate"
                      @blur="blurDate"
                    ></v-text-field>
                  </template>
                  <v-date-picker
                    locale="ru-ru"
                    v-model="created"
                    no-title
                    @input="dateMenu = false"
                  ></v-date-picker>
                </v-menu>
              </v-col>
            </v-row>

            <v-text-field
              v-model="shift"
              :counter="6"
              :rules="shiftRules"
              label="Зона"
              required></v-text-field>
          
            <v-row>
              <v-col cols="12" md="6" >
                <v-text-field
                  v-model="oblast"
                  :counter="120"
                  :rules="oblastRules"
                  label="Область"
                  required></v-text-field>
              </v-col>
              <v-col cols="12" md="6" >
                <v-text-field
                  v-model="city"
                  :counter="120"
                  :rules="cityRules"
                  label="Город"
                  required></v-text-field>
              </v-col>
            </v-row>

            <v-row>
              <v-col cols="12" md="6" >
                <v-text-field
                  v-model="os"
                  :counter="15"
                  :rules="osRules"
                  label="Система"
                  required></v-text-field>
              </v-col>
              <v-col cols="12" md="6" >
                <v-text-field
                  v-model="osv"
                  :counter="6"
                  :rules="osvRules"
                  label="Версия"
                  required></v-text-field>
              </v-col>
            </v-row>
          </v-col>
          <v-col cols="12" md="4">
            <div id="classification-plot"></div>
          </v-col>
        </v-row>
      </v-form>
    </v-card-text>
    <v-divider></v-divider>
    <v-card-actions>
      <v-btn color="success" text :disabled="!valid" @click="classify">
        Классифицировать
      </v-btn>
    </v-card-actions>
  </v-card>
</template>

<script>
  import axios from 'axios';
  import Plotly from 'plotly.js-dist-min';

  export default {
    name: 'classification',

    data: () => ({
      valid: true,
      loading: false,

      gamecategory: 'Applications',
      gamecategoryRules: [
        v => !!v || 'Game category is required',
        v => (v && v.length <= 20) || 'Game category must be less than 20 characters',
      ],
      
      subgamecategory: 'Shopping',
      subgamecategoryRules: [
        v => !!v || 'Sub game category category is required',
        v => (v && v.length <= 50) || 'Sub game category must be less than 50 characters',
      ],

      bundle: 'com.allgoritm.youla',
      bundleRules: [
        v => !!v || 'Bundle is required',
        v => (v && v.length <= 20) || 'Bundle must be less than 150 characters',
      ],

      dateMenu: false,
      created: '2021-09-19',

      shift: 'MSK+2',
      shiftRules: [
        v => !!v || 'Shift is required',
        v => (v && v.length <= 6) || 'Shift must be less than 6 characters',
      ],

      oblast: 'Томская область',
      oblastRules: [
        v => !!v || 'Region is required',
        v => (v && v.length <= 120) || 'Region must be less than 120 characters',
      ],

      city: 'Северск',
      cityRules: [
        v => !!v || 'City is required',
        v => (v && v.length <= 120) || 'City must be less than 120 characters',
      ],

      os: 'android',
      osRules: [
        v => !!v || 'OS is required',
        v => (v && v.length <= 15) || 'OS must be less than 15 characters',
      ],

      osv: '10.0',
      osvRules: [
        v => !!v || 'OS version is required',
        v => (v && v.length <= 6) || 'OS version must be less than 6 characters',
      ],
      
      layout: {
        margin: {
          l: 60,
          r: 10,
          b: 0,
          t: 10,
          pad: 4
        },
        showlegend: false,
        colorway : ['#f3cec9', '#e7a4b6', '#cd7eaf', '#a262a9', '#6f4d96', '#3d3b72', '#182844', '#ffa600']
      }
    }),
    methods: {
      classify () {
        this.loading = true;
        if (this.$refs.classification.validate()) {
          axios.post(`${process.env.VUE_APP_API_ROOT}predict`, [{
            gamecategory: this.gamecategory,
            subgamecategory: this.subgamecategory,
            bundle: this.bundle,
            created: this.created + ' 17:31:33', // TODO: Add time picker
            shift: this.shift,
            oblast: this.oblast,
            city: this.city,
            os: this.os,
            osv: this.osv
          }]).then(response => {
            if (response.status == 200) {
              let predictions = JSON.parse(response.data);
              this.loading = false;
              this.plot(predictions[0]);
            }
          });
        }
      },
      plot(prediction) {
        var values = [prediction[1], prediction[3], prediction[4], prediction[5]];
        var labels = ['Женщины, 25-41 год ', 'Женщины, 25-41 год, Дети', 'Мужчины\\Женшины, 18-44 года, Животные', 'Мужчины\\Женшины, 18-45 лет'];

        var data = [{
          values: values,
          labels: labels,
          domain: {column: 0},
          name: 'Category',
          hoverinfo: 'label+percent+name',
          hole: .6,
          type: 'pie'
        }];

        Plotly.newPlot('classification-plot', data, this.layout, { responsive: true });
      },
      focusDate() {
        setTimeout(() => {
          if (!this.dateMenu) {
            this.dateMenu = true;
          }
        }, 200);
      },
      blurDate() {
        setTimeout(() => {
          if (this.dateMenu) {
            this.dateMenu = false;
          }
        }, 200);
      }
    },
    mounted() {
      this.classify();
    }
  }
</script>
