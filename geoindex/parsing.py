import os
from datetime import datetime

def get_file_name(file_path):
    return os.path.basename(file_path)


def extract_satellite_number(file_name):
    try:
        parts = file_name.split("_")
        satellite_number = parts[1]
        return satellite_number
    except IndexError:
        print(
            f"Errore nell'estrazione del numero del satellite per il file {file_name}"
        )
        return None


def extract_instrument_code(file_name):
    try:
        parts = file_name.split("_")
        instrument_code = parts[2]
        return instrument_code
    except IndexError:
        print(f"Errore nell'estrazione del codice strumento per il file {file_name}")
        return None


def extract_instrument_number(file_name):
    try:
        parts = file_name.split("_")
        instrument_number = parts[3]
        return instrument_number
    except IndexError:
        print(f"Errore nell'estrazione del numero strumento per il file {file_name}")
        return None


def extract_data_level(file_name):
    try:
        parts = file_name.split("_")
        data_level = parts[4]
        return data_level
    except IndexError:
        print(f"Errore nell'estrazione del livello dei dati per il file {file_name}")
        return None


def extract_orbit(file_name):
    try:
        base_name = os.path.basename(file_name)
        parts = base_name.split("_")
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
    try:
        base_name = os.path.basename(
            file_name
        )  # returns the final component of a pathname
        parts = base_name.split("_")

        # find the index of the part that contains the start_date
        start_index = None
        for i in range(len(parts)):
            if (
                parts[i].isdigit() and len(parts[i]) == 8
            ):  # find the part with data format YYYYMMDD
                start_index = i
                break

        if start_index is None:
            raise ValueError(f"Formato data non trovato nel nome del file: {file_name}")

        start_date_str = "_".join(parts[start_index : start_index + 2])
        end_date_str = "_".join(parts[start_index + 2 : start_index + 4])

        start_date = datetime.strptime(start_date_str, "%Y%m%d_%H%M%S")
        end_date = datetime.strptime(end_date_str, "%Y%m%d_%H%M%S")

        return start_date, end_date
    except ValueError as e:
        print(f"Errore nel parsing delle date per il file {file_name}: {e}")
        return None, None


def parse_filename(file_name):
    file = get_file_name(file_name)
    satellite_nr = extract_satellite_number(file_name)
    instrument_code = extract_instrument_code(file_name)
    instrument_nr = extract_instrument_number(file_name)
    data_l = extract_data_level(file_name)
    start_date, end_date = extract_dates(file_name)
    semiorbit_nr = extract_orbit(file_name)
    return {
        "file_name": file,
        "satellite_nr": satellite_nr,
        "instrument_code": instrument_code,
        "instrument_nr": instrument_nr,
        "data_l": data_l,
        "semiorbit_nr": semiorbit_nr,
        "start_date": start_date,
        "end_date": end_date,
    }
