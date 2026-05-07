# This is a module of py functions being used by 
from pathlib import Path
import csv
# import sys_funcs
from pathlib import Path
import csv
import pandas as pd
import numpy as np
#import tkinter as tk
import pickle
from pathlib import Path
import csv
import os
import sys
import re
# ==============================================
from pathlib import Path
import pandas as pd
import os
# ================================================================================

def get_filename_frm_sn(dts, sn):
    """
    Retrieves the filename and full path for a given serial number from an enriched DataFrame dictionary.

    Args:
        dts (dict): Dictionary where each value is a dict with keys 'name', 'df', and 'serial'.
        sn (int): Serial number to look up.

    Returns:
        tuple: (filename, full_path) if found, else (None, None)
    """
    for path, entry in dts.items():
        if entry.get("serial") == sn:
            return entry.get("name"), path
    return None, None


# ======================================================================================
#  ============ add r for single slashes ie folder = r"C:\Users\bhuns\OneDrive\___Health Data\__DD studies\InBody CSV\ib97"

def load_dataframes_from_folder(folder_path, extension=".csv", encoding="utf-8", use_full_path=False):
    """
    Recursively loads all files with the given extension from a folder into pandas DataFrames.

    Args:
        folder_path (str): Windows-style path to the folder.
        extension (str): File extension to search for (e.g., ".csv", ".txt").
        encoding (str): Encoding used to read the files.
        use_full_path (bool): If True, keys will be full paths; otherwise, just filenames.

    Returns:
        dict: Dictionary of DataFrames keyed by filename or full path.
    """
    # Convert Windows path to WSL format if needed
    if os.name != "nt":  # If running in WSL/Linux
        folder_path = folder_path.replace("\\", "/")
        if folder_path.startswith("/mnt/") is False:
            drive_letter = folder_path[0].lower()
            folder_path = f"/mnt/{drive_letter}{folder_path[2:]}"
    
    folder = Path(folder_path)

    # Recursively find all matching files
    files = list(folder.rglob(f"*{extension}"))

    if not files:
        print(f"⚠️ No files with extension '{extension}' found in {folder_path}")
        return {}

    # Load each file into a DataFrame
    dataframes = {}
    for file in files:
        try:
            df = pd.read_csv(file, encoding=encoding) if extension == ".csv" else pd.read_table(file, encoding=encoding)
            key = str(file) if use_full_path else file.name
            dataframes[key] = df
        except Exception as e:
            print(f"❌ Failed to load {file}: {e}")

    return dataframes















#=====================================================================
def get_dtv_range():
    try:
        start_dtv = int(input("Enter beginning dtv: "))
        end_dtv = int(input("Enter ending dtv: "))
        return [start_dtv, end_dtv]
    except ValueError:
        print("Invalid input. Please enter integer values.")
        return None
#=======================================================
def clean_wsl_path(raw_path):                            #  raw_path = "bnm.csv"
    """
    Cleans and normalizes a WSL path for safe use in file operations.
    Returns a pathlib.Path object.
    """
    raw_path = raw_path.strip().replace('\\', '/')
    raw_path = re.sub(r'/+', '/', raw_path)
    return Path(raw_path)

#==========================================================================

# sys_funcs.py
import csv
from pathlib import Path

