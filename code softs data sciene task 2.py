# -*- coding: utf-8 -*-
"""IMDB Rating Prediction Model

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/#fileId=https%3A//storage.googleapis.com/kaggle-colab-exported-notebooks/imdb-rating-prediction-model-45051150-7269-4874-bb6a-ce00041d8be5.ipynb%3FX-Goog-Algorithm%3DGOOG4-RSA-SHA256%26X-Goog-Credential%3Dgcp-kaggle-com%2540kaggle-161607.iam.gserviceaccount.com/20240807/auto/storage/goog4_request%26X-Goog-Date%3D20240807T061112Z%26X-Goog-Expires%3D259200%26X-Goog-SignedHeaders%3Dhost%26X-Goog-Signature%3D3eefbd3209d8cc8d0cee4bf18846a4289ae1db44c694255bd318106239c5f10e5992a9803eb685e4e0e52a0c9a5b2eba8198b4032d892b09cd84f02d67452f3c3e692c5936b08bd9cf80bf58eccc8315f182acac542e8498c12f5c6a688d917dc009ac1809cbdb3a67e2ad0dfeb7234ddef45b0e6724c6eccf0542a8fc32c60bd6551500102e896027bbc33314796fcfeb6c6683f5fbe823ef4a78112fd5d0ddf0f4f3577b4a9fa50fb928afaa95f334703056d03c78f5aea48057de396a4891ad988cbdba3058db2094e7717931aa69a6cd49e8b47323dabf305ce7115a29868340fc13c75c4175af3a09a29083b1161d3ed9ad8f1fdd15cc74d834a852fe8a
"""

# IMPORTANT: RUN THIS CELL IN ORDER TO IMPORT YOUR KAGGLE DATA SOURCES
# TO THE CORRECT LOCATION (/kaggle/input) IN YOUR NOTEBOOK,
# THEN FEEL FREE TO DELETE THIS CELL.
# NOTE: THIS NOTEBOOK ENVIRONMENT DIFFERS FROM KAGGLE'S PYTHON
# ENVIRONMENT SO THERE MAY BE MISSING LIBRARIES USED BY YOUR
# NOTEBOOK.

import os
import sys
from tempfile import NamedTemporaryFile
from urllib.request import urlopen
from urllib.parse import unquote, urlparse
from urllib.error import HTTPError
from zipfile import ZipFile
import tarfile
import shutil

CHUNK_SIZE = 40960
DATA_SOURCE_MAPPING = 'imdb-india-movies:https%3A%2F%2Fstorage.googleapis.com%2Fkaggle-data-sets%2F1416444%2F2346296%2Fbundle%2Farchive.zip%3FX-Goog-Algorithm%3DGOOG4-RSA-SHA256%26X-Goog-Credential%3Dgcp-kaggle-com%2540kaggle-161607.iam.gserviceaccount.com%252F20240807%252Fauto%252Fstorage%252Fgoog4_request%26X-Goog-Date%3D20240807T061111Z%26X-Goog-Expires%3D259200%26X-Goog-SignedHeaders%3Dhost%26X-Goog-Signature%3D26f2abcc8c3d6ee501aae97bd6e3417a49f700a71c6943f0dd2b8668e902397d25b82ad459ac8b3ef087e4f8d6826471e4d283fa77e9d15ee8bfb5bc4761ce863eb5e728c9cfd507983c0d9a37e8e554340ecea2a21395a2c4b545976ce97b8f7ac1b0e20de9b36cfa27cfce07dc5883057a73d375ed1f3cbad3d970e8cd6901a548b26a75ffce4f79304d9d704bc1334250a2f58193bed78e3e25686929ed4ce5e821afa53271d08d3018ed27bedba4977ddef6047d929d2e6897a6b363c938a01972d87a84eec1f4823fae732e44b318190f6fee3fb5027f6ebdabfc51803661cdfc571270812a582133c8a83133ca295093fcac72b48d9b2c2dff9a32521f'

KAGGLE_INPUT_PATH='/kaggle/input'
KAGGLE_WORKING_PATH='/kaggle/working'
KAGGLE_SYMLINK='kaggle'

!umount /kaggle/input/ 2> /dev/null
shutil.rmtree('/kaggle/input', ignore_errors=True)
os.makedirs(KAGGLE_INPUT_PATH, 0o777, exist_ok=True)
os.makedirs(KAGGLE_WORKING_PATH, 0o777, exist_ok=True)

try:
  os.symlink(KAGGLE_INPUT_PATH, os.path.join("..", 'input'), target_is_directory=True)
except FileExistsError:
  pass
try:
  os.symlink(KAGGLE_WORKING_PATH, os.path.join("..", 'working'), target_is_directory=True)
