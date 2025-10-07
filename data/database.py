import pandas as pd
import os

from dotenv import load_dotenv
from sqlalchemy import create_engine, text, Connection, Sequence, Row

from vessel_log import VesselLog


def open_connection() -> Connection:
    load_dotenv()
    engine = create_engine(f"postgresql+psycopg2://{os.getenv('DBUSER')}:{os.getenv('DBPASS')}@{os.getenv('DBHOST')}/{os.getenv('DBNAME')}")
    return engine.connect()

def store_vessel_logs(conn: Connection, file_path):
    imo = os.path.basename(file_path).split('-')[5].split('.')[0]
    df = pd.read_csv(file_path)
    df['imo'] = int(imo)
    df['ts'] = pd.to_datetime(df['# Timestamp'])
    df['lat'] = df['Latitude'].astype(float)
    df['lon'] = df['Longitude'].astype(float)
    df = df[['imo', 'lat', 'lon', 'ts']]
    df.to_sql("vessel_logs", con=conn, if_exists='append', index=False)

def store_vessel(conn: Connection, file_path):
    with open(file_path) as txt_file:
        lines = txt_file.readlines()
        imo = lines[0].strip().split(': ')[1]
        name = lines[1].strip().split(': ')[1]
        ship_type = lines[2].strip().split(': ')[1]
        statement = text("INSERT INTO vessels (imo, name, ship_type) VALUES (:imo, :name, :ship_type) ON CONFLICT (imo) DO NOTHING;")
        conn.execute(statement, {"imo": imo, "name": name, "ship_type": ship_type})


def get_all_vessels():
    conn = open_connection()
    statement = text("SELECT * FROM vessels;")
    result = conn.execute(statement)
    return result.fetchall()

def get_vessel_info(imo: int):
    conn = open_connection()
    statement = text("SELECT * FROM vessels WHERE imo = :imo;")
    result = conn.execute(statement, {"imo": imo})
    return result.fetchone()

def get_vessel_logs(imo: int, start_ts: str, end_ts: str) -> list[VesselLog]:
    conn = open_connection()
    statement = text("SELECT lat, lon, ts FROM vessel_logs WHERE imo = :imo AND ts >= :start_ts AND ts <= :end_ts;")
    result = conn.execute(statement, {"imo": imo, "start_ts": start_ts, "end_ts": end_ts})
    return hydrate_vessel_logs(result.fetchall())

def hydrate_vessel_logs(raw_logs: Sequence[Row]) -> list[VesselLog]:
    return [VesselLog(lat, lon, ts) for lat, lon, ts in raw_logs]