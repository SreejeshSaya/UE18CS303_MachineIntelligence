'''
TITLE: Neural Network from Scratch
AUTHORS:
    Vishesh P PES1201800314
    Sreejesh Saya PES1201800293
    Pavan A PES1201800157

Design of a Neural Network from scratch [TODO]

**************************
Mention hyperparameters used and describe functionality in detail in this space

* alpha
    Also known as learning rate, alpha specifies what portion of the gradient to consider while updating the weights
    after each epoch. It can also be visualised, graphically, as the size of step taken in an attempt to reach
    the global minima.
    A large learning rate implies, greater probabilities of missing the global minima
    A small learning rate implies, greater probabilities of reaching the global minima
'''

# Importing the modules
#     pandas: access data in the form of panda dataframe for normalization and training and testing data
#     numpy: perform matrix operations for weight and biases
#     sklearn: Splitting of training and testing data ONLY
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split

class NN:
    def __init__(self, layers, alpha, epoch, activation = 'relu'):
        ''' Initialising the required variables for the neural network. '''

        # Weights biases for every layer stored in a dictionary in the form of a numpy matrix 
        self.params = dict() 

        # Dictionary containing all the Z's and A's of every layer.
        #   Z[i] = W[i].T*A[i-1] + b[i] [TODO]
        #   A[i] = activation(Z[i])
        self.AandZ = dict()  # [TODO NAME CHANGE]

        # Stores the gradients of the weights for all the layers in a dictionary.
        self.grads = dict() 

        #List of values of the form [9, n, 1] where 
            # 9 is the number of input features
            # n is the set of values where each value represents the number of neurons in that specific layer.
            # 1 is the output layer consisting of one neuron (output is either a 0 or 1)
        self.layers = layers 

        # Choosing activation function for all hidden layers (for simplicity reasons) 
        if(activation == 'relu'):
            self.activation = activation
            self.der_activation = 'der_relu'
        elif(activation == 'tanh'):
            self.activation = activation
            self.der_activation = 'der_tanh'

        for i in range(1, len(layers)):
            np.random.seed(0)            
            self.params[f"W{i}"] = np.random.randn(self.layers[i], self.layers[i-1]) * np.sqrt(1/self.layers[i-1])
            # Weights initialised randomly in numpy matrices of the order (n[l], n[l-1]) where 
            # n[l] is the number of neurons in current layer
            # n[l-1] is the number of neurons in previous layer
            # Xavier initialisation method also implemented along with random initialisation to avoid exploding/vanishing gradients.

            # Biases are initialised randomly in numpy vectors of length n[l].
            self.params[f"b{i}"] = np.random.randn(self.layers[i], 1)

            # Dictionary containing the gradients of the weights and biases(of every layer).
            self.grads[f"dW{i}"] = 0 
            self.grads[f"db{i}"] = 0

        self.alpha = alpha # Learning rate.
        self.epoch = epoch # Number of epochs for training the model
        self.X = None # Matrix of features of the training set
        self.y = None # Vector of target variable values.        
        
    # Given a numpy array x, apply the sigmoid function for every element in x
    def sigmoid(self, x):
        return 1/(1 + np.exp(-x))
    
    # Given a numpy array x, apply the reLU function for every element in x
    def relu(self, x):
        return np.maximum(0,x)
    
    # Given a numpy array x, apply tanH function for every element in x.
    def tanh(self, x):
        return np.tanh(x)
    
    # Returns the derivative of the tanh function.
    def der_tanh(self, x):
        return (1 - np.square(self.tanh(x)))
    
    # Returns the derivative of the ReLU function.
    def der_relu(self, x):
        return ((x > 0) * 1) # [TODO]
    
    def callback(self,  x):
        """
        Calls the respective activation function as specified by the user, set under __init__
        default activation function = relu
        Returns a value inturn returned by the activation function
        """    
        if(self.activation == 'relu'):
            return self.relu(x)
        elif(self.activation == 'tanh'):
            return self.tanh(x)
        
    def der_callback(self, x):
        """
        Calls the respective deravative_activation function, which was set implicitly based on activation set by user, set under __init__
        default activation function = der_relu
        Returns a value inturn returned by the der_activation function
        """  
        if(self.der_activation == 'der_relu'):
            return self.der_relu(x)
        elif(self.der_activation == 'der_tanh'):
            return self.der_tanh(x)
       
    
    def forward_propagation(self):
        '''
        The sample inputs are provided to the neural network and at each layer, preactivation and activation steps are performed and
        we get the predicted values for all sample inputs. 
        The loss is computed which is used to perform back propagation.

        Returns
        -------
        yhat : Vector of values corresponding to provided inputs X
        loss : Numerical value representing the loss function signifying the strength of the neural network.
        '''

        # Setting A0 to be the matrix of features X, for simplicity
        self.AandZ["A0"] = self.X

        # L2 regularisation = (lambda)*[ sigma( w[i]*w[i] )]
        # Reg_weights = [sigma( w[i]*w[i] )]
        self.reg_weights = 0 
        for i in range(1, len(self.layers)):
            self.AandZ[f"Z{i}"] = self.params[f"W{i}"].dot(self.AandZ[f"A{i-1}"]) + self.params[f"b{i}"]
            # Z[i] = W[i].T*A[i-1] + b[i]
            # W[i] is the weights matrix of layer i
            # A[i-1] is the activation values of the previous layer passed as input to the current layer.
            # b[i] is the bias vector of layer i.

            # The last layer has the sigmoid activation function applied
            # All hidden layers have activation function applied which is selected when creating the NN model
            if(i!=(len(self.layers)-1)):
                # A[i] is the activation of Z[i] , where i refers to a particular layer.
                # the callback function returns the respective output of the activation function requested by the user.
                self.AandZ[f"A{i}"] = self.callback(self.AandZ[f"Z{i}"])
            else:
                # yhat is the vector of predicted values for each vector in matrix X.
                # The activation function of the output layer is sigmoid to retrieve a value between 0 and 1 for the entire vector yhat.
                yhat = self.sigmoid(self.AandZ[f"Z{i}"])

            self.reg_weights += np.sum(np.square(self.params[f"W{i}"]))

        m = len(self.y) # Number of records 

        # L2 Regularization
        self.lamda = 1
        self.l2_reg = (self.lamda/(2*m)) * self.reg_weights
        try:
            # Loss function : Cross entropy. 
            # The loss is calculated after predicting the values for the entire training set (Batch processing).
            # L2 regularization combined with the loss function to prevent overfitting.
        	# Cross entropy loss with l2_regularizer
        	loss = -(1/m) * (np.sum(np.multiply(np.log(yhat), self.y) + np.multiply((1 - self.y), np.log(1 - yhat)))) - self.l2_reg
        except ZeroDivisionError:
        	print("ZeroDivisionError encountered while calculating loss. Run again.")

        return yhat, loss
                
            
    def backward_propagation(self, yhat): # [TODO]
        '''
        Backward propagation is an algorithm which uses gradient descent to tweak the weights and biases of each neuron in every layer.
        Given a neural network and an error function, this algorithm determines the gradient of the error function with respect to
                    i. the neural network's weights which is multiplied with the learning rate and together subtracted from the original weights' values
                    ii. the biases of the neurons in each layer which is multiplied with the learning rate and together subtracted from the original biases' values
                    
        The gradient of the error function with respect to the Activations of layer i is of the form
                dA[i]
        The gradient of the error function with  respect to the Linear Combiations(Z) of each layer i is of the form
                dZ[i]
        The gradient of the error function with  respect to the Weights of each layer i is of the form
                dW[i]
        The gradients of the error function with respect to the Biases of each layer is of the form
                db[i]
                
        The formulae to determine the above mentioned variables are specified below.
        
        '''
    
        m = len(self.y) # Size of the vector of actual values.
        self.grads[f"dA{len(self.layers)-1}"] = -(np.divide(self.y,yhat) - np.divide((1 - self.y),(1-yhat))) - ((self.lamda * self.reg_weights)/m)
        #The gradient of the Error function with respect to the Activation of the last layer is implemented separately in the previous line. 
                      
        for i in range(len(self.layers)-1, 0, -1): #Iterating through each layer 
            if(i ==(len(self.layers)-1) ):
                sig = self.sigmoid(self.AandZ[f"Z{i}"])
                self.grads[f"dZ{i}"] = self.grads[f"dA{i}"] * sig * (1-sig)
                #dZ[i] = dA[i] * act(Z[i])'
                #where act(Z[i])' is the derivative of the activation of Z[i].
            
            else:
                #der_callback calls the respective deravative_activation function set under NN.__init__ 
               self.grads[f"dZ{i}"] = self.grads[f"dA{i}"] * self.der_callback(self.AandZ[f"Z{i}"])
               #dZ[i] = dA[i] * act(Z[i])'
               #where act(Z[i])' is the derivative of the activation of Z[i].
            
            self.grads[f"dW{i}"] = (1/m) * np.dot(self.grads[f"dZ{i}"], self.AandZ[f"A{i-1}"].T)
            #dW[i] = (1/m) * (dZ[i] . A[i-1](transpose))
            
            self.grads[f"db{i}"] = (1/m) * np.sum(self.grads[f"dZ{i}"], axis = 1, keepdims = True)
            #db[i] = (1/m) * (Sum of all elements of dZ[i])
            
            self.grads[f"dA{i-1}"] = np.dot(self.params[f"W{i}"].T, self.grads[f"dZ{i}"])
            #dA[i-1] = W[i](transpose) . dZ[i]
             
            self.params[f"W{i}"] -= (self.alpha * self.grads[f"dW{i}"]) #Gradient descent
            self.params[f"b{i}"] -= (self.alpha * self.grads[f"db{i}"]) #Gradient descent

     
    ''' X and Y are dataframes '''
    def fit(self,X,Y, verbose = 0):
        '''
        Function that trains the neural network by taking x_train and y_train samples as input
        
        Batch processing implemeted in this neural network 
        i.e. all the records of the inputs are passed to the neural network before performing gradient descent.
		
        Learning-rate decay has also been implemented : At the end of every epoch, the learning rate is reduced by a factor,
        helping the loss function to converge better at the local/global minima.
        '''

        # Assigning the matrix of features X to self.X.       
        self.X = X.values.T
        # Assigning the vector of values y containing the target variable values, which will be later used to compute the loss.
        self.y = Y.values

        for i in range(self.epoch):
            # If verbose is set to 1, epoch number and loss is displayed after every epoch
            if(verbose == 1):
            	print(f"Epoch {i+1} - ", end=" ")
            yhat, loss = self.forward_propagation() # Forward propagation
            self.backward_propagation(yhat) # Backward propagation
            if(verbose):
            	print(f"Error : {loss}")
            self.alpha = (0.9995**i) * self.alpha # Learning-rate decay.

	
    def predict(self,X):
        """
        The predict function performs a simple feed forward of weights
		and outputs yhat values 

		yhat is a list of the predicted value for df X

        """
        # A_prev represents the set of inputs obtained from the previous layer provided to the current layer's neurons.
        A_prev = X.values.T

        for i in range(1, len(self.layers)):
            # Preactivation operation performed at each layer
            z = self.params[f"W{i}"].dot(A_prev) + self.params[f"b{i}"]

            if(i!=(len(self.layers)-1)):    
                # Activation operation performed at each layer. 
                # Callback function uses the respective activation function as requested by the user.
                A_prev  = self.callback(z)
            else:
                # Sigmoid function is the dedault activation for the output layer
                # yhat is a vector containing final predicted values corresponding to all the samples in the X matrix.
                yhat = self.sigmoid(z)

        return yhat    
        
	
    def CM(self, y_test, y_test_obs):
        '''
        Prints confusion matrix 
		y_test is list of y values in the test dataset
		y_test_obs is list of y values predicted by the model
	    '''
        for i in range(len(y_test_obs)):
            if(y_test_obs[i]>0.6):
                y_test_obs[i]=1
            else:
                y_test_obs[i]=0
        
        cm=[[0,0],[0,0]]
        fp=0
        fn=0
        tp=0
        tn=0
        
        for i in range(len(y_test)):
            if(y_test[i]==1 and y_test_obs[i]==1):
                tp=tp+1
            if(y_test[i]==0 and y_test_obs[i]==0):
                tn=tn+1
            if(y_test[i]==1 and y_test_obs[i]==0):
                fp=fp+1
            if(y_test[i]==0 and y_test_obs[i]==1):
                fn=fn+1
        cm[0][0]=tn # True Negative
        cm[0][1]=fp # False Positive
        cm[1][0]=fn # False Negative
        cm[1][1]=tp # True Positive

        try:
            p= tp/(tp+fp)
            r=tp/(tp+fn)
            f1=(2*p*r)/(p+r)
            acc = (tp+tn)/(tp+tn+fp+fn)
            print("Confusion Matrix : ")
            print(cm)
            print("\n")
            print(f"Precision : {p}")
            print(f"Recall : {r}")
            print(f"F1 SCORE : {f1}")
            print(f"Accuracy score : {acc}")
        except ZeroDivisionError:
            print("ZeroDivisionError encountered while computing the confusion matrix. Run again.")
		
        
        
