# As usual, a bit of setup

import numpy as np
from classifier_trainer import ClassifierTrainer
from gradient_check import eval_numerical_gradient
from classifiers.convnet import *

def rel_error(x, y):
  """ returns relative error """
  return np.max(np.abs(x - y) / (np.maximum(1e-8, np.abs(x) + np.abs(y))))
  

from data_utils import load_train_data

def get_train_data(num_training=29336, num_validation=1000, num_test=1000):
	print 'Getting Training Data'
	"""
	Load the dataset from disk and perform preprocessing to prepare
	it for the classifier.  
	"""
	# Load the raw data
	X_train, y_train = load_train_data('train_datadict_initial')
		
	# Subsample the data
	mask = range(num_training, num_training + num_validation)
	X_val = X_train[mask]
	y_val = y_train[mask]
	mask = range(num_training)
	X_train = X_train[mask]
	y_train = y_train[mask]
	#mask = range(num_test)
	#X_test = X_test[mask]
	#y_test = y_test[mask]

	print 'Normalize data'
	# Normalize the data: subtract the mean image
	mean_image = np.mean(X_train, axis=0)
	X_train -= mean_image
	X_val -= mean_image
	#X_test -= mean_image

	# Transpose so that channels come first
	#X_train = X_train.transpose(0, 3, 1, 2).copy()
	#X_val = X_val.transpose(0, 3, 1, 2).copy()
	#x_test = X_test.transpose(0, 3, 1, 2).copy()

	return X_train, y_train, X_val, y_val


# Invoke the above function to get our data.
X_train, y_train, X_val, y_val = get_train_data()
print 'Train data shape: ', X_train.shape
print 'Train labels shape: ', y_train.shape
print 'Validation data shape: ', X_val.shape
print 'Validation labels shape: ', y_val.shape
#print 'Test data shape: ', X_test.shape
#print 'Test labels shape: ', y_test.shape


# Use a two-layer ConvNet to overfit 50 training examples.
print 'Overfit small data'
model = init_two_layer_convnet()
trainer = ClassifierTrainer()
best_model, loss_history, train_acc_history, val_acc_history = trainer.train(
          X_train[:50], y_train[:50], X_val, y_val, model, two_layer_convnet,
          reg=0.001, momentum=0.9, learning_rate=0.0001, batch_size=10, num_epochs=10,
          verbose=True)
		  
  
reg = [1e-4, 1e-3, 2e-3]
lrates = [1e-3]
best_val = 0
ensemble_model = None #ensemble
first = True
num_models = 0

#initialize outside for "hot start" between iterations
model = init_custom_convnet(filter_size=3, num_filters=32)
trainer = ClassifierTrainer()
for lr in lrates:
    for r in reg:
        print lr, r
        best_model, loss_history, train_acc_history, val_acc_history = trainer.train(
                  X_train, y_train, X_val, y_val, model, custom_convnet,
                  reg=r, momentum=0.90, learning_rate=lr, batch_size=50, num_epochs = 2, acc_frequency=50, verbose=True)
        if first:
            ensemble_model = best_model
            first = False            
            num_models+=1
        else:
            ensemble_model['W1'] += best_model['W1']
            ensemble_model['b1'] += best_model['b1']
            ensemble_model['W2'] += best_model['W2']
            ensemble_model['b2'] += best_model['b2']
            ensemble_model['W3'] += best_model['W3']
            ensemble_model['b3'] += best_model['b3']
            
            num_models+=1
#average models for ensemble        
ensemble_model['W1'] /= num_models
ensemble_model['b1'] /= num_models
ensemble_model['W2'] /= num_models
ensemble_model['b2'] /= num_models
ensemble_model['W3'] /= num_models
ensemble_model['b3'] /= num_models

# evaluate val accuracy
scores_val = custom_convnet(X_val, ensemble_model)
y_pred_val = np.argmax(scores_val, axis=1)
val = np.mean(y_pred_val ==  y_val)

print "Ensemble val acc: ", val 
