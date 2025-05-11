import threading
import os

from data_loader import load_gtfs_data
from influxdb_wrapper import InfluxDBClientWrapper
from simulator import VehicleSimulator

# InfluxDB config
INFLUX_URL = os.getenv("INFLUX_URL", "http://localhost:8086")
INFLUX_TOKEN = os.getenv("INFLUX_TOKEN", "mytoken")
INFLUX_ORG = os.getenv("INFLUX_ORG", "myorg")
INFLUX_BUCKET = os.getenv("INFLUX_BUCKET", "vehicles")

# Number of trips to simulate
NUMBER_OF_TRIPS = 5

# Run InfluxDB queries or not
RUN_Q = False

# Initialize InfluxDB client
influx_client = InfluxDBClientWrapper(INFLUX_URL, INFLUX_TOKEN, INFLUX_ORG, INFLUX_BUCKET)

# Load related GTFS data for trips
stops, trips, stop_times = load_gtfs_data()

# Initialize simulator
simulator = VehicleSimulator(influx_client, stops, trips, stop_times)

# Entry function for multi-threading
def simulate_for_trip(trip_id, vehicle_id):
    simulator.simulate_trip(trip_id, vehicle_id)

# Select random trips
random_selected_trips = trips.sample(NUMBER_OF_TRIPS).itertuples()

threads = []

print(f"The simulation of the {NUMBER_OF_TRIPS} random trips started.")
 
# Simulate multiple vehicles
for i, trip in enumerate(random_selected_trips):
    vehicle_id = f"veh_{i+1}"
    thread = threading.Thread(target=simulate_for_trip, args=(trip.trip_id, vehicle_id))
    thread.start()
    threads.append(thread)

for t in threads:
    t.join()

print(f"The simulation of the {NUMBER_OF_TRIPS} random trips finnished.")

# Check, whether the gtfs data loaded successfully or not
query = f'from(bucket:"{INFLUX_BUCKET}") |> range(start: -1h)'
result = influx_client.query_api().query(query)
for table in result:
    for record in table.records:
        print(f"Time: {record.get_time()}, Vehicle ID: {record.get_value('vehicle_id')}")
