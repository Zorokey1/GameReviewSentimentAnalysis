import tensorflow as tf
import pandas as pd
import numpy as np
import tensorflow_datasets as tfds

from tensorflow.python import keras, data
from keras import layers, losses, metrics

data_path = "./data/reviews.csv"
raw_data_tf = tf.data.experimental.make_csv_dataset(
    data_path,
    batch_size=32,
    select_columns=['Review', 'Score'],
    label_name='Score',
    num_epochs=1,
    shuffle=False,
    encoding="UTF-8")

def is_test(x, y):
    return x % 10 == 7

def is_train(x, y):
    return x % 10 < 7

def is_val(x,y):
    return x % 10 > 7


raw_data_tf.shuffle(322652, seed=5, reshuffle_each_iteration=False)

recover = lambda x,y: y

train_dataset_tf = raw_data_tf.enumerate().filter(is_train).map(recover)
test_dataset_tf = raw_data_tf.enumerate().filter(is_test).map(recover)
val_dataset_tf = raw_data_tf.enumerate().filter(is_val).map(recover)

AUTOTUNE = tf.data.AUTOTUNE

max_features = 10000
sequence_length = 2000


vectorize_layer = tf.keras.layers.TextVectorization(
    standardize="lower_and_strip_punctuation",
    max_tokens=max_features,
    output_mode='int',
    output_sequence_length=sequence_length)


vectorize_layer.adapt(train_dataset_tf.map(lambda x,y: x['Review']))


def preprocess(x):
    return vectorize_layer(x)


train_dataset_tf = train_dataset_tf.map(lambda x,y: (x['Review'],y)).cache().prefetch(buffer_size=AUTOTUNE)
test_dataset_tf = test_dataset_tf.map(lambda x,y: (x['Review'],y)).cache().prefetch(buffer_size=AUTOTUNE)
val_dataset_tf = val_dataset_tf.map(lambda x,y: (x['Review'],y)).cache().prefetch(buffer_size=AUTOTUNE)

model = tf.keras.Sequential([
    vectorize_layer,
    layers.Embedding(max_features,64),
    layers.Dropout(0.2),
    layers.GlobalAveragePooling1D(),
    layers.Dropout(0.2),
    layers.Dense(1, activation='relu')])

model.summary()

model.compile(loss=losses.MeanSquaredError(),
              optimizer='adam',
              metrics=metrics.MeanSquaredError())

history = model.fit(
    train_dataset_tf,
    validation_data=val_dataset_tf,
    epochs=1,
    steps_per_epoch=2000
)

loss, accuracy = model.evaluate(test_dataset_tf)

print("Loss: ", loss)
print("Accuracy: ", accuracy)

test_reviews = ['This was an awesome game that I did not expect to be this good',
                'This game was the worst I have ever seen in my life. I wouldnt recommend this to not even my worst enemy',
                'Legend of Brinko was an okay game that could have done better, but it wasnt bad']

print(model.predict(test_reviews))

model.save('./models/my_model.keras')


print("done")