except FileExistsError:
  pass

for data_source_mapping in DATA_SOURCE_MAPPING.split(','):
    directory, download_url_encoded = data_source_mapping.split(':')
    download_url = unquote(download_url_encoded)
    filename = urlparse(download_url).path
    destination_path = os.path.join(KAGGLE_INPUT_PATH, directory)
    try:
        with urlopen(download_url) as fileres, NamedTemporaryFile() as tfile:
            total_length = fileres.headers['content-length']
            print(f'Downloading {directory}, {total_length} bytes compressed')
            dl = 0
            data = fileres.read(CHUNK_SIZE)
            while len(data) > 0:
                dl += len(data)
                tfile.write(data)
                done = int(50 * dl / int(total_length))
                sys.stdout.write(f"\r[{'=' * done}{' ' * (50-done)}] {dl} bytes downloaded")
                sys.stdout.flush()
                data = fileres.read(CHUNK_SIZE)
            if filename.endswith('.zip'):
              with ZipFile(tfile) as zfile:
                zfile.extractall(destination_path)
            else:
              with tarfile.open(tfile.name) as tarfile:
                tarfile.extractall(destination_path)
            print(f'\nDownloaded and uncompressed: {directory}')
    except HTTPError as e:
        print(f'Failed to load (likely expired) {download_url} to path {destination_path}')
        continue
    except OSError as e:
        print(f'Failed to load {download_url} to path {destination_path}')
        continue

print('Data source import complete.')

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error,r2_score
from xgboost import XGBRegressor
import optuna
import shap
from sklearn.preprocessing import LabelEncoder
from sklearn.preprocessing import MinMaxScaler, StandardScaler

plt.style.use("ggplot")

import warnings
warnings.filterwarnings("ignore")

df = pd.read_csv('/kaggle/input/imdb-india-movies/IMDb Movies India.csv',encoding='ISO-8859-1').drop(columns='Name')

df.dropna(inplace=True)

df.head()

# Find info about the columns
print(df.shape)
print("-"*60)
print(df.isna().sum())
print("-"*60)
print(df.duplicated().sum())
print("-"*60)
df.info()

df.nunique()

# Function to plot pie chart
def plot_pie_chart(column):
    plt.figure(figsize=(8, 8))
    df[column].value_counts().head(10).plot.pie(autopct='%1.1f%%', startangle=90, colors=sns.color_palette('pastel'), wedgeprops=dict(width=0.3))
    plt.title(f'Distribution of {column}')
    plt.ylabel('')
    plt.show()


def plot_hist_chart(column):
    plt.figure(figsize=(10, 5))
    df[column].hist()
    plt.title(f'{column} Distribution')
    plt.xlabel('Index')
    plt.ylabel(column)
    plt.show()

# Plotting for each column
for col in df.columns:
    if df[col].dtype == 'object':
        plot_pie_chart(col)
    else:
        plot_hist_chart(col)

# Remove () and convert dtype if year to int
df['Year'] = df['Year'].str.replace('(','')
df['Year'] = df['Year'].str.replace(')','').astype(int)

df['Duration'] = df['Duration'].str.split(' ',expand=True)[0].astype(float)

df['Votes'] = df['Votes'].str.replace(',','').astype(int)

df

director_avg_rating = {}
for index, row in df.iterrows():
    director = row['Director']
    rating = row['Rating']
    if director in director_avg_rating:
        director_avg_rating[director]['sum'] += rating
        director_avg_rating[director]['count'] += 1
    else:
        director_avg_rating[director] = {'sum': rating, 'count': 1}

df['Director Average Rating'] = df['Director'].apply(lambda x: director_avg_rating[x]['sum'] / director_avg_rating[x]['count'])

# add a column ''ead actor average rating'
actor_avg_rating = {}
for index, row in df.iterrows():
    actors = row['Actor 1'].split(', ')
    rating = row['Rating']
    for actor in actors:
        if actor in actor_avg_rating:
            actor_avg_rating[actor]['sum'] += rating
            actor_avg_rating[actor]['count'] += 1
        else:
            actor_avg_rating[actor] = {'sum': rating, 'count': 1}

def calculate_lead_actor_average(row):
    actors = row['Actor 1'].split(', ')
    lead_actor_ratings = [actor_avg_rating[actor]['sum'] / actor_avg_rating[actor]['count'] for actor in actors]
    return max(lead_actor_ratings)

df['Lead Actor Average Rating'] = df.apply(calculate_lead_actor_average, axis=1)

df['Genre1'] = df.Genre.str.split(',',expand=True)[0]
df['Genre2'] = df.Genre.str.split(',',expand=True)[1]
df['Genre3'] = df.Genre.str.split(',',expand=True)[2]

