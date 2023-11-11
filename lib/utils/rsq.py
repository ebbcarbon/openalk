from typing import Tuple

import numpy as np

import matplotlib.pyplot as plt


def RSQ(x: np.ndarray, y: np.ndarray) -> Tuple[np.float64, np.float64,
                                          np.ndarray, np.ndarray, np.float64]:
    print('Called RSQ')

    print(x)
    print(x.shape)
    print(y)
    print(y.shape)
    x = np.expand_dims(x, axis=0)
    y = np.expand_dims(y, axis=0)
    print(x)
    print(x.shape)
    print(y)
    print(y.shape)


    if x.shape[1] > x.shape[0]:
        x = np.transpose(x)

    if y.shape[1] > y.shape[0]:
        y = np.transpose(y)

    print(x)
    print(x.shape)
    print(y)
    print(y.shape)

    workMatrix = np.zeros((x.shape[0], 6))
    print(workMatrix)
    print(workMatrix.shape)
    workMatrix[:, [0]] = x
    print(workMatrix)
    workMatrix[:, [1]] = y

    print(f"Original work matrix: {workMatrix}")
    # remove NaNs and infs

    workMatrix = workMatrix[np.all(~np.isnan(workMatrix), axis=1), :]
    workMatrix = workMatrix[np.all(~np.isinf(workMatrix), axis=1), :]

    print(f"Cleaned work matrix: {workMatrix}")

    print(workMatrix[:, 0])
    print(workMatrix[:, 0].shape)
    print(workMatrix[:, 1])
    print(workMatrix[:, 1].shape)
    # Calculate slope, intercept, modelx, and modely

    fitParam = np.polyfit(workMatrix[:, 0], workMatrix[:, 1], 1)
    print(fitParam)

    slope = fitParam[0]
    intercept = fitParam[1]
    yModel = workMatrix[:, [0]] * slope + intercept
    xModel = workMatrix[:, [0]]

    workMatrix[:, [2]] = yModel

    plt.plot(xModel, y, 'r.', xModel, yModel)
    plt.show()

    # Calculate SSE, SSR, SST

    workMatrix[:, [3]] = np.subtract(workMatrix[:, [1]], workMatrix[:, [2]])  # SSE
    workMatrix[:, [4]] = np.subtract(
        workMatrix[:, [1]], np.mean(workMatrix[:, [1]])
    )  # SSR
    workMatrix[:, [5]] = np.subtract(
        workMatrix[:, [2]], np.mean(workMatrix[:, [1]])
    )  # SST

    SSE = np.sum(np.square(workMatrix[:, [3]]))
    SSR = np.sum(np.square(workMatrix[:, [4]]))
    SST = np.sum(np.square(workMatrix[:, [5]]))

    Rsq = 1 - SSE / SST

    return slope, intercept, xModel, yModel, Rsq
