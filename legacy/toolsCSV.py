import os, numpy as np, pandas as pd
# ------------------------
from log import Log, t2str
global log
log :Log = Log()
def set_log(l):
    global log
    log = l

def timeParse(time_str:str):
    """
    Convert a time value to seconds.
    If time_val is a pandas Timestamp, use its attributes.
    Otherwise, assume it's a string in the format 'MM:SS.sss'.
    """
    date_str, time_str = time_str.split(' ')
    # Convert time part to seconds
    time_str = time_str.split(':')
    date_s = float(time_str[0]) * 3600 + float(time_str[1]) * 60 + float(time_str[2])

    # Convert date part to seconds since epoch (1970-01-01)
    date_str = date_str.split('-')
    date_s += float(date_str[0]) * 365*24*3600 + float(date_str[1])*30*24*3600 + float(date_str[2]) * 24*3600
    return date_s - 62867750400
def splitCSV(filepath, output_folder:str):
    """
    Loads the inclinometer CSV file without altering order or values,
    separates the data by sensor_id, and saves a separate CSV file for each sensor (keeping order of appearance)

    Parameters:
        filepath (str): Path to the original inclinometer CSV file.
        output_folder (str): Folder to save the separate sensor files.
                            If None, creates a folder with the same base name as the input file.

    Returns:
        list: A list of file paths for the saved sensor streams.
    """
    log.up("Separating inclinometer streams")
    # Load the original file without processing
    df = pd.read_csv(filepath)
    datapath = filepath.split("/")[:-1]
    datapath = "/".join(datapath) + "/"
    # Get unique sensor ids
    s_ids = df["sensor_id"].unique()
    log.log(f"Found {len(s_ids)} unique sensor ids")

    # Create a folder for the output files, in the same directory as the input file
    if not os.path.exists(datapath + output_folder):
        os.makedirs(datapath + output_folder)
    log.log(f"Output folder: {output_folder}")

    # Save each sensor stream to a separate file
    saved_files = []
    for sensor_id in s_ids:
        sensor_file = os.path.join(datapath + output_folder, f"{sensor_id}.csv")
        sensor_df = df[df["sensor_id"] == sensor_id]
        sensor_df.to_csv(sensor_file, index=False)
        saved_files.append(sensor_file)
        log.log(f"Sensor {sensor_id} saved to {sensor_file}")
def diffCSV(filepath: str, output_filepath: str):
    """
    Loads a CSV file, computes the first and second derivatives for every column
    except "time" and "sensor_id", and saves the new DataFrame to output_filepath.

    The first derivative is computed using centered differences for interior rows,
    and forward/backward differences at the first/last row.

    The second derivative is computed as the difference of the forward and backward
    first derivative approximations divided by half the time interval.

    The new columns are named by prefixing 'd' for the first derivative and 'dd' for
    the second derivative to the original column name (e.g. 'dX', 'ddX').

    Note: The time column is parsed to numeric values for the derivative calculations
    using parse_time_mmss, but the original "time" values are preserved in the saved file.
    If "sensor_id" is not present originally, it will not be included in the output.
    """
    log.up(f"Adding derivatives to {filepath}")
    df = pd.read_csv(filepath)
    # Verify that the "time" column exists.
    if "time" not in df.columns:
        raise ValueError("Column 'time' not found in CSV file.")
    # Save the original time column to restore later.
    original_time = df["time"].copy()
    # Check if sensor_id is present.
    sensor_present = "sensor_id" in df.columns
    if not sensor_present:
        log.log("Column 'sensor_id' not found in CSV file.")
    # Compute a numeric version of the time column for derivative calculations.
    time_numeric = df["time"].apply(timeParse)
    # Process each column except "time" and "sensor_id".
    for col in df.columns:
        if col in ["time", "sensor_id"]:
            continue

        # Define new column names.
        d_col = f"d{col}"
        dd_col = f"dd{col}"

        # Initialize derivative arrays.
        d = np.empty(len(df))
        d[:] = np.nan

        # First derivative:
        # Interior rows: centered differences.
        d[1:-1] = (df[col].shift(-1) - df[col].shift(1))[1:-1] / (time_numeric.shift(-1) - time_numeric.shift(1))[1:-1]
        # First row: forward difference.
        d[0] = (df[col].iloc[1] - df[col].iloc[0]) / (time_numeric.iloc[1] - time_numeric.iloc[0])
        # Last row: backward difference.
        d[-1] = (df[col].iloc[-1] - df[col].iloc[-2]) / (time_numeric.iloc[-1] - time_numeric.iloc[-2])
        df[d_col] = d

        # Second derivative:
        dd = np.empty(len(df))
        dd[:] = np.nan

        # Compute left and right first derivatives.
        left_deriv = (df[col] - df[col].shift(1)) / (time_numeric - time_numeric.shift(1))
        right_deriv = (df[col].shift(-1) - df[col]) / (time_numeric.shift(-1) - time_numeric)
        # Interior rows: centered second derivative.
        dd[1:-1] = (right_deriv - left_deriv)[1:-1] / ((time_numeric.shift(-1) - time_numeric.shift(1))[1:-1] / 2)

        # For first row, use forward differences (if at least three rows exist).
        if len(df) >= 3:
            left_deriv_0 = (df[col].iloc[1] - df[col].iloc[0]) / (time_numeric.iloc[1] - time_numeric.iloc[0])
            right_deriv_0 = (df[col].iloc[2] - df[col].iloc[1]) / (time_numeric.iloc[2] - time_numeric.iloc[1])
            dd[0] = (right_deriv_0 - left_deriv_0) / ((time_numeric.iloc[2] - time_numeric.iloc[0]) / 2)
        else:
            dd[0] = np.nan

        # For last row, use backward differences.
        if len(df) >= 3:
            left_deriv_last = (df[col].iloc[-1] - df[col].iloc[-2]) / (time_numeric.iloc[-1] - time_numeric.iloc[-2])
            right_deriv_last = (df[col].iloc[-2] - df[col].iloc[-3]) / (time_numeric.iloc[-2] - time_numeric.iloc[-3])
            dd[-1] = (left_deriv_last - right_deriv_last) / ((time_numeric.iloc[-1] - time_numeric.iloc[-3]) / 2)
        else: dd[-1] = np.nan

        df[dd_col] = dd
    # Restore the original "time" column.
    df["time"] = original_time

    # If sensor_id wasn't originally present, remove it (if added somehow).
    if not sensor_present and "sensor_id" in df.columns:
        df.drop(columns=["sensor_id"], inplace=True)

    # Save the new DataFrame.
    df.to_csv(output_filepath, index=False)
    log.down(f"File saved to {output_filepath}")
def copyCSV(source_path, target_path, column_name, output_path=None):
    # Read the CSV files
    df_source = pd.read_csv(source_path)
    df_target = pd.read_csv(target_path)

    # Verify the column exists in both files
    if column_name not in df_source.columns:
        raise ValueError(f"Column '{column_name}' not found in source file.")
    if column_name not in df_target.columns:
        raise ValueError(f"Column '{column_name}' not found in target file.")

    # Optionally, check that both CSV files have the same number of rows
    if len(df_source) != len(df_target):
        raise ValueError("Source and target CSV files have different number of rows.")

    # Copy the column from source to target
    df_target[column_name] = df_source[column_name]

    # Save the modified DataFrame; overwrite target if no output path is given.
    if output_path:
        df_target.to_csv(output_path, index=False)
    else:
        df_target.to_csv(target_path, index=False)

    log.log(f"Column '{column_name}' successfully copied from '{source_path}' to '{target_path if output_path is None else output_path}'.")
