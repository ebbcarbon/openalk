import numpy as np

def RSQ(x, y) :

    x = np.expand_dims(x, axis = 0)
    y = np.expand_dims(y, axis = 0)

    if (x.shape[1] > x.shape[0]) :
        
        x = np.transpose(x)
        
    if (y.shape[1] > y.shape[0]) :
        
        y = np.transpose(y)

    workMatrix = np.zeros((x.shape[0], 6))
    workMatrix[:, [0]] = x
    workMatrix[:, [1]] = y

    # remove NaNs and infs
    
    workMatrix = workMatrix[np.all(~np.isnan(workMatrix), axis = 1),:]
    workMatrix = workMatrix[np.all(~np.isinf(workMatrix), axis = 1),:]

    # Calculate slope, intercept, modelx, and modely
        
    fitParam = np.polyfit(workMatrix[:, 0], workMatrix[:, 1], 1)

    slope = fitParam[0]
    intercept = fitParam[1]
    yModel = workMatrix[:, [0]] * slope + intercept
    xModel = workMatrix[:, [0]]

    workMatrix[:, [2]] = yModel

    # Calculate SSE, SSR, SST

    workMatrix[:, [3]] = np.subtract(workMatrix[:, [1]], workMatrix[:, [2]]) #SSE
    workMatrix[:, [4]] = np.subtract(workMatrix[:, [1]], np.mean(workMatrix[:, [1]])) #SSR
    workMatrix[:, [5]] = np.subtract(workMatrix[:, [2]], np.mean(workMatrix[:, [1]])) #SST

    SSE = np.sum(np.square(workMatrix[:, [3]]))
    SSR = np.sum(np.square(workMatrix[:, [4]]))
    SST = np.sum(np.square(workMatrix[:, [5]]))

    Rsq = 1 - SSE/SST

    return slope, intercept, xModel, yModel, Rsq

    

