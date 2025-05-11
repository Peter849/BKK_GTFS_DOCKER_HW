from influxdb_client import InfluxDBClient, Point, WritePrecision
from datetime import datetime, timezone

class InfluxDBClientWrapper:
    def __init__(self, url, token, org, bucket):
        self.client = InfluxDBClient(url=url, token=token, org=org)
        self.write_api = self.client.write_api()
        self.bucket = bucket
        self.org = org

    def write_vehicle_data(self, vehicle_id, trip_id, stop_id, lat, lon, delay):
        """
        Write data about a vehicle's location and delay to InfluxDB.
        """

        current_datetime = datetime.now(timezone.utc).replace(tzinfo=None)

        point = (
            Point("vehicle_location")
            .tag("vehicle_id", vehicle_id)
            .tag("trip_id", trip_id)
            .tag("stop_id", stop_id)
            .field("latitude", lat)
            .field("longitude", lon)
            .field("delay", delay)
            .time(current_datetime, WritePrecision.S)
        )
        try:
            self.write_api.write(bucket=self.bucket, org=self.org, record=point)
            
            log_message = f"""
            ✅ Measured VEHICLE LOCATION DATA for {vehicle_id} written to InfluxDB:
                • Tags:    vehicle_id={vehicle_id}, trip_id={trip_id}, stop_id={stop_id}
                • Fields:  lat={lat}, lon={lon}, delay={delay}
                • Current time:    {current_datetime.isoformat()}
            """
            print(log_message)
        except Exception as e:
            print(f"❌ Exception raised during InfluxDB write at {current_datetime}:\n{e}")
