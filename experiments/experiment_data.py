import datetime
import os

from sqlalchemy import text

from algorithms.isolate_routes import isolate_trajectories, is_vessel_static
from classes.vessel_log import VesselLog
import json
from dateutil import parser

from data.database import get_vessel_logs, open_connection


def download_trajectories_from_db(
    num_trajectories: int, data_directory: str, min_points: int, max_points: int
):
    print("Finding vessel IMOs with sufficient data points...")
    conn = open_connection()
    statement = text(
        "SELECT imo, COUNT(*) as log_count "
        "FROM vessel_logs "
        "WHERE lat < 90 AND lat > -90 AND lon < 180 AND lon > -180 "
        "GROUP BY imo "
        "HAVING COUNT(*) BETWEEN 20000 AND 500000 "
        "ORDER BY log_count ASC"
    )
    result = conn.execute(statement)

    """
    We get all vessel IMOs that have log counts between min_points and max_points.
    """
    vessel_imos = [imo for imo, log_count in result.fetchall()]

    print(f"Found {len(vessel_imos)} vessel IMOs with sufficient data points.")

    print("Downloading vessel logs and isolating trajectories...")

    num_of_saved_trajectories = 0
    for imo in vessel_imos:
        if num_of_saved_trajectories == num_trajectories:
            break

        """Download vessel logs for the given IMO"""
        vessel_logs = get_vessel_logs(
            imo=imo,
            start_ts=datetime.datetime(2024, 1, 1),
            end_ts=datetime.datetime(2024, 1, 31),
        )

        valid = True
        for log in vessel_logs:
            if not (-90 <= log.lat <= 90 and -180 <= log.lon <= 180):
                valid = False
                break
        if not valid:
            continue

        """
        Split vessel logs into isolated trajectories
        T = isolated trajectory
        """
        for T in isolate_trajectories(vessel_logs):
            if min_points <= len(T) <= max_points and not is_vessel_static(T):
                """Save trajectory to file"""
                data_file_name = (
                    f"imo_{T[0].imo}_start_{T[0].ts.date()}_end_{T[-1].ts.date()}.json"
                )
                write_trajectory_to_json(
                    T, os.path.join(data_directory, data_file_name)
                )
                """Increment number of saved trajectories and check if we reached the limit"""
                num_of_saved_trajectories += 1

                print(
                    f"Saved trajectory {data_file_name} with {len(T)} points. Total saved: {num_of_saved_trajectories}/{num_trajectories}"
                )

                if num_of_saved_trajectories == num_trajectories:
                    break


def write_trajectory_to_json(trajectory: list[VesselLog], filepath: str):
    with open(filepath, "w+") as json_file:
        json.dump(
            [
                {
                    "imo": log.imo,
                    "ts": log.ts.isoformat(),
                    "lat": log.lat,
                    "lon": log.lon,
                    "id": log.id,
                }
                for log in trajectory
            ],
            json_file,
            indent=4,
        )


def read_trajectory_from_json(filepath: str) -> list[VesselLog]:
    with open(filepath, "r") as json_file:
        data = json.load(json_file)
    return [
        VesselLog(
            imo=log["imo"],
            ts=parser.isoparse(log["ts"]),
            lat=log["lat"],
            lon=log["lon"],
            id=log["id"],
        )
        for log in data
    ]
