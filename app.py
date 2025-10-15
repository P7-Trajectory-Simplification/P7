from flask import Flask, request
from flask import render_template
from sqlalchemy import case
from algorithms.isolate_routes import isolate_routes
from data.database import get_all_vessels, get_vessel_logs
from algorithms.dp import douglas_peucker
from algorithms.squish import squish
from vessel_log import VesselLog
from datetime import datetime

app = Flask(__name__)


vessel_log_cache = {}

def get_needed_data(vessel_number: int, vessel_imo: int, start_time: str, end_time: str, start_time_dt: datetime, end_time_dt: datetime):

    if vessel_number not in vessel_log_cache:

        vessel_log_cache[vessel_number] = [get_vessel_logs(vessel_imo, start_time, end_time)]
        print("Got first data")
        return 0
    else:
        left_chunk_idx = None
        right_chunk_idx = None
        length = len(vessel_log_cache[vessel_number])
        for i in range(0, length):
            chunk = vessel_log_cache[vessel_number][i]
            if chunk[0].ts <= start_time_dt <= chunk[-1].ts:
                left_chunk_idx = i
            if chunk[0].ts <= end_time_dt <= chunk[-1].ts:
                right_chunk_idx = i
                if left_chunk_idx == right_chunk_idx:
                    print("Already had the data")
                    return i
                
        if left_chunk_idx != right_chunk_idx:
            print("Got more data")
            if left_chunk_idx is None:
                del vessel_log_cache[vessel_number][0:right_chunk_idx+1]
                end_time = vessel_log_cache[vessel_number][right_chunk_idx][-1].ts.strftime("%Y-%m-%d %H:%M:%S")
                vessel_log_cache[vessel_number].insert(0,get_vessel_logs(vessel_imo, start_time, end_time))
                return 0
            elif right_chunk_idx is None:
                del vessel_log_cache[vessel_number][left_chunk_idx: length]
                start_time = vessel_log_cache[vessel_number][left_chunk_idx][0].ts.strftime("%Y-%m-%d %H:%M:%S")
                vessel_log_cache[vessel_number].append(get_vessel_logs(vessel_imo, start_time, end_time))
                return len(vessel_log_cache[vessel_number]) - 1
            else:
                del vessel_log_cache[vessel_number][left_chunk_idx:right_chunk_idx+1]
                start_time = vessel_log_cache[vessel_number][left_chunk_idx][0].ts.strftime("%Y-%m-%d %H:%M:%S")
                end_time = vessel_log_cache[vessel_number][right_chunk_idx][-1].ts.strftime("%Y-%m-%d %H:%M:%S")
                vessel_log_cache[vessel_number].insert(left_chunk_idx, get_vessel_logs(vessel_imo, start_time, end_time))
                return left_chunk_idx


def extract_data_from_chunk(chunk: list[VesselLog], start_time_dt: datetime, end_time_dt: datetime) -> list[VesselLog]:
    left_index = None
    right_index = None
    for i in range(0,len(chunk) - 2):
        if chunk[i].ts <= start_time_dt <= chunk[i+1].ts:
            left_index = i
        if chunk[i].ts <= end_time_dt <= chunk[i+1].ts:
            right_index = i
    
    if left_index is None:
        left_index = 0
    if right_index is None:
        right_index = len(chunk) - 1
    return chunk[left_index: right_index + 1]


def get_data(csv_algorithms: str, start_time: str, end_time: str, vessel_number: int = 125):
    start_time_dt = datetime.strptime(start_time, "%Y-%m-%d")
    end_time_dt = datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S")

    vessel_one = get_all_vessels()[vessel_number]
    idx = get_needed_data(vessel_number, vessel_one.imo, start_time, end_time, start_time_dt, end_time_dt)
    needed_data = extract_data_from_chunk(vessel_log_cache[vessel_number][idx], start_time_dt, end_time_dt)
    
    routes = isolate_routes(needed_data)

    algorithms = csv_algorithms.split(',')
    response = {}
    for alg in algorithms:
        match alg:
            #case 'Ours':
            case 'DP':
                simplified_routes = []
                for route in routes:
                    simplified_routes.append(douglas_peucker(route['route'], 0.001))

                response[alg] = routes_to_array(simplified_routes)
            case 'SQUISH':
                simplified_routes = []
                for route in routes:
                    squish(route['route'], route['squish_buff'])
                    temp = []
                    for item in route['squish_buff']:
                        temp.append(item[0])
                    simplified_routes.append(temp)
                response[alg] = routes_to_array(simplified_routes)

            #case 'SQUISH-E':
    temp = []
    for route in routes:
        temp.append(route['route'])

    response['raw'] = routes_to_array(temp)
    return response




def routes_to_array(routes: list[list[VesselLog]]):
    routes_array = []
    for route in routes:
        temp_array = []
        for log in route:
            temp_array.append((log.lat, log.lon, log.ts))
        routes_array.append(temp_array)
    return routes_array


@app.route('/')
def index():
    return render_template('index.html.jinja', algorithms=['Ours', 'SQUISH', 'SQUISH-E', 'DP'])

@app.route('/algorithm')
def get_algorithm_ours():
    algs = request.args.get('algs')
    start_time = request.args.get('start_time')
    end_time = request.args.get('end_time')
    print(start_time)
    print(end_time)
    return get_data(algs, start_time, end_time)