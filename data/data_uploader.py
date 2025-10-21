import glob

from data.database import open_connection, store_vessel, store_vessel_logs


def upload_run():
    conn = open_connection()
    days = ['06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23',
            '24', '25', '26', '27', '28', '29', '30', '31']
    for day in days:
        print(f'Processing day {day}')
        vessel_info_files = glob.glob('raw_data/2024/01/' + day + '/aisdk-2024-*-*-extracted-*-info.txt')
        vessel_log_files = glob.glob('raw_data/2024/01/' + day + '/aisdk-2024-*-*-extracted-*.csv')
        processed_info_files = 0
        processed_log_files = 0
        for vessel_info_file in vessel_info_files:
            store_vessel(conn, vessel_info_file)
            processed_info_files += 1
            if processed_info_files % 10 == 0:
                print(f'Processed {processed_info_files} of {len(vessel_info_files)} vessel info files')

        for vessel_log_file in vessel_log_files:
            store_vessel_logs(conn, vessel_log_file)
            processed_log_files += 1
            if processed_log_files % 10 == 0:
                print(f'Processed {processed_log_files} of {len(vessel_log_files)} vessel log files')