import tensorflow as tf
from tensorflow import keras
from keras.models import Sequential
from keras.layers import Dense
import matplotlib.pyplot as plt
import numpy
# load pima indians dataset
def deep_learning(df, feature_cols, layer_one_nodes):
    # split into input (X) and output (Y) variables
    X = df[feature_cols]
    Y = df.label
    # Adding layers of neuron machine learning.
    # Every add command adds another layer of nouerons
    model = Sequential()
    model.add(Dense(layer_one_nodes, input_dim=len(feature_cols), activation='relu'))
    model.add(Dense(int(layer_one_nodes - 0.25*layer_one_nodes), activation='relu'))
    model.add(Dense(1, activation='sigmoid'))
    # Compile model  
    model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
    # Fit the model - Epoach number of time the Deeo learning runs on training and batch is the number of rows that after i'll update
    history = model.fit(X, Y, validation_split=0.33, epochs=150, batch_size=10, verbose=0)
    # list all data in history
    print(history.history.keys())
    # summarize history for accuracy
    plt.plot(history.history['accuracy'])
    plt.plot(history.history['val_accuracy'])
    plt.title('model accuracy')
    plt.ylabel('accuracy')
    plt.xlabel('epoch')
    plt.legend(['train', 'test'], loc='upper left')
    plt.show()
    # summarize history for loss
    plt.plot(history.history['loss'])
    plt.plot(history.history['val_loss'])
    plt.title('model loss')
    plt.ylabel('loss')
    plt.xlabel('epoch')
    plt.legend(['train', 'test'], loc='upper left')
    plt.show()
