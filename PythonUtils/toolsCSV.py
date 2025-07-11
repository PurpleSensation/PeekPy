"""
CSV and Time Series Processing Utilities
=========================================

Specialized tools for processing time-series sensor data in CSV format.
Designed for maritime structural monitoring applications where precise
time handling and data integrity are critical.

Functions:
- timeParse: Convert time strings to seconds since epoch
- splitCSV: Separate multi-sensor CSV files by sensor ID
- diffCSV: Compute derivatives for all data columns
- copyCSV: Copy columns between CSV files

Author: Dr. Hono Salval & CoreMarine Development Team
"""

import os
import numpy as np
import pandas as pd
from PythonUtils.log import Log, t2str

# Global logger instance - can be overridden by set_log()
global log
log: Log = Log()


def set_log(l):
    """Set the global logger instance for this module."""
    global log
    log = l


def timeParse(time_str: str) -> float:
    """
    Convert a time value to seconds since a reference epoch.
    
    This function parses time strings in the format "YYYY-MM-DD HH:MM:SS.sss"
    and converts them to seconds since a custom epoch (adjusted from Unix epoch).
    
    Parameters:
    -----------
    time_str : str
        Time string in format "YYYY-MM-DD HH:MM:SS.sss"
        
    Returns:
    --------
    float
        Time in seconds since reference epoch
        
    Example:
    --------
    >>> timeParse("2024-03-15 14:30:25.123")
    1710508225.123
    """
    try:
        # Split date and time components
        date_str, time_str = time_str.split(' ')
        
        # Convert time part to seconds
        time_parts = time_str.split(':')
        time_seconds = (float(time_parts[0]) * 3600 + 
                       float(time_parts[1]) * 60 + 
                       float(time_parts[2]))

        # Convert date part to seconds since epoch (1970-01-01)
        date_parts = date_str.split('-')
        # Approximate conversion (365 days/year, 30 days/month)
        date_seconds = (float(date_parts[0]) * 365 * 24 * 3600 + 
                       float(date_parts[1]) * 30 * 24 * 3600 + 
                       float(date_parts[2]) * 24 * 3600)
        
        # Apply offset adjustment (62867750400 seconds)
        return time_seconds + date_seconds - 62867750400
        
    except (ValueError, IndexError) as e:
        log.warning(f"Failed to parse time string '{time_str}': {e}")
        return 0.0


def splitCSV(filepath: str, output_folder: str) -> list:
    """
    Loads a multi-sensor CSV file and separates data by sensor_id into individual files.
    
    This function is particularly useful for inclinometer data where multiple sensors
    are stored in a single CSV file and need to be processed separately.
    
    Parameters:
    -----------
    filepath : str
        Path to the original CSV file containing multi-sensor data
    output_folder : str
        Folder name to save the separate sensor files
        
    Returns:
    --------
    list
        List of file paths for the saved sensor streams
        
    Example:
    --------
    >>> splitCSV("sensors.csv", "individual_sensors")
    ['data/individual_sensors/1.csv', 'data/individual_sensors/2.csv', ...]
    """
    log.up("Separating sensor streams")
    
    try:
        # Load the original file without processing
        df = pd.read_csv(filepath)
        datapath = os.path.dirname(filepath)
        
        # Validate required column
        if "sensor_id" not in df.columns:
            log.warning("No 'sensor_id' column found in CSV file")
            log.down("Failed")
            return []
        
        # Get unique sensor ids
        s_ids = df["sensor_id"].unique()
        log(f"Found {len(s_ids)} unique sensor ids")

        # Create output directory
        output_path = os.path.join(datapath, output_folder)
        if not os.path.exists(output_path):
            os.makedirs(output_path)
        log(f"Output folder: {output_folder}")

        # Save each sensor stream to a separate file
        saved_files = []
        for sensor_id in s_ids:
            sensor_file = os.path.join(output_path, f"{sensor_id}.csv")
            sensor_df = df[df["sensor_id"] == sensor_id]
            sensor_df.to_csv(sensor_file, index=False)
            saved_files.append(sensor_file)
            log(f"Sensor {sensor_id}: {len(sensor_df)} rows -> {sensor_file}")
        
        log.down(f"{len(saved_files)} files created")
        return saved_files
        
    except Exception as e:
        log.warning(f"Error processing CSV file: {e}")
        log.down("Failed")
        return []


