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

    def query_recent_vehicle_data(
        self,
        measurement="vehicle_location",
        time_range="-1h",
        vehicle_id=None,
        trip_id=None,
        stop_id=None,
    ):
        """
        Query recent vehicle data from InfluxDB with optional filters.

        Args:
            measurement (str): Name of the measurement to query.
            time_range (str): Time range for the query (e.g., "-1h", "-24h").
            vehicle_id (str): Optional filter by vehicle_id tag.
            trip_id (str): Optional filter by trip_id tag.
            stop_id (str): Optional filter by stop_id tag.
        """

        filters = f'|> range(start: {time_range})\n'
        filters += f'|> filter(fn: (r) => r._measurement == "{measurement}")\n'

        if vehicle_id:
            filters += f'|> filter(fn: (r) => r.vehicle_id == "{vehicle_id}")\n'
        if trip_id:
            filters += f'|> filter(fn: (r) => r.trip_id == "{trip_id}")\n'
        if stop_id:
            filters += f'|> filter(fn: (r) => r.stop_id == "{stop_id}")\n'

        query = f'from(bucket: "{self.bucket}")\n{filters}'

        try:
            result = self.client.query_api().query(query)
            print(f"\n📋 InfluxDB Query Results ({time_range}):\n")
            for table in result:
                for record in table.records:
                    time_str = record.get_time().strftime("%Y-%m-%d %H:%M:%S")
                    print(f"Time: {time_str}, Field: {record.get_field()}, Value: {record.get_value()}, Tags: {record.values}")
        except Exception as e:
            print(f"❌ Error during InfluxDB query: {e}")
