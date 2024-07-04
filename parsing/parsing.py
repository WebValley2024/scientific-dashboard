import os
def extract_orbit(file_name):
    try:
        base_name = os.path.basename(file_name)
        parts = base_name.split('_')
        start_index = None
        for i in range(len(parts)):
            if parts[i].isdigit() and len(parts[i]) == 8: 
                start_index = i
                break
    
        if start_index is None:
            raise ValueError(f"Formato data non trovato nel nome del file: {file_name}")
        
        orbit = parts[start_index - 1]  
        return orbit
    except ValueError as e:
        print(f"Errore nel parsing dell'orbita per il file {file_name}: {e}")
        return None
    
def extract_dates(file_name):
    from datetime import datetime as dt
    try:
        base_name = os.path.basename(file_name)
        parts = base_name.split('_')
        start_index = None
        for i in range(len(parts)):
            if parts[i].isdigit() and len(parts[i]) == 8:
                start_index = i
                break
        if start_index is None:
            raise ValueError(f"Date format not found in file name: {file_name}")
        start_date_str = '_'.join(parts[start_index:start_index + 2])
        end_date_str = '_'.join(parts[start_index + 2:start_index + 4])
        start_date = dt.strptime(start_date_str, '%Y%m%d_%H%M%S').date()
        end_date = dt.strptime(end_date_str, '%Y%m%d_%H%M%S').date()
        return start_date, end_date
    except ValueError as e:
        print(f"Error parsing dates for file {file_name}: {e}")
        return None, None

def extract_dataset_type(file_paths):    
    dataset_types = []
    
    for file_path in file_paths:
        file_name = file_path.split('/')[-1]
        
        if 'EFD' in file_name:
            dataset_types.append([file_path, 'EFD'])
        elif 'LAP' in file_name:
            dataset_types.append([file_path, 'LAP'])
        elif 'SCM' in file_name:
            dataset_types.append([file_path, 'SCM'])
        elif 'HEP_4' in file_name:
            dataset_types.append([file_path, 'HEP_4'])
        elif 'HEP_1' in file_name:
            dataset_types.append([file_path, 'HEP_1'])
        elif 'HEP_2' in file_name:
            dataset_types.append([file_path, 'HEP_2'])
        elif 'HEP_DDD' in file_name:
            dataset_types.append([file_path, 'HEP_DDD'])
        else:
            raise ValueError(f"Unknown dataset type in file name: {file_name}")
    return dataset_types