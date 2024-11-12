import argparse
import datetime
import gpxpy.gpx
import math


def generate_gpx(coordinate, start_time, duration, elevation_gain):
    # Parse inputs
    lat, lon = map(float, coordinate.split(","))
    duration_parts = list(map(int, duration.split(":")))
    total_seconds = (
        duration_parts[0] * 3600 + duration_parts[1] * 60 + duration_parts[2]
    )

    base_elevation = 500  # Starting elevation in meters
    elevation_per_second = (
        elevation_gain / total_seconds
    )  # Constant elevation gain per second
    radius = (
        1 / 111139
    )  # Approximate 1-meter radius in degrees (1 degree latitude ~ 111.139 km)
    angular_speed = (
        0.1 / radius
    )  # Angular speed for 0.1 m/s around the 1-meter radius circle

    # Initialize GPX file
    gpx = gpxpy.gpx.GPX()
    gpx_track = gpxpy.gpx.GPXTrack()
    gpx.tracks.append(gpx_track)
    gpx_segment = gpxpy.gpx.GPXTrackSegment()
    gpx_track.segments.append(gpx_segment)

    # Generate GPX points with circular movement and steady elevation gain
    for i in range(total_seconds):
        timestamp = start_time + datetime.timedelta(seconds=i)

        # Calculate circular movement
        angle = angular_speed * i  # Angle in radians for circular path
        lat_offset = radius * math.cos(angle)
        lon_offset = (
            radius * math.sin(angle) / math.cos(math.radians(lat))
        )  # Adjust for Earth's curvature...

        elevation = base_elevation + elevation_per_second * i

        point = gpxpy.gpx.GPXTrackPoint(
            latitude=lat + lat_offset,
            longitude=lon + lon_offset,
            elevation=elevation,
            time=timestamp,
        )
        gpx_segment.points.append(point)

    # Save GPX file
    with open("stairmaster_activity.gpx", "w") as f:
        f.write(gpx.to_xml())

    print("GPX file 'stairmaster_activity.gpx' generated successfully.")


def main():
    parser = argparse.ArgumentParser(
        description="Generate a GPX file for a stairmaster activity."
    )
    parser.add_argument(
        "--coordinate",
        type=str,
        default="48.26483115244917,11.672326802248373",
        help="Starting coordinate as 'latitude,longitude'",
    )
    parser.add_argument(
        "--start_time",
        type=str,
        default=datetime.datetime.now().strftime("%H:%M:%S"),
        help="Starting time in HH:MM:SS format",
    )
    parser.add_argument(
        "--start_date",
        type=str,
        default=datetime.datetime.now().strftime("%Y-%m-%d"),
        help="Starting date in YYYY-MM-DD format",
    )
    parser.add_argument(
        "--duration",
        type=str,
        required=True,
        help="Duration of the activity in HH:MM:SS format",
    )
    parser.add_argument(
        "--elevation_gain", type=float, help="Total elevation gain in meters"
    )
    parser.add_argument(
        "--floors", type=int, help="Number of floors climbed (each floor is 3.5 meters)"
    )

    args = parser.parse_args()

    # Calculate elevation gain based on floors if elevation_gain is not provided
    elevation_gain = args.elevation_gain
    if elevation_gain is None and args.floors is not None:
        elevation_gain = args.floors * 3.5
    elif elevation_gain is None:
        parser.error("You must specify either --elevation_gain or --floors.")

    # Parse start time and date
    start_time_str = f"{args.start_date} {args.start_time}"
    start_time = datetime.datetime.strptime(start_time_str, "%Y-%m-%d %H:%M:%S")

    # Generate GPX file
    generate_gpx(args.coordinate, start_time, args.duration, elevation_gain)
    print("GPX file generated: stairmaster_activity.gpx")


if __name__ == "__main__":
    main()
