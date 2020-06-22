import os
import numpy as np
import pandas as pd 
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Embedding, LSTM, Dense, Dropout
from time import strptime
from math import ceil
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
from sklearn.preprocessing import MinMaxScaler 

# Load data 
file = r'DJIA_historical' + '.csv'
dirname = os.path.dirname(__file__)
filename = os.path.join((dirname), 'data/' +file)
df = pd.read_csv(filename)

# Visualize the total dataset
data = df['Close']
dates = df['Date']
adj_dates = mdates.datestr2num(dates)
plt.plot_date(adj_dates, data, '-')
    
plt.title('DJIA Close vs. Date, 1985-2020')
plt.xlabel('Date', fontsize=18)
plt.ylabel('Close value', fontsize=16)
plt.show()

# Check for, and handle, missing values 
if data.isna().sum():
    print('Alert! Missing data')
    # do something to handle empty data rows 
    
# Define the training set
percent_training = 0.80
num_training_samples = ceil(percent_training*len(df)) # 7135
training_set = df.iloc[:num_training_samples, 5:6].values

# Scale training data
scaler = MinMaxScaler(feature_range = (0, 1))
training_set_scaled = scaler.fit_transform(training_set)

# Some parameters
sequence_length = 30

# Build x and y components 
x_train = np.array([training_set_scaled[i - sequence_length:i, 0] for i in range(sequence_length, len(training_set_scaled))])
y_train = np.array([training_set_scaled[i, 0] for i in range(sequence_length, len(training_set_scaled))])

x_train = np.reshape(x_train, (x_train.shape[0], x_train.shape[1], 1)) # (7105, 30, 1)

# Define Test Set 
num_testing_samples = len(df) - x_train.shape[0] # 1813
testing_set = df.iloc[-num_testing_samples:, 5:6].values
testing_set_scaled = scaler.fit_transform(testing_set)

x_test = np.array([testing_set_scaled[i - sequence_length:i, 0] for i in range(sequence_length, len(testing_set_scaled))])
x_test = np.reshape(x_test, (x_test.shape[0], x_test.shape[1], 1)) # (7105, 30, 1)
y_test = np.array([testing_set_scaled[i, 0] for i in range(sequence_length, len(testing_set_scaled))])

# Build model 
epochs = 100
batch_size = 32

# Describe layers
LSTM_1 = LSTM(
    units = 5, 
    input_shape = (x_train.shape[1], 1),
    return_sequences = True,
    )
# Output shape is (batch_size, steps, units)

model = Sequential()
model.add(LSTM_1)
model.add(Dropout(0.2))

model.add(LSTM(units = 14))
model.add(Dropout(0.2))

model.add(Dense(1))
model.compile(loss = 'mean_squared_error', 
             optimizer = 'adam', 
             metrics = ['accuracy']
             )

early_stopping = EarlyStopping(monitor='val_loss', 
                               mode='min', 
                               verbose=1, 
                               patience = 9,
                               restore_best_weights = False
                               )

history = model.fit(x_train,
          y_train,
          epochs = epochs, 
          batch_size = batch_size,
          verbose = 2, 
          validation_split = 0.20,
          # validation_data = (x_test, y_test),
          callbacks = [early_stopping],
          )

# Evaluate performance 
model.summary()
loss = model.evaluate(x_test, y_test, batch_size = batch_size)

print('Training stopped after',early_stopping.stopped_epoch,'epochs.')

plt.plot(history.history['accuracy'])
plt.title('Model Accuracy vs. Epoch')
plt.ylabel('accuracy')
plt.xlabel('epoch')
plt.legend(['Train', 'Test'], loc='upper left')
plt.show()

plt.plot(history.history['loss'])
plt.title('Model Loss vs. Epoch')
plt.ylabel('loss')
plt.xlabel('Epoch')
plt.legend(['Train', 'Test'], loc='upper left')
plt.show()

prediction = model.predict(x_test)
prediction = scaler.inverse_transform(prediction)

y_test2 = np.reshape(y_test, (y_test.shape[0], 1))
y_test = scaler.inverse_transform(y_test2)

test_dates = adj_dates[-1783:]

# Visualizing the results
plt.plot_date(test_dates, y_test, '-', linewidth = 2, color = 'red', label = 'Real DJIA Close')
plt.plot(test_dates, prediction, color = 'blue', label = 'Predicted Close')
plt.title('Close Prediction')
plt.xlabel('Time')
plt.ylabel('DJIA Close')
plt.legend()
plt.show()













