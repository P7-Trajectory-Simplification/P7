import datetime

from sqlalchemy import text

from algorithms.isolate_routes import isolate_routes
from classes.route import Route
from data.database import open_connection, get_vessel_logs


def find_vessels_with_most_vessel_logs(top_n: int) -> list[tuple[int, int]]:
    conn = open_connection()
    statement = text(
        'SELECT imo, COUNT(*) as log_count FROM vessel_logs GROUP BY imo ORDER BY log_count DESC LIMIT :top_n;'
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

    with open('isolated_routes.json', 'w') as json_file:
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

    with open('isolated_routes.json', 'r') as json_file:
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

if __name__ == '__main__':
    top_n = 200
    #results = find_vessels_with_most_vessel_logs(top_n)
    #save_results_to_json(results)
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
