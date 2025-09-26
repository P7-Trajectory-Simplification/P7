import pandas as pd
import psycopg2
import os

from dotenv import load_dotenv
from sqlalchemy import create_engine

def open_connection():
    load_dotenv()
    conn = psycopg2.connect(
        dbname=os.getenv("DBNAME"),
        user=os.getenv("DBUSER"),
        password=os.getenv("DBPASS"),
        host=os.getenv("DBHOST"),
        port=5432
    )
    cur = conn.cursor()
    return conn, cur


def close_connection(conn, cur):
    cur.close()
    conn.close()


def execute_query(conn, cur, query, params=None):
    cur.execute(query, params)
    conn.commit()

def store_vessel_logs(file_path):
    engine = create_engine(f"postgresql+psycopg2://{os.getenv('DBUSER')}:{os.getenv('DBPASS')}@{os.getenv('DBHOST')}/{os.getenv('DBNAME')}")

    imo = os.path.basename(file_path).split('-')[5].split('.')[0]
    df = pd.read_csv(file_path)
    df['imo'] = int(imo)
    df['ts'] = pd.to_datetime(df['# Timestamp'])
    df['lat'] = df['Latitude'].astype(float)
    df['lon'] = df['Longitude'].astype(float)
    df = df[['imo', 'lat', 'lon', 'ts']]
    df.to_sql("vessel_logs", con=engine.connect(), if_exists='append', index=False)

def store_vessel(conn, cur, file_path):
    with open(file_path) as txt_file:
        lines = txt_file.readlines()
        imo = int(lines[0].strip().split(': ')[1])
        name = lines[1].strip().split(': ')[1]
        ship_type = lines[2].strip().split(': ')[1]
        query = "INSERT INTO vessels (imo, name, ship_type) VALUES (%s, %s, %s) ON CONFLICT (imo) DO NOTHING;"
        execute_query(conn, cur, query, (imo, name, ship_type))