#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr 20 11:05:43 2021

@author: mariapalacios
"""

import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import OneHotEncoder
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split

RANDOM_SEED=42

# No uses rutas absolutas (solo funcionan en tu ordenador), usa rutas relativas
dataset = pd.read_csv("datasets/healthcare-dataset-stroke-data.csv")
dataset.head()

# Let's give better names to some categorical levels
dataset['hypertension'] = dataset['hypertension'].replace([0, 1], ['healthy-tension', 'hypertense'])
dataset['heart_disease'] = dataset['heart_disease'].replace([0, 1], ['healthy-heart', 'heart-disease'])
dataset['ever_married'] = dataset['ever_married'].replace(['No', 'Yes'], ['not-ever-married', 'ever-married'])
dataset['smoking_status'] = dataset['smoking_status'].replace(['Unknown'], ['unknown'])

X = dataset.drop(['id'], axis=1).iloc[:, :-1]
y = dataset.iloc[:, -1].values
# print(np.unique(y, return_counts=True)) # count number of 0s and 1s

# Remove 'Other' gender for easining the interpretation of results 
dataset = dataset.loc[dataset['gender'] != 'Other', :]

# Careful, this should be reviewed for each dataset
numerical_idx = X.select_dtypes(include=['float64']).columns
categorical_idx = X.select_dtypes(include=['object', 'bool', 'int64']).columns
assert X.shape[1] == (len(numerical_idx) + len(categorical_idx)), 'some column is missing'

# impute BMI's NAs
# X.columns[X.isna().any()].tolist() # This line may be used to check that indeed BMI has NAs
numerical_imp = SimpleImputer()
X_numerical = numerical_imp.fit_transform(X[numerical_idx])

# Encode categorical variables
oh_enc = OneHotEncoder()
X_cat = oh_enc.fit_transform(X[categorical_idx]).todense()

X = np.concatenate([X_cat, X_numerical], axis=1)
X_features = np.concatenate([oh_enc.get_feature_names(), numerical_idx])


C = 0.001
est = LogisticRegression(penalty='l1', C=C, random_state=RANDOM_SEED, solver='saga', max_iter=1000,
                         class_weight='balanced')
est.fit(X, y)
coefs = est.coef_.ravel()
relevant_columns = X_features[coefs != 0]
sparsity_l1 = np.mean(coefs == 0) * 100
print(f"C={C}")
print(f"Sparsity with L1 penalty: {sparsity_l1} ({np.sum(coefs != 0)} / {len(coefs)} columns)")
print(f"Relevant columns are: {', '.join(relevant_columns)}")
# print('Classification summary:')
# print(classification_report(y, est.predict(X)))

# El clasificador base solo usa age, avg_glucose_level, bmi
# Busca explicaciones en las que aparezcan variables distintas a estas tres.
# Usa X e y como datos (los nombres de las columnas estan en X_features), est  es el clasificador final

import lime.lime_tabular
#from lime.lime_text import LimeTabularExplainer
class_names=['healthy','stroke']
X= np.asarray(X)
explainer = lime.lime_tabular.LimeTabularExplainer(X, feature_names = list(X_features), 
                                                  class_names=class_names,
                                                  categorical_features=range(X_cat.shape[1]),
                                                  discretize_continuous=True)
#import matplotlib
import matplotlib.pyplot as plt



i =5108
#for i in range(len(dataset)):
exp = explainer.explain_instance(X[i], est.predict_proba, num_features=3, top_labels=len(X_features))#num features es tres 
#porque es realemente lo que queremos, lo que se sabemos que son importantes.

print('Document id: %d' % i)
print('Probability(stroke) =', est.predict_proba([X[i]])[0,1])
print('True class: %s' % class_names[y[i]])

#exp.as_list()
#posicion=exp.as_list()[0]
#primero=posicion[0].index('<')
#segundo=posicion[0].index('<=')
#first_feature=posicion[0][primero+1:segundo]
#posicion=exp.as_list()[1]
#primero=posicion[0].index('>')
#second_feature=posicion[0][0:primero]
#posicion=exp.as_list()[2]
#primero=posicion[0].index('>')
#second_feature=posicion[0][0:primero]
    #
    #print('Original prediction:', est.predict_proba(y[i])[0,1])
    #tmp = y[i].copy()
    #
    #print('Prediction removing some features:', est.predict_proba(tmp)[0,1])
    #print('Difference:', est.predict_proba(tmp)[0,1] - est.predict_proba(y[i])[0,1])

    #VISUALIZING EXPLANATIONS
fig = exp.as_pyplot_figure()
plt.subplots_adjust(left=0.35)
fig.show()
    
    #if (relevant_columns!= exp.)
    
    

    

#exp.save_to_file('/Users/mariapalacios/Desktop/TFG/oiStroke.html')
#exp.show_in_notebook(show_table=True)
    



    
    
    
    
    
    
