import random
import time
from datetime import datetime, timezone

class VehicleSimulator:
    def __init__(self, client, stops, trips, stop_times):
        self.client = client
        self.stops = stops
        self.trips = trips
        self.stop_times = stop_times

    def simulate_trip(self, trip_id, vehicle_id):
        """
        Simulate a trip for a specific vehicle.
        """
        trip_stops = self.stop_times[self.stop_times["trip_id"] == trip_id].copy()
        trip_stops = trip_stops.sort_values(by="arrival_time")
        trip_stops = trip_stops.merge(self.stops[["stop_id", "stop_lat", "stop_lon", "stop_name"]], on="stop_id", how="left")

        trip_name_row = self.trips[self.trips["trip_id"] == trip_id]
        trip_name = None
        if not trip_name_row.empty:
            if "trip_headsign" in trip_name_row.columns:
                trip_name = trip_name_row.iloc[0]["trip_headsign"]
            elif "trip_short_name" in trip_name_row.columns:
                trip_name = trip_name_row.iloc[0]["trip_short_name"]

        print(f"\n🚍 Starting simulation for Vehicle ID: {vehicle_id}, Trip ID: {trip_id}, Total stops: {len(trip_stops)}\n")

        for index, row in trip_stops.iterrows():
            delay = random.randint(-2, 5)

            # Random wait between 1 and 100 seconds
            wait_time = random.randint(1, 100)
            time.sleep(wait_time)

            # Calling the InfluxDB client
            self.client.write_vehicle_data(
                vehicle_id=vehicle_id,
                trip_id=trip_id,
                stop_id=row['stop_id'],
                lat=row['stop_lat'],
                lon=row['stop_lon'],
                delay=delay,
                stop_name=row.get("stop_name", None),
                trip_name=trip_name
            )

        print(f"✅ Simulation completed for Vehicle ID: {vehicle_id}\n")
