#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May 28 11:26:07 2021

@author: mariapalacios
"""

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report

from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder
import matplotlib.pyplot as plt
RANDOM_SEED=42

# No uses rutas absolutas (solo funcionan en tu ordenador), usa rutas relativas
dataset = pd.read_csv("datasets/heart_failure_clinical_records_dataset.csv")
dataset.head()

dataset['anaemia'] = dataset['anaemia'].replace([0, 1], ['not-anaemia', 'anaemia'])
dataset['diabetes'] = dataset['diabetes'].replace([0, 1], ['not-diabetes', 'diabetes'])
dataset['high_blood_pressure'] = dataset['high_blood_pressure'].replace([0, 1], ['normal-bp', 'high-bp'])
dataset['sex'] = dataset['sex'].replace([0, 1], ['Female', 'Male'])
dataset['smoking'] = dataset['smoking'].replace([0, 1], ['not-smoker', 'smoker'])


X = dataset.drop('time', axis=1).iloc[:, :-1]
X_features = X.columns
y = dataset.iloc[:, -1].values

numerical_idx = X.select_dtypes(include=['float64', 'int64']).columns
categorical_idx = X.select_dtypes(include=['object', 'bool']).columns
assert X.shape[1] == (len(numerical_idx) + len(categorical_idx)), 'some column is missing'

scaler=StandardScaler()

# Encode categorical variables
X_numerical = scaler.fit_transform(X[numerical_idx])
oh_enc = OneHotEncoder()
X_cat = oh_enc.fit_transform(X[categorical_idx]).todense()


X = np.concatenate([X_cat, X_numerical], axis=1)
X_features = np.concatenate([oh_enc.get_feature_names(), numerical_idx])

colors=np.array(['blue', 'red'])[y]
plt.scatter(np.array(X[:, -2]).flatten(), np.array(X[:, -4]).flatten(), c=colors,
            alpha=0.4)
plt.show()

C = 0.025
est = LogisticRegression(penalty='l1', C=C, random_state=RANDOM_SEED, solver='saga', max_iter=1000,
                         class_weight='balanced')
est.fit(X, y)
coefs = est.coef_.ravel()
relevant_columns = X_features[coefs != 0]
sparsity_l1 = np.mean(coefs == 0) * 100
print(f"C={C}")
print(f"Sparsity with L1 penalty: {sparsity_l1} ({np.sum(coefs != 0)} / {len(coefs)} columns)")
print(f"Relevant columns are: {', '.join(relevant_columns)}")
print('Classification summary:')
print(classification_report(y, est.predict(X)))


import shap

i=100
class_names=['healthy','heart_failure']
X=np.array(X)
X_features=np.array(X_features)
#SHAP EXPLAINER
explainer = shap.KernelExplainer(est.predict, X)
shap_values = explainer.shap_values(X)


import pickle
with open('heart_failure-shap.pkl', 'wb') as fd:
    pickle.dump([explainer, shap_values], fd)