base_url = 'http://aisdata.ais.dk/'
year_directories = ['2006', '2007', '2008', '2009', '2010', '2011', '2012', '2013', '2014', '2015', '2016', '2017', '2018', '2019', '2020', '2021', '2022', '2023', '2024', '2025']
columns = [
    "Timestamp",                        # Timestamp from the AIS basestation, format: 31/12/2015 23:59:59
    "Type of mobile",                   # Describes what type of target this message is received from (class A AIS Vessel, Class B AIS vessel, etc)
    "MMSI",                             # MMSI number of vessel
    "Latitude",                         # Latitude of message report (e.g. 57,8794)
    "Longitude",                        # Longitude of message report (e.g. 17,9125)
    "Navigational status",              # Navigational status from AIS message if available, e.g.: 'Engaged in fishing', 'Under way using engine'
    "ROT",                              # Rate of turn from AIS message if available
    "SOG",                              # Speed over ground from AIS message if available
    "COG",                              # Course over ground from AIS message if available
    "Heading",                          # Heading from AIS message if available
    "IMO",                              # IMO number of the vessel
    "Callsign",                         # Callsign of the vessel
    "Name",                             # Name of the vessel
    "Ship type",                        # Describes the AIS ship type of this vessel
    "Cargo type",                       # Type of cargo from the AIS message
    "Width",                            # Width of the vessel
    "Length",                           # Length of the vessel
    "Type of position fixing device",   # Type of positional fixing device from the AIS message
    "Draught",                          # Draught field from AIS message
    "Destination",                      # Destination from AIS message
    "ETA",                              # Estimated Time of Arrival, if available
    "Data source type",                 # Data source type, e.g. AIS
    "Size A",                           # Length from GPS to the bow
    "Size B",                           # Length from GPS to the stern
    "Size C",                           # Length from GPS to starboard side
    "Size D"                            # Length from GPS to port side
]