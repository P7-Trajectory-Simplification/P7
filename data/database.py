from datetime import datetime

import pandas as pd
import os

from dotenv import load_dotenv
from sqlalchemy import create_engine, text, Connection, Sequence, Row

from classes.vessel import Vessel
from classes.vessel_log import VesselLog


def open_connection() -> Connection:
    load_dotenv()
    engine = create_engine(
        f'postgresql+psycopg2://{os.getenv("DBUSER")}:{os.getenv("DBPASS")}@{os.getenv("DBHOST")}/{os.getenv("DBNAME")}'
    )
    return engine.connect()


def store_vessel_logs(conn: Connection, file_path):
    imo = os.path.basename(file_path).split('-')[5].split('.')[0]
    df = pd.read_csv(file_path)
    df['imo'] = int(imo)
    df['ts'] = pd.to_datetime(df['# Timestamp'])
    df['lat'] = df['Latitude'].astype(float)
    df['lon'] = df['Longitude'].astype(float)
    df = df[['imo', 'lat', 'lon', 'ts']]
    df.to_sql('vessel_logs', con=conn, if_exists='append', index=False)


def store_vessel(conn: Connection, file_path):
    with open(file_path) as txt_file:
        lines = txt_file.readlines()
        imo = lines[0].strip().split(': ')[1]
        name = lines[1].strip().split(': ')[1]
        ship_type = lines[2].strip().split(': ')[1]
        statement = text(
            'INSERT INTO vessels (imo, name, ship_type) VALUES (:imo, :name, :ship_type) ON CONFLICT (imo) DO NOTHING;'
        )
        conn.execute(statement, {'imo': imo, 'name': name, 'ship_type': ship_type})


def get_all_vessels() -> list[Vessel]:
    conn = open_connection()
    statement = text('SELECT * FROM vessels;')
    result = conn.execute(statement)
    return hydrate_vessels(result.fetchall())


def get_vessel_logs(imo: int, start_ts: datetime, end_ts: datetime) -> list[VesselLog]:
    start_time = start_ts.strftime('%Y-%m-%d %H:%M:%S')
    end_time = end_ts.strftime('%Y-%m-%d %H:%M:%S')
    conn = open_connection()
    statement = text(
        'SELECT imo, lat, lon, ts, id FROM vessel_logs WHERE imo = :imo AND ts >= :start_ts AND ts <= :end_ts ORDER BY ts;'
    )
    result = conn.execute(
        statement, {'imo': imo, 'start_ts': start_time, 'end_ts': end_time}
    )
    return hydrate_vessel_logs(result.fetchall())


def hydrate_vessel_logs(raw_logs: Sequence[Row]) -> list[VesselLog]:
    return [VesselLog(lat, lon, ts, imo, id) for imo, lat, lon, ts, id in raw_logs]


def hydrate_vessels(raw_vessel: Sequence[Row]) -> list[Vessel]:
    return [Vessel(imo, name, ship_type) for imo, name, ship_type in raw_vessel]
