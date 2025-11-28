import datetime
import os
from pathlib import Path

from sqlalchemy import text

from algorithms.isolate_routes import isolate_routes
from classes.vessel_log import VesselLog
from data.database import open_connection, get_vessel_logs


def find_vessels_with_most_vessel_logs(top_n: int) -> list[tuple[int, int]]:
    conn = open_connection()
    statement = text(
        'SELECT imo, COUNT(*) as log_count FROM vessel_logs WHERE lat != 91 GROUP BY imo ORDER BY log_count DESC LIMIT :top_n'
    )
    result = conn.execute(statement, {'top_n': top_n})
    return [(imo, log_count) for imo, log_count in result.fetchall()]


def save_results_to_json(results: list[tuple[int, int]]):
    import json

    with open('vessels_with_most_logs.json', 'w') as json_file:
        json.dump(
            [{'imo': imo, 'log_count': log_count} for imo, log_count in results],
            json_file,
            indent=4,
        )

def load_results_from_json() -> list[tuple[int, int]]:
    import json

    with open('vessels_with_most_logs.json', 'r') as json_file:
        data = json.load(json_file)
    return [(item['imo'], item['log_count']) for item in data]

def save_routes_to_json(routes: list[dict]):
    import json
    base_dir = Path(__file__).resolve().parent  # .../P7/experiments
    filepath = os.path.join(base_dir, "isolated_routes.json")

    with open(filepath, 'w') as json_file:
        json.dump(
            [
                {
                    'imo': route['imo'],
                    'log_count': route['log_count'],
                    'start_ts': route['start_ts'].isoformat(),
                    'end_ts': route['end_ts'].isoformat(),
                }
                for route in routes
            ],
            json_file,
            indent=4,
        )

def load_routes_from_json() -> list[dict]:
    import json
    from dateutil import parser
    base_dir = Path(__file__).resolve().parent  # .../P7/experiments
    filepath = os.path.join(base_dir, "isolated_routes.json")

    with open(filepath, 'r') as json_file:
        data = json.load(json_file)
    return [
        {
            'imo': route['imo'],
            'log_count': route['log_count'],
            'start_ts': parser.isoparse(route['start_ts']),
            'end_ts': parser.isoparse(route['end_ts']),
        }
        for route in data
    ]


def save_route_data_to_json(trajectories: list[VesselLog], filename: str):
    import json

    base_dir = Path(__file__).resolve().parent  # .../P7/experiments
    route_data_path = os.path.join(base_dir, "route_data") # .../P7/experiments/route_data
    os.makedirs(route_data_path, exist_ok=True)
    filepath = os.path.join(route_data_path, filename)

    with open(filepath, 'w+') as json_file:
        json.dump(
            [
                {
                    'imo': log.imo,
                    'ts': log.ts.isoformat(),
                    'lat': log.lat,
                    'lon': log.lon,
                    'id': log.id,
                }
                for log in trajectories
            ],
            json_file,
            indent=4,
        )

def load_route_data_from_json(filename: str) -> list[VesselLog]:
    import json
    from dateutil import parser
    base_dir = Path(__file__).resolve().parent  # .../P7/experiments
    route_data_dir = os.path.join(base_dir, "route_data") # .../P7/experiments/route_data
    filepath = os.path.join(route_data_dir, filename)

    with open(filepath, 'r') as json_file:
        data = json.load(json_file)
    return [
        VesselLog(
            imo=log['imo'],
            ts=parser.isoparse(log['ts']),
            lat=log['lat'],
            lon=log['lon'],
            id=log['id'],
        )
        for log in data
    ]

def get_routes_info():
    top_n = 200
    results = find_vessels_with_most_vessel_logs(top_n)
    save_results_to_json(results)
    vessels = load_results_from_json()
    routes = []
    counter = 0
    for imo, log_count in vessels:
        vessel_logs = get_vessel_logs(
            imo=imo,
            start_ts=datetime.datetime(2024, 1, 1),
            end_ts=datetime.datetime(2024, 1, 31),
        )
        isolated_routes = isolate_routes(vessel_logs)
        for isolated_route in isolated_routes:
            routes.append({
                'imo': imo,
                'log_count': log_count,
                'start_ts': isolated_route.trajectory[0].ts,
                'end_ts': isolated_route.trajectory[-1].ts,
            })
        counter += 1
        print("Processed vessels", counter)

    sorted_routes = sorted(routes, key=lambda route: route['log_count'], reverse=True)
    save_routes_to_json(sorted_routes[:top_n])

def get_route_data():
    routes = load_routes_from_json()
    counter = 0
    for route in routes:
       print(str(counter) + "/" + str(len(routes)))
       vessel_logs = get_vessel_logs(
           imo=route['imo'],
           start_ts=route['start_ts'],
           end_ts=route['end_ts'],
       )
       save_route_data_to_json(
           vessel_logs,
           f"imo_{route['imo']}_start_{route['start_ts'].date()}_end_{route['end_ts'].date()}.json"
       )
       counter += 1

if __name__ == '__main__':
    #get_routes_info()
    get_route_data()