class Normalizer:
    def __init__(self):
        self.means = {} #dictionary - {key, value} :: {attribute_name, attribute's mean}
        self.stds = {}  #dictionary - {key, value} :: {attribute_name, attribute's standard deviation}
    
    def fit_transform(self, X_train): # X_train is a dataframe.
        self.means = X_train.mean() #calculates mean or average values for every attribute of the X_train dataframe
        self.stds = X_train.std() #calculates standard deviation values for every attribute of the X_train dataframe
        # normalization => z = (X(i) - mean)/std_deviation
        normalized_df = (X_train - self.means)/self.stds #holds the normalised datframe of X_train 
        return normalized_df
    
    def transform(self, X_test): # X_test is a dataframe.
        normalized_df = (X_test - self.means)/self.stds #normlizes X_test based on mean and standard deviation computed on X_train dataframe
        return normalized_df


        
def preprocess(df): #[TODO]
    # Compute (median/mean/mode) imputation values
    # For the null values present in the dataset, we have chosen either the mean, median or mode 
    # to fill in depending on the appropriateness of the values for the column
    medianAge = df['Age'].median()
    meanWt = int(df['Weight'].mean())
    medianDP = df.mode()['Delivery phase'][0]
    medianHB = df['HB'].median()
    meanBP = df['BP'].median()
    education = df.mode()['Education'][0]
    residence = df.mode()['Residence'][0]

    # Replace all null values with the corresponding column's imputated values (inplace)
    df['Age'].fillna(value=medianAge, inplace=True)
    df['Weight'].fillna(value=meanWt, inplace=True)
    df['Delivery phase'].fillna(value=medianDP, inplace=True)
    df['HB'].fillna(value=medianHB, inplace=True)
    df['BP'].fillna(value=meanBP, inplace=True)
    df['Education'].fillna(value=education, inplace=True)
    df['Residence'].fillna(value=residence, inplace=True)
    