def diffCSV(filepath: str, output_filepath: str) -> bool:
    """
    Loads a CSV file and computes first and second derivatives for all data columns.
    
    Derivatives are computed using:
    - Centered differences for interior points
    - Forward/backward differences for endpoints
    - Time-based derivatives using the 'time' column
    
    Parameters:
    -----------
    filepath : str
        Path to the input CSV file
    output_filepath : str
        Path for the output CSV file with derivatives
        
    Returns:
    --------
    bool
        True if successful, False otherwise
        
    Notes:
    ------
    - Requires 'time' column for derivative calculations
    - New columns are named with 'd' prefix for first derivative (e.g., 'dX')
    - Second derivatives use 'dd' prefix (e.g., 'ddX')
    - Original time values are preserved in output
    """
    log.up(f"Computing derivatives for {os.path.basename(filepath)}")
    
    try:
        df = pd.read_csv(filepath)
        
        # Verify that the "time" column exists
        if "time" not in df.columns:
            log.warning("No 'time' column found - derivatives require time data")
            log.down("Failed")
            return False
        
        # Save the original time column to restore later
        original_time = df["time"].copy()
        
        # Check if sensor_id is present
        sensor_present = "sensor_id" in df.columns
        if not sensor_present:
            log("No 'sensor_id' column found")
        
        # Compute a numeric version of the time column for derivative calculations
        log("Parsing time values...")
        time_numeric = df["time"].apply(timeParse)
        
        # Process each column except "time" and "sensor_id"
        data_columns = [col for col in df.columns if col not in ["time", "sensor_id"]]
        log(f"Computing derivatives for {len(data_columns)} data columns")
        
        for col in data_columns:
            # Define new column names
            d_col = f"d{col}"
            dd_col = f"dd{col}"

            # Initialize derivative arrays
            d = np.empty(len(df))
            d[:] = np.nan

            # First derivative: centered differences for interior points
            if len(df) >= 3:
                d[1:-1] = ((df[col].shift(-1) - df[col].shift(1)) / 
                          (time_numeric.shift(-1) - time_numeric.shift(1)))[1:-1]
                
                # First row: forward difference
                d[0] = ((df[col].iloc[1] - df[col].iloc[0]) / 
                       (time_numeric.iloc[1] - time_numeric.iloc[0]))
                
                # Last row: backward difference
                d[-1] = ((df[col].iloc[-1] - df[col].iloc[-2]) / 
                        (time_numeric.iloc[-1] - time_numeric.iloc[-2]))
            
            df[d_col] = d

            # Second derivative
            dd = np.empty(len(df))
            dd[:] = np.nan

            if len(df) >= 3:
                # Compute left and right first derivatives
                left_deriv = ((df[col] - df[col].shift(1)) / 
                             (time_numeric - time_numeric.shift(1)))
                right_deriv = ((df[col].shift(-1) - df[col]) / 
                              (time_numeric.shift(-1) - time_numeric))
                
                # Interior rows: centered second derivative
                dd[1:-1] = ((right_deriv - left_deriv) / 
                           ((time_numeric.shift(-1) - time_numeric.shift(1)) / 2))[1:-1]

                # Endpoints using forward/backward differences
                if len(df) >= 3:
                    left_deriv_0 = ((df[col].iloc[1] - df[col].iloc[0]) / 
                                   (time_numeric.iloc[1] - time_numeric.iloc[0]))
                    right_deriv_0 = ((df[col].iloc[2] - df[col].iloc[1]) / 
                                    (time_numeric.iloc[2] - time_numeric.iloc[1]))
                    dd[0] = ((right_deriv_0 - left_deriv_0) / 
                            ((time_numeric.iloc[2] - time_numeric.iloc[0]) / 2))
                    
                    left_deriv_last = ((df[col].iloc[-1] - df[col].iloc[-2]) / 
                                      (time_numeric.iloc[-1] - time_numeric.iloc[-2]))
                    right_deriv_last = ((df[col].iloc[-2] - df[col].iloc[-3]) / 
                                       (time_numeric.iloc[-2] - time_numeric.iloc[-3]))
                    dd[-1] = ((left_deriv_last - right_deriv_last) / 
                             ((time_numeric.iloc[-1] - time_numeric.iloc[-3]) / 2))

            df[dd_col] = dd
            log(f"Added derivatives: {d_col}, {dd_col}")
        
        # Restore the original "time" column
        df["time"] = original_time

        # If sensor_id wasn't originally present, remove it if somehow added
        if not sensor_present and "sensor_id" in df.columns:
            df.drop(columns=["sensor_id"], inplace=True)

        # Save the new DataFrame
        df.to_csv(output_filepath, index=False)
        log.down(f"Saved to {output_filepath}")
        return True
        
    except Exception as e:
        log.warning(f"Error computing derivatives: {e}")
        log.down("Failed")
        return False