df = df.drop(columns=['Genre','Director','Actor 1','Actor 2','Actor 3'])

df.shape[0]

print(df.shape)
print(df.isna().sum())
df = df.fillna(0)

for i in df.index:
    if df.at[i, 'Genre2'] == 0:
        df.at[i, 'Genre2'] = df.at[i, 'Genre1']
    elif df.at[i, 'Genre3'] == 0:
        df.at[i, 'Genre3'] = df.at[i, 'Genre2']
print(df.isna().sum())

df.info()

for col in ['Genre1', 'Genre2', 'Genre3']:
    df[col], _ = pd.factorize(df[col])

df.head()

target = 'Rating'
X = df.drop(columns=[target,'Duration'])
y = df[target]

scaler = MinMaxScaler()
X = scaler.fit_transform(X)

X_train,X_test,y_train,y_test = train_test_split(X,y,test_size=0.2)

# Define objective function for Optuna
def objective(trial):
    # Define hyperparameters to search
    param = {
        'n_estimators': trial.suggest_int('n_estimators', 300, 1000),
        'max_depth': trial.suggest_int('max_depth', 3, 10),
        'learning_rate': trial.suggest_float('learning_rate', 0.01, 0.1),
        'subsample': trial.suggest_float('subsample', 0.6, 1.0),
        'colsample_bytree': trial.suggest_float('colsample_bytree', 0.6, 1.0),
        'reg_alpha': trial.suggest_float('reg_alpha', 0, 10),
        'reg_lambda': trial.suggest_float('reg_lambda', 0, 10),
        'verbosity': 0,
    }

    xgb = XGBRegressor(**param)

    # Fit the model on training data
    xgb.fit(X_train, y_train)

    # Predict on the validation set
    y_pred = xgb.predict(X_test)

    r2 = r2_score(y_test, y_pred)

    return r2

# Perform hyperparameter optimization using Optuna
study = optuna.create_study(direction='maximize')
study.optimize(objective, n_trials=50)

# Print the best trial and parameters found
print("Best trial:")
best_trial = study.best_trial
print(f"  Value: {best_trial.value}")
print("  Params: ")
for key, value in best_trial.params.items():
    print(f"    {key}: {value}")

# Use the best parameters to train the final model
best_params = best_trial.params

xgb_normal = XGBRegressor(**best_params)


xgb_normal.fit(X_train, y_train,eval_set=[(X_train, y_train), (X_test,y_test)],verbose=0)

# Make predictions on the test set
y_pred_test = xgb_normal.predict(X_test)

mae = mean_absolute_error(y_test,y_pred_test)


print("Test MAE:",mae )

results = xgb_normal.evals_result()
val_rmse = results["validation_1"]['rmse']
best_epopch = min(val_rmse)
i_best_epoch = val_rmse.index(best_epopch)
epochs = len(results['validation_0']['rmse'])
x_axis = range(0, epochs)

# plot m log loss
fig, ax = plt.subplots()
ax.plot(x_axis, results['validation_0']['rmse'], label='Train')
ax.plot(x_axis, results['validation_1']['rmse'], label='Test')
ax.plot(i_best_epoch, best_epopch, marker="o", color="green", label="Best")
ax.legend()
plt.ylabel('rmse')
plt.title('XGBoost rmse')
plt.show()

plt.scatter(y_test, y_pred_test, alpha=0.7, label='Real')
plt.plot([y_test.min(), y_test.max()],[y_test.min(), y_test.max()], '--', c='.3')
plt.xlabel('Actual Values')
plt.ylabel('Predicted Values')
plt.title('Scatter Plot XGBoost Model')
plt.show()

residuals = y_test - y_pred_test
plt.scatter(y_test, residuals, label='Residuals', alpha=0.7)
plt.axhline(y=0, color='red', linestyle='--', label='Zero Residuals')
plt.xlabel('Actual Values')
plt.ylabel('Residuals')
plt.title('Residual Plot for XGBoost')
plt.legend()
plt.show()

# Optianing the most features that had an impact of our price
def plot_feature_importance(model, feature_names=None, plot=True):

    feature_importance = model.feature_importances_

    if feature_names is None:
        feature_names = model.feature_name()

    feature_importance_df = pd.DataFrame({'Feature': feature_names, 'Importance': feature_importance})

    feature_importance_df = feature_importance_df.sort_values(by='Importance', ascending=False)

    if plot:
        plt.figure(figsize=(10, 10))
        sns.barplot(x='Importance', y='Feature', data=feature_importance_df)
        plt.title('Feature Importance')
        plt.show()

    return feature_importance_df

feature_importance_df = plot_feature_importance(xgb_normal,feature_names=df.drop(columns=[target,'Duration']).columns)