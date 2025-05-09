import pandas as pd

def load_gtfs_data(gtfs_path="budapest_gtfs/"):
    """
    Load GTFS data from the provided directory path.
    Returns three pandas DataFrames: stops, trips, stop_times.
    """
    stops = pd.read_csv(gtfs_path + "stops.txt")
    trips = pd.read_csv(gtfs_path + "trips.txt")
    stop_times = pd.read_csv(gtfs_path + "stop_times.txt")
    
    return stops, trips, stop_times
