
import os
import pickle
import pathlib
import pandas as pd
import numpy as np
from catboost import CatBoostClassifier

# Model params
cat_features = ['gamecategory', 'subgamecategory', 'bundle', 'oblast', 'city', 'os', 'osv']

split_params = {'folds': 5}

model_params = {'objective': 'MultiClass', 
                'iterations':3,
                'learning_rate':0.05,               
                'depth': 5, 
                'l2_leaf_reg': 50,  
                'one_hot_max_size': 15,
                'task_type': 'CPU',
                'has_time': False,
                'random_state': 20210926                
               }

train_params = {'early_stopping_rounds': 150, 
                'silent': True,
                'plot': True               
               }

gpu_params = {'devices': '0',
              'data_partition': 'DocParallel',
              'max_ctr_complexity': 4,
#              'bootstrap_type': 'MVS',
              'border_count': 128, 
              'fold_permutation_block': 0,
              'simple_ctr':'FeatureFreq',
              'combinations_ctr': 'FeatureFreq',      
              'ctr_target_border_count': 1,
              'random_strength': 0.95,
              'gpu_ram_part': 0.95
             }


cpu_params = {'thread_count': 14}

features_params = {'cat_features': cat_features}

observations_params = {"weight": 'not_implemented'}

params = {'split_params': split_params, 
          'model_params': model_params, 
          'train_params': train_params, 
          'gpu_params': gpu_params, 
          'cpu_params': cpu_params, 
          'features_params': features_params, 
          'observations_params': observations_params
         }

def get_time_features(data):
    data['hour_shift'] = data['shift'].apply(lambda x: x.replace('MSK', ''))
    data['hour_shift'] = data['hour_shift'].replace({'': 0, 'missing': 0}).astype('int8')
    
    data['local_time'] = data['created'] + pd.to_timedelta('1H') * data['hour_shift']
    data['month'] = data['local_time'].dt.month.astype('int8')
    data['date'] = data['local_time'].dt.date
    data['day'] = data['local_time'].dt.day.astype('int8')
    data['wd'] = data['local_time'].dt.weekday.astype('int8')
    data['hour'] = data['local_time'].dt.hour.astype('int8')
    data['minutes'] = data['local_time'].dt.minute.astype('int8')
    return data


class Model():
    def __init__(self, params):
        self.params = params
        self.device = params['model_params']['task_type']
        self.model_params = params['model_params']
        self.folds = params['split_params']['folds']        
        self.train_params = params['train_params']
        self.gpu_params = params['gpu_params']
        self.cpu_params = params['cpu_params']
        self.features_params = params['features_params']
        self.observations_params = params['observations_params'] 
        self.models = []
        self.model_predictions = []
        self.predictions_summary = None        
        self.importance = []
        self.features = None
        
    def fit(self, X, y): 
        self.features = X.columns
        self.model_params = self.model_params | self.gpu_params if self.device == 'GPU' else \
            self.model_params | self.cpu_params   
        
        for fold in range(self.folds):
            print(f'\nFold: {fold + 1}')
            self.model_params['random_state'] += 1 
            
            if self.folds > 1:
                train_idx = [x for x in range(X.shape[0]) if x%self.folds != fold]
                val_idx = [x for x in range(X.shape[0]) if x%self.folds == fold]            
            
                X_train = X.iloc[train_idx]
                y_train = y.iloc[train_idx]
            
                X_val = X.iloc[val_idx]
                y_val = y.iloc[val_idx] 
            else:
                X_train = X
                y_train = y

            train_dataset = Pool(data=X_train, label=y_train, **self.features_params)                
           
            model = CatBoostClassifier(**self.model_params)    
            
            if self.folds > 1:
                eval_dataset = Pool(data=X_val, label=y_val, **self.features_params)  
                model.fit(train_dataset, eval_set=eval_dataset, **self.train_params)
            else:
                model.fit(train_dataset,  **self.train_params)
            
            self.models.append(model.copy())   

        self.calculate_importance()
            
        
    def predict(self, X):
        self.model_predictions = []
        for model_number in range(self.folds):    
            model = self.models[model_number]
            columns = [str(x) + '__' + str(model_number) for x in model.get_all_params()['class_names']]
            df = pd.DataFrame(data=model.predict_proba(X), columns=columns)
            self.model_predictions.append(df)  
    
        self.predictions_summary = pd.concat(self.model_predictions, axis=1)

        labels = model.get_all_params()['class_names']
        for label in labels:
            label_columns = [x for x in self.predictions_summary.columns if f'{label}__' in str(x)]
            self.predictions_summary[label] = self.predictions_summary[label_columns].mean(axis=1)

        self.predictions_summary['prediction'] = self.predictions_summary[labels].idxmax(axis=1)
        self.predictions_summary['confidence'] = self.predictions_summary[labels].max(axis=1)
                    
        return self.predictions_summary  
  
   
    def save_models(self, path):
        for model_number, model in enumerate(self.models):
            model.save_model(path + f"model{model_number}.cbm")
            
    def load_models(self, path, file_prefix=''):
        for model_number in range(self.folds):
            model = CatBoostClassifier()
            model.load_model(path.joinpath(f"{file_prefix}model{model_number}.cbm"))
            self.models.append(model.copy())
            
    def calculate_importance(self):
        for model_number in range(self.folds):
            fi_dict = list(zip(self.features, self.models[model_number].feature_importances_))
            importance_df = pd.DataFrame.from_records(fi_dict).set_index(0)
            importance_df.columns = ['importance']
            importance_df = importance_df.sort_values('importance', ascending=False)
            self.importance.append(importance_df) 
            

def predict(data: pd.DataFrame) -> pd.DataFrame:
    data = data.fillna('missing')
    data = get_time_features(data)
    
    model = Model(params)    
    model.load_models(path=pathlib.Path(__file__).parent, file_prefix='models/segmentation_model_')
    predictions = model.predict(data[model.models[0].feature_names_])
    
    return predictions
