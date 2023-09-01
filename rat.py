from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
import numpy as np
import pandas as pd
from math import sqrt
import random

ratings_df = pd.read_csv('ratings.csv')

n = 75000
ratings_df_sample = ratings_df[:n]
n_users = len(ratings_df_sample["userId"].unique())
n_movies = len(ratings_df_sample["movieId"].unique())

movies = ratings_df_sample["movieId"].unique()

def scale_movie_id(movie_id):
    scaled = np.where(movie_ids == movie_id)[0][0] + 1
    return scaled
    ratings_df_sample["movieId"] = ratings_df_sample["movieId"].apply(scale_movie_id)

train_dataset, test_dataset = train_test_split(ratings_df_sample, test_size=0.25)

example = random.shuffle(ratings_df_sample[:50000])

def rmse(prediction, ground_truth):
    prediction = np.nan_to_num(prediction)[ground_truth.nonzero()].flatten()
    ground_truth = np.nan_to_num(ground_truth)[ground_truth.nonzero()].flatten()
    mse = mean_squared_error(prediction, ground_truth)
    return sqrt(mse)

train_data_matrix = np.zeros((n_users, n_movies))
for line in train_dataset.itertuples():
    train_data_matrix[line[1]-1, line[2]-1] = line[3]

test_data_matrix = np.zeros((n_users, n_movies))
for line in test_dataset.itertuples():
    test_data_matrix[line[1]-1, line[2]-1] = line[3]

movies_df = pd.read_csv("movies.csv")
data_df = pd.merge(ratings_df, movies_df, on="movieId")
data_df.drop("timestamp", 1, inplace=True)

#средний рейтинг
data_df.groupby("title")["rating"].mean().sort_values(ascending=False).head()

#общий рейтинг
data_df.groupby("title")["rating"].count().sort_values(ascending=False).head()

ratings = pd.DataFrame(data_df.groupby("title")["rating"].mean())
ratings['num'] = pd.DataFrame(data_df.groupby("title")["rating"].count())

import matplotlib.pyplot as plt
import seaborn as sns

sns.set_style("white")
plt.figure(figsize=(10, 4))
ratings["num"].hist(bins=70)

plt.figure(figsize=(10, 4))
ratings["rating"].hist(bins=70)

moviemat = data_df.pivot_table(index="userId", columns="title", values="rating")
moviemat.head()
ratings.sort_values("num", ascending=False).head(10)

starwars_user_ratings = 0 #че то
similar_to_starwars = moviemat.corrwith(starwars_user_ratings)
corr_starwars = pd.DataFrame(similar_to_starwars) #и тут дописать

corr_starwars.sort_values("Correlation", ascending=False).head(10)
corr_starwars = corr_starwars.join(ratings["num"])
corr_starwars[corr_starwars["num"]>100].sort_values("Correlation", ascending=False).head(10)

