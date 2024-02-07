import logging
from typing import Tuple

import numpy as np

logger = logging.getLogger(__name__)

def linear_regression(x: np.ndarray, y: np.ndarray) -> Tuple[np.float64,
                            np.float64, np.ndarray, np.ndarray, np.float64]:
    """Fits a degree one polynomial from x to y.

    Args:
        x (np.ndarray): x-coordinates of the sample points.
        y (np.ndarray): y-coordinates of the sample points.

    Returns:
        tuple containing:
         - slope (np.float64): slope of the line of best fit.
         - intercept (np.float64): intercept of the line of best fit.
         - x_model (np.ndarray): original x-coordinates.
         - y_model (np.ndarray): y-coordinates after fitting.
         - rsq (np.float64): R-squared value.
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

    # Sum of squares error (SSE)
    work_matrix[:, [3]] = np.subtract(
        work_matrix[:, [1]], work_matrix[:, [2]]
    )
    # Sum of squares regression (SSR)
    work_matrix[:, [4]] = np.subtract(
        work_matrix[:, [1]], np.mean(work_matrix[:, [1]])
    )
    # Sum of squares total (SST)
    work_matrix[:, [5]] = np.subtract(
        work_matrix[:, [2]], np.mean(work_matrix[:, [1]])
    )

    sum_squares_error = np.sum(np.square(work_matrix[:, [3]]))
    sum_squares_regression = np.sum(np.square(work_matrix[:, [4]]))
    sum_squares_total = np.sum(np.square(work_matrix[:, [5]]))

    rsq = 1 - (sum_squares_error / sum_squares_total)

    return slope, intercept, x_model, y_model, rsq
