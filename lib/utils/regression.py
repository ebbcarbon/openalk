from typing import Tuple

import numpy as np

def linear_regression(x: np.ndarray, y: np.ndarray) -> Tuple[np.float64,
                            np.float64, np.ndarray, np.ndarray, np.float64]:
    """Takes in two numpy arrays, x and y, and fits a degree one polynomial
    from x to y.
    """
    x = np.expand_dims(x, axis=0)
    y = np.expand_dims(y, axis=0)

    if x.shape[1] > x.shape[0]:
        x = np.transpose(x)

    if y.shape[1] > y.shape[0]:
        y = np.transpose(y)

    work_matrix = np.zeros((x.shape[0], 6))
    work_matrix[:, [0]] = x
    work_matrix[:, [1]] = y

    # Remove NaNs and infs
    work_matrix = work_matrix[np.all(~np.isnan(work_matrix), axis=1), :]
    work_matrix = work_matrix[np.all(~np.isinf(work_matrix), axis=1), :]

    # Run regression
    fit_param = np.polyfit(work_matrix[:, 0], work_matrix[:, 1], 1)

    slope = fit_param[0]
    intercept = fit_param[1]
    y_model = work_matrix[:, [0]] * slope + intercept
    x_model = work_matrix[:, [0]]

    work_matrix[:, [2]] = y_model

    # SSE
    work_matrix[:, [3]] = np.subtract(
        work_matrix[:, [1]], work_matrix[:, [2]]
    )
    # SSR
    work_matrix[:, [4]] = np.subtract(
        work_matrix[:, [1]], np.mean(work_matrix[:, [1]])
    )
    # SST
    work_matrix[:, [5]] = np.subtract(
        work_matrix[:, [2]], np.mean(work_matrix[:, [1]])
    )

    SSE = np.sum(np.square(work_matrix[:, [3]]))
    SSR = np.sum(np.square(work_matrix[:, [4]]))
    SST = np.sum(np.square(work_matrix[:, [5]]))

    rsq = 1 - SSE / SST

    return slope, intercept, x_model, y_model, rsq
