'''
LSTM regression on Lotka Volterra System 
'''
import numpy as np
import pickle
import matplotlib.pyplot as plt

#Keras imports
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM
from tensorflow.keras.layers import Dense
from tensorflow.keras.callbacks import ModelCheckpoint

seed=1
np.random.seed(seed)

class Lotka_Volterra(object):
    def __init__(self,shift=1,sequence_length=12,sample_size=2000,hidden_lstm=6,Dense_output=2,n_steps=12,n_features=2,epochs=250):
        '''
        Initialize Lotka_Volterra Class

        Parameters
        ----------
        shift : Integer
            Number of steps to be predicted into the future.
        pred_mode : Integer
            Mode to be forecasted, Predator or Pray population.
        sequence_length: Integer
            Window size provided as input.
        hidden_lstm : Integer
            Number of hidden units in the LSTM layer.
        Dense_output : Integer
            Number of output dimensions for the Dense Layer.
        n_steps : Integer
            Window size of an input sample.
        n_features : Integer
            Number of Input Dimensions.
        epochs : Integer
            Number of training epochs.         
        '''
        #Data Parameters
        self.shift = shift
        self.sequence_length = sequence_length
        self.sample_size=sample_size
        #LSTM Parameters
        self.hidden_lstm=hidden_lstm
        self.Dense_output=Dense_output
        self.n_steps=n_steps
        self.n_features=n_features
        self.epochs=epochs
        #load data
        self.load_data()
        
        
        
    def load_data(self):
        '''
        Load Lotka-Volterra Data (generated by the script Lotka_volterra_data.py)
        and create input sequences and training data.
        Assign data to the self.data attribute of the class.
        '''    
        #shift =1 for one step ahead prediction
        total_length=self.sequence_length+self.shift
    
        data = pickle.load(open("./Data/Lotka_Volterra2.p", "rb"))
    
        #create sequences with length sequence_length
        result = []
        for index in range(len(data) - total_length):
            
            i=data[index: index + total_length]
            k=i[:self.sequence_length]
            j=np.array(i[total_length-1])
            j=j.reshape(1,2)
            k=np.append(k,j,axis=0)
            result.append(k)
            
        result = np.array(result) 
        
        #reshape (#Timesteps,seq_length,#modes)
        
        result=result.reshape(result.shape[0],result.shape[1],2)
        
        train_end=int(0.8*len(result))
        res_train=result[:train_end]
        res_test=result[train_end:]
    
        #sample_size
        valid=int(0.8*self.sample_size)
        Input_data=res_train[:self.sample_size,:self.sequence_length,:]
        Output_data=res_train[:self.sample_size,-1,:]
        
        Input_data_test=res_test[:int(self.sample_size/3),:self.sequence_length,:] 
        Output_data_test=res_test[:int(self.sample_size/3),-1,:]  
        X_train=Input_data[:valid,:,:]
        y_training=Output_data[:valid]
        
        X_test=Input_data_test[:,:]
        y_testing=Output_data_test[:]
        
        X_valid=Input_data[valid:,:,:]
        y_validation=Output_data[valid:] 
        
        #Reshape targets
        
        y_train=y_training.reshape(y_training.shape[0],2)
        y_test=y_testing.reshape(y_testing.shape[0],2)
        y_valid=y_validation.reshape(y_validation.shape[0],2)
        
        
        data = {
            'train': [X_train, y_train],
            'valid': [X_valid, y_valid],
            'test': [X_test, y_test],
        }
        self.data=data
    
    def build_train_lstm(self):
        '''
        Function that builds, trains and evaluates an LSTM
        
        Returns
        -------
        model : Optimized Model
            Trained and optimized LSTM model.
        history : Dictionnary
            Dictionnary containing the training history.
        score:Dictionnary
            Dictionnary that contains the model evaluation score.
        '''
        checkpoint = ModelCheckpoint('best_LV_LSTM.h5', verbose=1, monitor='val_loss',save_best_only=True, mode='auto')  
        model = Sequential()
        model.add(LSTM(self.hidden_lstm, activation='relu', input_shape=(self.n_steps, self.n_features)))
        model.add(Dense(self.Dense_output))
        model.compile(optimizer='adam', loss='mse')
        # fit model
        data=self.data
        history = model.fit(data['train'][0], data['train'][1],validation_data=(data['valid'][0], data['valid'][1]), epochs=self.epochs, verbose=2,callbacks=[checkpoint])

        # Generate generalization metrics
        score = model.evaluate(data['test'][0], data['test'][1], verbose=1)
    
        return model,history,score











