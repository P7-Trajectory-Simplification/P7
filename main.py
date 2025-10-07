from data.database import get_all_vessels, get_vessel_info, get_vessel_logs
from algorithms.dp import douglas_peucker

vessel_one = get_all_vessels()[125]
print(vessel_one)
vessel_logs = get_vessel_logs(vessel_one.imo, "2024-01-01", "2024-01-31")
#vessel_logs = douglas_peucker(vessel_logs, 0.00001)
#print(len(vessel_logs))



import matplotlib.pyplot as plt

orig_lats = [log.lat for log in vessel_logs]
orig_lons = [log.lon for log in vessel_logs]

print(len(vessel_logs))
simplified = douglas_peucker(vessel_logs, 0.001)
print(len(simplified))

simp_lats = [log.lat for log in simplified]
simp_lons = [log.lon for log in simplified]

plt.figure(figsize=(8, 6))
plt.scatter(orig_lons, orig_lats, s=5, label="Original")
plt.scatter(simp_lons, simp_lats, s=20, label="Simplified", color="red")
plt.legend()
plt.xlabel("Longitude")
plt.ylabel("Latitude")
plt.title("Douglas–Peucker Simplification (Points Only)")
plt.show()