def read_csv_to_array(filepath):
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"CSV file not found: {path}")
    with path.open(newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        array = [row for row in reader if row]
    return array


#=====================================================================

# array_to_dt_row_dict(array) THIS IS THE TOTAL DATA FOR THIS "bnm"
def array_to_dt_row_dict(array):
    header = array[0][1:]  # Skip 'dtv', keep other column names
    dt_row_dict = {} 

    for row in array[1:]:
        key = row[0]  # 'dtv' value
        values = row[1:]
        dt_row_dict[key] = dict(zip(header, values))

    return dt_row_dict
# =====================================================================
# update_dt_row_dict  Makes the empty dictionary to fill
def make_blnk_update_row_dict(dt_row_dict, dvt):
    start_date, end_date = dvt
    blnk_update_dt_row_dict = {}

    for date_key in dt_row_dict:  # ✅ use dt_row_dict here
        if start_date <= date_key <= end_date:
            blnk_update_dt_row_dict [date_key] = {col: '' for col in dt_row_dict[date_key]}  # also fix xrow_dict if needed
#    update_row_dict = blnk_update_dt_row_dict 
#    return update_row_dict
    return blnk_update_row_dict
# =========================================================

# DEF transpose lut from rows to cols
def transpose_csv_to_col_dict(csv_rows):
    headers = csv_rows[0][1:]  # skip BOM or placeholder
    col_dict = {}

    for col_index, serial in enumerate(headers):
        entry = {}
        for row in csv_rows[1:]:
            key = row[0].strip('"')  # remove quotes
            value = row[col_index + 1].strip('"')
            # Convert types if needed
            if key in ['value', 'min', 'max', 'step']:
                try:
                    entry[key] = float(value) if '.' in value else int(value)
                except ValueError:
                    entry[key] = None
            elif key == 'active':
                entry[key] = value.lower() not in ['no', 'false', '0', '']
            else:
                entry[key] = value
        col_dict[serial] = entry

    return col_dict

# =========================================================
# step 1 for sliders ✅ Final Pattern: Interactive Form + Pickle-Based Retrieval
# import ipywidgets as widgets
from IPython.display import display, clear_output
import pickle


# ===================================================================================
# Step 2: Retrieve the result in a separate cell for sliders
def get_update_dt_row_dict(pickle_path="update_dt_row_dict"):
    import pickle
    with open(pickle_path, "rb") as f:
        result = pickle.load(f)
    print("📤 Retrieved result from pickle:")
    return result

#========================================================================================

def transfer_updates(updated_dict, dt_row_dict):
    """
    Transfers non-empty values from updated_dict into dt_row_dict.
    Assumes both dictionaries share the same structure: {day: {serial: value}}.
    """
    for day, serials in updated_dict.items():
        if day not in dt_row_dict:
            dt_row_dict[day] = {}  # Optionally scaffold missing day
        for serial, value in serials.items():
            if value != '':
                dt_row_dict[day][serial] = value
    return dt_row_dict
# ============ put values into the" blnk_update_dt_row_dict" ================================================
#==================================================================

def universal_import(folder_path, pattern="*", expected_columns=None, df_name=None, verbose=True):
    folder = Path(folder_path)
    if not folder.exists():
        raise FileNotFoundError(f"Folder not found: {folder_path}")
    
    file_list = list(folder.glob(pattern))
    dfs = []
    
    for f in file_list:
        for encoding in ['utf-8', 'ISO-8859-1']:
            try:
                if f.suffix in ['.xlsx', '.xls']:
                    df = pd.read_excel(f)
                else:
                    df = pd.read_csv(f, encoding=encoding, sep=",", engine="c")
                
                if expected_columns and df.shape[1] != expected_columns:
                    if verbose:
                        print(f"⚠️ Skipped {f.name}: expected {expected_columns} columns, got {df.shape[1]}")
                    break
                
                df['source_file'] = f.name
                df['encoding_used'] = encoding
                dfs.append(df)
                if verbose:
                    print(f"✅ Loaded {f.name} with {encoding}")
                break
            except Exception as e:
                if encoding == 'ISO-8859-1' and verbose:
                    print(f"❌ Skipped {f.name}: {e}")
    
    if dfs:
        combined = pd.concat(dfs, ignore_index=True)
        label = df_name if df_name else "imported_dataframe"
        pickle_path = Path.cwd() / f"{label}.pkl"
        combined.to_pickle(pickle_path)
        if verbose:
            print(f"✅ [{label}] Final DataFrame: {len(combined)} rows from {len(dfs)} files.")
            print(f"💾 Saved to pickle: {pickle_path}")
        return combined
    else:
        if verbose:
            print("🚫 No valid files loaded.")
        return pd.DataFrame()

###_adding [iclel save]

# disapbled for test =============================================================
from datetime import datetime

def parse_inbody_timestamp(ts_str):
    try:
        dt = datetime.strptime(ts_str, "%Y%m%d%H%M%S")
        return {
            "Year": dt.year,
            "Month": f"{dt.month:02d} ({dt.strftime('%B')})",
            "Day": f"{dt.day:02d}",
            "Hour": f"{dt.hour:02d} (24-hour format)",
            "Minute": f"{dt.minute:02d}",
            "Second": f"{dt.second:02d}"
        }
    except ValueError:
        return {"Error": "Invalid timestamp format. Expected YYYYMMDDHHMMSS."}
#================================================================================================
from datetime import datetime

def build_lut(data_dict, start_serial=700):
    lut = {}
    base_date = datetime(1900, 1, 1)

    for i, raw_ts in enumerate(data_dict["14. Test Date / Time"]):
        try:
            ts_str = str(raw_ts).strip()
            if ts_str.lower() == "nan" or len(ts_str) < 14:
                continue
            dt = datetime.strptime(ts_str[:14], "%Y%m%d%H%M%S")
        except (ValueError, TypeError):
            continue

        dtv = (dt - base_date).days  # Days since 1/1/1900
        serial_id = f"ib{start_serial + i}"
        lut[serial_id] = {
            "timestamp": ts_str,
            "datetime": dt,
            "dtv": dtv,
            "index": i
        }

    return lut


#=================================================================================================================
# DEF def extract_a_column_as_df(source_dict, key_name)  --put in sys_func.py 

def extract_a_column_as_df(source_dict, key_name):
    """
    Extract a single column from a dictionary of lists and return it as a DataFrame.

    Parameters:
    - source_dict: dict[str, list] — dictionary where each key maps to a column
    - key_name: str — the key to extract

    Returns:
    - pd.DataFrame — DataFrame with one column named after the key
    """
    if key_name not in source_dict:
        raise KeyError(f"Key '{key_name}' not found in the dictionary.")
    
    return pd.DataFrame({key_name: source_dict[key_name]})

  # ==============================================================================================================
# def extract_multicolumns_as_df(source_dict, column_names) --put in sys_func.py 

def extract_multicolumns_as_df(source_dict, column_names):
    """
    Extract multiple columns from a dictionary of lists and return them as a DataFrame.

    Parameters:
    - source_dict: dict[str, list] — dictionary where each key maps to a column
    - column_names: list[str] — list of keys to extract

    Returns:
    - pd.DataFrame — DataFrame with selected columns
    """
    missing = [col for col in column_names if col not in source_dict]
    if missing:
        raise KeyError(f"Missing keys in dictionary: {missing}")
    
    selected_data = {col: source_dict[col] for col in column_names}
    return pd.DataFrame(selected_data)

#=============================================================================================================
# DEF  def validate_and_sort_timestamps(df, timestamp_col="Cleaned_Timestamp")           --put in sys_func.py
def validate_and_sort_timestamps(df, timestamp_col="Cleaned_Timestamp"):
    """
    Validates and sorts a timestamp column, logging parsing failures and computing time gaps.

    Parameters:
    - df: pd.DataFrame — input DataFrame
    - timestamp_col: str — name of the timestamp column

    Returns:
    - df_sorted: pd.DataFrame — cleaned and chronologically sorted DataFrame
    - df_errors: pd.DataFrame — rows with invalid timestamps
    """
    df = df.copy()

    # Step 1: Attempt datetime conversion
    df[timestamp_col] = pd.to_datetime(df[timestamp_col], errors="coerce")

    # Step 2: Split valid and invalid rows
    df_valid = df[df[timestamp_col].notna()].copy()
    df_errors = df[df[timestamp_col].isna()].copy()

    # Step 3: Sort valid rows chronologically
    df_sorted = df_valid.sort_values(timestamp_col).reset_index(drop=True)

    # Step 4: Compute time gaps (optional)
    df_sorted["delta_minutes"] = df_sorted[timestamp_col].diff().dt.total_seconds().div(60)

    return df_sorted, df_errors

# ================================================================================
# filters out mrn timestamps 
# def extract_and_filter_by_time_window(source_dict, column_group, timestamp_col="Cleaned_Timestamp",start_time=time(4, 0), end_time=time(10, 0)):
from datetime import time
import pandas as pd

def extract_and_filter_by_time_window(source_dict, column_group, timestamp_col="Cleaned_Timestamp",start_time=time(4, 0), end_time=time(10, 0)):
    """
    Extracts selected columns from a dict, validates timestamps, sorts chronologically,
    and filters by time-of-day window.

    Parameters:
    - source_dict: dict — your working dict (e.g. ib970cln)
    - column_group: list — list of column names to extract
    - timestamp_col: str — name of the timestamp column
    - start_time: datetime.time — lower bound for time-of-day filter
    - end_time: datetime.time — upper bound for time-of-day filter

    Returns:
    - df_filtered: pd.DataFrame — cleaned, sorted, and time-window-filtered DataFrame
    - df_errors: pd.DataFrame — rows with invalid timestamps
    """
    # Step 1: Extract selected columns
    df = pd.DataFrame({col: source_dict[col] for col in column_group if col in source_dict})

    # Step 2: Validate timestamp column
    if timestamp_col not in df.columns:
        raise ValueError(f"Timestamp column '{timestamp_col}' not found in selected group.")

    df[timestamp_col] = pd.to_datetime(df[timestamp_col], errors="coerce")

    # Step 3: Split valid and invalid timestamps
    df_valid = df[df[timestamp_col].notna()].copy()
    df_errors = df[df[timestamp_col].isna()].copy()

    # Step 4: Sort chronologically
    df_valid = df_valid.sort_values(timestamp_col).reset_index(drop=True)

    # Step 5: Extract time component
    df_valid["time_only"] = df_valid[timestamp_col].dt.time

    # Step 6: Filter by time-of-day window
    df_filtered = df_valid[
        (df_valid["time_only"] >= start_time) &
        (df_valid["time_only"] <= end_time)
    ].copy()

    # Step 7: Drop helper column
    df_filtered.drop(columns=["time_only"], inplace=True)

    return df_filtered, df_errors
# ====XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
# use explorer path to copy files from windows dir to WSL directories
import os
import shutil
import platform

def xplr_pths_to_JL(windows_src, WSL_target):
    r"""
    Converts Explorer-copied paths into JupyterLab-compatible paths.

    Parameters:
    - windows_src (str): Windows-style source file path (e.g., copied from Explorer)
    - WSL_target (str): WSL UNC-style folder path (e.g., \\wsl.localhost\Ubuntu\home\...)

    Returns:
    - windows_path (str): Resolved source path (with \\?\ prefix if needed)
    - WSL_target_folder (str): Native WSL path (e.g., /home/user/...)
    """
    # Use raw string logic — no escaping
    windows_src = windows_src.strip()
    if not windows_src.startswith(r"\\?\\"):
        windows_path = r"\\?\{}".format(windows_src)
    else:
        windows_path = windows_src

    if WSL_target.startswith(r"\\wsl.localhost\Ubuntu"):
        WSL_target_folder = WSL_target.replace(r"\\wsl.localhost\Ubuntu", "").replace("\\", "/")
    else:
        WSL_target_folder = WSL_target.replace("\\", "/")

    return windows_path, WSL_target_folder


def File_Copier_Windows_to_WSL(windows_path, WSL_target_folder):
    r"""
    Copies a Windows file to a WSL-accessible folder.

    Parameters:
    - windows_path (str): Full Windows path to the source file
    - WSL_target_folder (str): Native WSL path to the target folder

    Returns:
    - target_file (str): Full path to the copied file in WSL
    """
    windows_path = os.path.normpath(windows_path)
    WSL_target_folder = os.path.normpath(WSL_target_folder)

    if not os.path.isfile(windows_path):
        raise FileNotFoundError(f"Source file not found: {windows_path}")

    if not os.path.isdir(WSL_target_folder):
        raise NotADirectoryError(f"Target folder not found: {WSL_target_folder}")

    filename = os.path.basename(windows_path)
    target_file = os.path.join(WSL_target_folder, filename)

    try:
        shutil.copy2(windows_path, target_file)
        print(f"✅ File copied to WSL: {target_file}")
        return target_file
    except Exception as e:
        print(f"❌ Copy failed: {e}")
        raise


# =========================   READ ===========================================
       # def read_file_dual_path(win_path, wsl_path=None, skip_head_rows=0):

import os
import pandas as pd

def read_file_dual_path(win_path, wsl_path=None, skip_head_rows=0):
    """
    Reads a file (.xlsx, .asc, or .csv) from either Windows or WSL path.
    Skips noisy head rows for .asc/.csv if needed. Tries fallback encodings.
    """
    if wsl_path is None:
        wsl_path = win_path.replace("C:\\", "/mnt/c/").replace("\\", "/")

    print("wsl_path = ", wsl_path)

    def read_text_file(path, encodings=["utf-8", "ISO-8859-1", "cp1252"]):
        for enc in encodings:
            try:
                with open(path, "r", encoding=enc) as f:
                    lines = f.readlines()
                clean_lines = [line.strip() for line in lines if line.strip()]
                trimmed_lines = clean_lines[skip_head_rows:]
                from io import StringIO
                buffer = StringIO("\n".join(trimmed_lines))
                return pd.read_csv(buffer, engine="python", on_bad_lines="skip")
            except Exception as e:
                print(f"Encoding {enc} failed: {e}")
        raise ValueError("All encoding attempts failed.")

    def read_file(path):
        ext = os.path.splitext(path)[1].lower()
        if ext == ".xlsx":
            return pd.read_excel(path)
        elif ext in [".asc", ".csv"]:
            return read_text_file(path)
        else:
            raise ValueError(f"Unsupported file extension: {ext}")

    for path in [wsl_path, win_path]:
        if os.path.exists(path):
            try:
                return read_file(path)
            except Exception as e:
                print(f"{path} failed: {e}")

    print("File not found in either path.")
    return None

# ===============================================================  write  ======================================================
# Writes a DataFrame to .xlsx or .csv in either Windows or WSL path.
#    Accepts raw Windows paths and auto-converts to WSL if needed.

import os
import pandas as pd

def write_file_dual_path(df, win_path, wsl_path=None, overwrite=True):
    """
    Writes a DataFrame to .xlsx or .csv in either Windows or WSL path.
    Accepts raw Windows paths and auto-converts to WSL if needed.
    """
    win_path = os.path.normpath(win_path)

    if wsl_path is None:
        wsl_path = win_path.replace("\\", "/").replace("C:", "/mnt/c")

    print("Attempting write to WSL path:", wsl_path)

    def write_file(path):
        ext = os.path.splitext(path)[1].lower()
        if not overwrite and os.path.exists(path):
            raise FileExistsError(f"File already exists: {path}")
        if ext == ".xlsx":
            df.to_excel(path, index=False)
        elif ext == ".csv":
            df.to_csv(path, index=False, encoding="utf-8")
        else:
            raise ValueError(f"Unsupported file extension: {ext}")

    for path in [wsl_path, win_path]:
        try:
            write_file(path)
            print(f"Write successful to: {path}")
            return path
        except Exception as e:
            print(f"{path} write failed: {e}")

    print("Write failed in both paths.")
    return None

# ====================================================
import os
import csv
def asc_to_csv_cnv(input_folder):
   
    output_folder = os.path.join(input_folder, "converted_csv")
    os.makedirs(output_folder, exist_ok=True)
    
    header = ["Label", "Val1", "Val2", "Val3", "Val4", "Val5", "Val6", "Val7", "Val8"]
    
    for filename in os.listdir(input_folder):
        if filename.lower().endswith(".asc"):
            input_path = os.path.join(input_folder, filename)
            output_path = os.path.join(output_folder, filename.replace(".asc", ".csv"))
    
            with open(input_path, "r", encoding="utf-8") as infile, open(output_path, "w", newline="", encoding="utf-8") as outfile:
                reader = csv.reader(infile)
                writer = csv.writer(outfile)
                writer.writerow(header)
    
                for row in reader:
                    cleaned = [item.strip() for item in row]
                    writer.writerow(cleaned)
    
    print(f"✅ Conversion complete. CSVs saved to:\n{output_folder}")
    return 

# ============================================================================================================


