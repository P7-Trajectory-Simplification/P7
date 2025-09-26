# Ship Data
This directory contains datasets related to ship movements, characteristics, and other maritime information. The data is collected from AIS (Automatic Identification System).
## Raw Data
The raw data files are in CSV format which include various attributes:
- `Timestamp`: The timestamp of the AIS message.
- `Type of mobile`: The type of mobile (e.g., Class A AIS Vessel, Class B AIS vessel).
- `MMSI`: The Maritime Mobile Service Identity number of the vessel.
- `Latitude`: The latitude of the vessel's position.
- `Longitude`: The longitude of the vessel's position.
- `Navigational status`: The navigational status of the vessel (e.g., 'Engaged in fishing', 'Under way using engine').
- `ROT`: Rate of turn.
- `SOG`: Speed over ground.
- `COG`: Course over ground.
- `Heading`: The heading of the vessel.
- `IMO`: The International Maritime Organization number of the vessel.
- `Callsign`: The callsign of the vessel.
- `Name`: The name of the vessel.
- `Ship type`: The type of ship.
- `Cargo type`: The type of cargo.
- `Width`: The width of the vessel.
- `Length`: The length of the vessel.
- `Type of position fixing device`: The type of positional fixing device.
- `Draught`: The draught of the vessel.
- `Destination`: The destination of the vessel.
- `ETA`: Estimated Time of Arrival.
- `Data source type`: The data source type (e.g., AIS).
- `Size A`: Length from GPS to the bow.
- `Size B`: Length from GPS to the stern.
- `Size C`: Length from GPS to starboard side.
- `Size D`: Length from GPS to port side.

In order to reduce the size of the dataset, some columns have been removed from the raw data files. The columns that will be used are:
- `Timestamp`
- `Latitude`
- `Longitude`
- `IMO`
- `Name`
- `Ship type`
- `Destination`
- `ETA`

Furthermore, to reduce individual file size, the data has been split into multiple files, each containing data for a specific vessel.
The CSV files have been sorted into a Hive-style partitioned directory structure based on the year, month, and day. This structure allows for more efficient querying and data retrieval.

These files, due to their size, have been inserted into a database for easier access and querying. The database tables are: vessels and vessel_logs.


## Guide
To replicate the described process, upload the raw CSV files into directories corresponding to their date (year/month/day).\
Then run the script data_processor.processor_run() to process the CSV, i.e. remove irrelevant columns and rows with missing or malformatted data.\
Then run the script data_splitter.split_run() to split the data into multiple files based on the imo number of the ship.\
Finally, run the script data_uploader.upload_run() to upload the processed and split data into the database.