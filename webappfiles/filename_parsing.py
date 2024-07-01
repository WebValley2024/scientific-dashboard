import datetime
import os

def parse_filename(file_path):
    """
    Parse the given file path based on the format:
    CSES_01_XXXX_XXX_XX_XXXXXX_YYYYMMDD_hhmmss_YYYYMMDD_hhmmss_XXX.h5
    
    Extracts the start and end dates from the filename.
    """
    filename = os.path.basename(file_path)
    parts = filename.split('_')
    
    if len(parts) < 9:
        raise ValueError("Invalid file name format")
    
    start_date_str = parts[6]
    end_date_str = parts[8][:8]  # Extract YYYYMMDD from hhmmss_YYYYMMDD
    
    try:
        start_date = datetime.datetime.strptime(start_date_str, '%Y%m%d').date()
        end_date = datetime.datetime.strptime(end_date_str, '%Y%m%d').date()
    except ValueError as e:
        raise ValueError(f"Error parsing dates from file name: {e}")
    
    return start_date, end_date

def is_within_date_range(file_path, start_date_range, end_date_range):
    """
    Check if the start and end dates extracted from the file name
    fall within the specified date range.
    
    Parameters:
    - file_path: Path to the file
    - start_date_range: Start date of the range (datetime.date object)
    - end_date_range: End date of the range (datetime.date object)
    
    Returns:
    - True if both start and end dates are within the specified range, False otherwise.
    """
    try:
        file_start_date, file_end_date = parse_filename(file_path)
        return start_date_range <= file_start_date <= end_date_range and \
               start_date_range <= file_end_date <= end_date_range
    except ValueError:
        return False  # Handle invalid file name format gracefully

def timerange(file_dir):
    # file_dir = '/home/user/data/'
    start_date_range = datetime.date(2021, 12, 1)
    end_date_range = datetime.date(2021, 12, 31)
    
    if is_within_date_range(file_path, start_date_range, end_date_range):
        print(f"The file {file_path} is within the specified date range.")
    else:
        print(f"The file {file_path} is not within the specified date range.")