def normalize(df):
    # Normalizer object to normalize the training and testing sets
    norm = Normalizer()

    # Separate the feature set and the target variable and store in X and y respectively
    target = 'Result'
    X = df.drop(target, axis=1)
    y = df[target]

    # Splitting the dataset into training set and testing set using sklearn library
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3)
    
    # Copying the df to avoid SettingWithCopy Warning - Pandas
    X_train = X_train.copy()
    X_test = X_test.copy()
    y_train = y_train.copy()
    y_test = y_test.copy()

    # Normalize the numerical values in the dataset
    X_train.loc[:, ['Age', 'Weight', 'HB', 'BP']] = norm.fit_transform(X_train[['Age', 'Weight', 'HB', 'BP']])
    X_test.loc[:, ['Age', 'Weight', 'HB', 'BP']] = norm.transform(X_test[['Age', 'Weight', 'HB', 'BP']])
    return X_train, X_test, y_train, y_test 


if __name__=='__main__':
    # Load dataset into a panda dataframe
    # df = pd.read_csv('LBW_Dataset.csv')
    # preprocess(df)
    # df.to_csv('processedLBW_Dataset.csv', index=False)

    # Load preprocessed dataset into a panda dataframe
    df = pd.read_csv('processedLBW_Dataset.csv')

    # Perform preprocessing on the dataset to fill in null values and normalize numerical values
    # Also perform splitting of dataset into training and testing datasets and return them
    X_train, X_test, y_train, y_test = normalize(df)

    # List of the layers in the NN model, with each element representing a layer and the element value represents the number of neurons in the layer
    # First Layer: 9 (Number of features served as INPUT)
    # Last Layer: 1 (OUTPUT Binary Classification, a value between 0 and 1)
    # Other Layers: Hidden layers
    layers = [9, 8, 5, 3, 1]

    # alpha: The learning rate used in backpropagation while training the model
    alpha = 0.05

    # Number of iterations for training the model over the training dataset (forward propagation + backward propagation)
    epoch = 200

    # Activation function for the hidden layers 
    actvn_func = 'relu'

    # Create the Neural Network model 
    model = NN(layers, alpha, epoch, activation = actvn_func)    

    # Train the Neural Network model over the training dataset
    model.fit(X_train, y_train, verbose=0)
    
    # Getting the training set accuracy
    y_pred = list(model.predict(X_train)[0])
    y_train_orig = list(y_train.values)  

    print("\n---- Evaluation ----")
    print("\nOVER TRAINING DATASET")
    model.CM(y_train_orig, y_pred)

    print("---- ---- ---- ---- ----")
          
    # Getting the testing set accuracy
    y_pred = list(model.predict(X_test)[0])
    y_test_orig = list(y_test.values)

    print("\nOVER TESTING DATASET")
    model.CM(y_test_orig, y_pred)
    print("---- ---- ---- ---- ----")