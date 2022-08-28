# -*- coding: utf-8 -*-
"""Submission3_Image_Classification_TensorLite.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1kCbzQdsXdQVIVv35qakgNqtY5nqsqkaW
"""

from google.colab import drive
drive.mount('/content/drive')

# Commented out IPython magic to ensure Python compatibility.
# %cd /content/drive/MyDrive/Dicoding_Machine_Learning_2/Submission3

import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator

dir = 'cardataset'
train_datagen = ImageDataGenerator(
    rescale = 1.0/255.0,
    validation_split=0.2
)

train_generator = train_datagen.flow_from_directory(
    dir,
    target_size=(150,150),
    batch_size=32,
    class_mode='categorical',
    subset='training'
)

validation_generator = train_datagen.flow_from_directory(
    dir,
    target_size=(150,150),
    batch_size=32,
    class_mode='categorical',
    subset='validation'
)

import tensorflow as tf
from tensorflow.keras.layers import Input

base_model = tf.keras.applications.vgg16.VGG16(
    input_tensor=Input(shape=(150,150,3)),
    include_top=False,
    weights='imagenet'
)
for layer in base_model.layers:
    layer.trainable = False

prediction_layer = tf.keras.layers.Dense(3, activation='softmax')

#arsitektur VGG16 sudah mengandung conv2d dan maxpool
model = tf.keras.Sequential([
  base_model,
  tf.keras.layers.Flatten(),
  tf.keras.layers.Dense(256, activation='relu'),
  tf.keras.layers.Dropout(0.2),
  tf.keras.layers.Dense(128, activation='relu'),
  prediction_layer
])
model.summary()
model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=0.01),
              loss=tf.keras.losses.CategoricalCrossentropy(),
              metrics=['accuracy'])

class myCallbacks(tf.keras.callbacks.Callback):
  def on_epoch_end(self, epoch, logs={}):
    if(logs.get('accuracy')>0.92 and logs.get('val_accuracy')>0.92):
      print('Akurasi Tercapai')
      self.model.stop_training = True
callback = myCallbacks()

with tf.device('/GPU:0'):
  history = model.fit(
    train_generator,
    validation_data=validation_generator,
    epochs=40,
    steps_per_epoch=128,
    batch_size=64,
    callbacks=[callback],
    verbose=2
    )

export_dir = 'trained_model/'
tf.saved_model.save(model, export_dir)

import matplotlib.pyplot as plt

plt.plot(history.history['accuracy'])
plt.plot(history.history['val_accuracy'])
plt.title('Plot Akurasi')
plt.ylabel('accuracy')
plt.xlabel('epoch')
plt.legend(['train', 'val'], loc='upper left')
plt.show()

plt.plot(history.history['loss'])
plt.plot(history.history['val_loss'])
plt.title('Plot Akurasi')
plt.ylabel('accuracy')
plt.xlabel('epoch')
plt.legend(['train', 'val'], loc='upper left')
plt.show()

import pathlib
converter = tf.lite.TFLiteConverter.from_saved_model(export_dir)
tflite_model = converter.convert()
 
tflite_model_file = pathlib.Path('model.tflite')
tflite_model_file.write_bytes(tflite_model)