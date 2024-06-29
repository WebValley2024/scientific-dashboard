import xarray as xr
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt


import numpy as np
import xarray as xr

def reduce_frequency(data_array, frequency):
    """
    Reduce the number of measurements in each row of the xarray based on the specified frequency,
    while preserving the metadata.
    
    Parameters:
    data_array (xarray.DataArray): The input xarray.
    frequency (int): The number of elements to keep in each row.
    
    Returns:
    xarray.DataArray: The reduced xarray.
    """
    # Get the shape of the data array
    num_rows, num_cols = data_array.shape
    
    if frequency > num_cols:
        raise ValueError("Frequency cannot be greater than the number of columns in the data array.")
    
    # Create a list to hold the reduced rows
    reduced_rows = []
    
    for row in data_array.values:
        # Calculate the indices of the elements to keep
        indices = np.linspace(0, num_cols - 1, frequency, dtype=int)
        reduced_row = row[indices]
        reduced_rows.append(reduced_row)
    
    # Stack the reduced rows into a new array
    reduced_values = np.stack(reduced_rows, axis=0)
    
    # Create a new DataArray with the reduced data
    reduced_data_array = xr.DataArray(reduced_values, 
                                      dims=[data_array.dims[0], data_array.dims[1]], 
                                      coords={data_array.dims[0]: data_array.coords[data_array.dims[0]],
                                              data_array.dims[1]: data_array.coords[data_array.dims[1]][indices]},
                                      attrs=data_array.attrs)
    
    return reduced_data_array