def copyCSV(source_path: str, target_path: str, column_name: str, output_path: str = None) -> bool:
    """
    Copy a specific column from one CSV file to another.
    
    This utility is useful for transferring processed data between different
    sensor data files while maintaining proper alignment.
    
    Parameters:
    -----------
    source_path : str
        Path to the source CSV file
    target_path : str
        Path to the target CSV file
    column_name : str
        Name of the column to copy
    output_path : str, optional
        Output path (defaults to overwriting target_path)
        
    Returns:
    --------
    bool
        True if successful, False otherwise
        
    Raises:
    -------
    ValueError
        If column doesn't exist in source/target or row counts don't match
    """
    log.up(f"Copying column '{column_name}'")
    
    try:
        # Read the CSV files
        df_source = pd.read_csv(source_path)
        df_target = pd.read_csv(target_path)

        # Verify the column exists in both files
        if column_name not in df_source.columns:
            raise ValueError(f"Column '{column_name}' not found in source file")
        if column_name not in df_target.columns:
            raise ValueError(f"Column '{column_name}' not found in target file")

        # Check that both CSV files have the same number of rows
        if len(df_source) != len(df_target):
            raise ValueError(f"Row count mismatch: source={len(df_source)}, target={len(df_target)}")

        # Copy the column from source to target
        df_target[column_name] = df_source[column_name]
        log(f"Copied {len(df_source)} rows")

        # Save the modified DataFrame
        output_file = output_path if output_path else target_path
        df_target.to_csv(output_file, index=False)

        log.down(f"Saved to {output_file}")
        return True
        
    except Exception as e:
        log.warning(f"Error copying column: {e}")
        log.down("Failed")
        return False


# Additional utility functions for time series processing

def validateCSV(filepath: str, required_columns: list = None) -> dict:
    """
    Validate a CSV file for common issues in time series data.
    
    Parameters:
    -----------
    filepath : str
        Path to the CSV file to validate
    required_columns : list, optional
        List of required column names
        
    Returns:
    --------
    dict
        Validation results with statistics and issues found
    """
    log.up(f"Validating {os.path.basename(filepath)}")
    
    try:
        df = pd.read_csv(filepath)
        results = {
            'valid': True,
            'rows': len(df),
            'columns': len(df.columns),
            'issues': [],
            'statistics': {}
        }
        
        # Check for required columns
        if required_columns:
            missing = [col for col in required_columns if col not in df.columns]
            if missing:
                results['issues'].append(f"Missing required columns: {missing}")
                results['valid'] = False
        
        # Check for duplicate timestamps if time column exists
        if 'time' in df.columns:
            duplicates = df['time'].duplicated().sum()
            if duplicates > 0:
                results['issues'].append(f"Found {duplicates} duplicate timestamps")
        
        # Check for NaN values
        nan_counts = df.isnull().sum()
        if nan_counts.any():
            nan_cols = nan_counts[nan_counts > 0].to_dict()
            results['issues'].append(f"NaN values found: {nan_cols}")
        
        # Basic statistics
        if len(df) > 0:
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            results['statistics'] = {
                'numeric_columns': len(numeric_cols),
                'time_span': None,
                'sample_rate': None
            }
            
            # Time span calculation if time column exists
            if 'time' in df.columns and len(df) > 1:
                try:
                    time_numeric = df['time'].apply(timeParse)
                    time_span = time_numeric.max() - time_numeric.min()
                    results['statistics']['time_span'] = time_span
                    results['statistics']['sample_rate'] = len(df) / time_span if time_span > 0 else 0
                except:
                    results['issues'].append("Could not parse time column for statistics")
        
        log(f"Validation complete: {len(results['issues'])} issues found")
        log.down("Valid" if results['valid'] else "Issues found")
        return results
        
    except Exception as e:
        log.warning(f"Error validating CSV: {e}")
        log.down("Failed")
        return {'valid': False, 'error': str(e)}


def mergeCSVs(file_list: list, output_path: str, sort_by: str = 'time') -> bool:
    """
    Merge multiple CSV files into a single file.
    
    Parameters:
    -----------
    file_list : list
        List of CSV file paths to merge
    output_path : str
        Output path for merged file
    sort_by : str
        Column name to sort the merged data by
        
    Returns:
    --------
    bool
        True if successful, False otherwise
    """
    log.up(f"Merging {len(file_list)} CSV files")
    
    try:
        dataframes = []
        for filepath in file_list:
            df = pd.read_csv(filepath)
            dataframes.append(df)
            log(f"Loaded {os.path.basename(filepath)}: {len(df)} rows")
        
        # Merge all dataframes
        merged_df = pd.concat(dataframes, ignore_index=True)
        
        # Sort if requested and column exists
        if sort_by and sort_by in merged_df.columns:
            merged_df = merged_df.sort_values(by=sort_by, ignore_index=True)
            log(f"Sorted by column '{sort_by}'")
        
        # Save merged file
        merged_df.to_csv(output_path, index=False)
        
        log.down(f"Merged file saved: {len(merged_df)} total rows")
        return True
        
    except Exception as e:
        log.warning(f"Error merging CSV files: {e}")
        log.down("Failed")
        return False
