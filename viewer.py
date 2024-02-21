from algcfg import GeneticConfig
from roufilebuilder import RouFile
from sumoconfbuilder import SumoConfFile
import libsumo as traci
import random
import time
import sys
import os

try:
    conf_file = sys.argv[1]
except:
    print("==> You must pass a configuration file as argument")

conf = GeneticConfig()
conf.load_from_file(conf_file)

# Generate rou file
rou_file = RouFile()
# Vehicle type definition (same type in genetic algorithm )
rou_file.new_vehicle_type("car",1.0,5.0,4.0,2.5,50.0,0.5,"passenger")

for route in conf.routes:
    rou_file.new_route(route.label, route.edges) # Nord vers Sud

for i in range(len(conf.routes)):
    for j in range(conf.routes[i].vehicles):
        rou_file.new_vehicle("veh{}_{}".format(i,j), conf.routes[i].label, "car", random.randint(0, conf.duration), (1,0,0))

rou_file.save(conf.sumo_folder)
print("- Rou file generated")


sumo_conf = SumoConfFile(conf.net_file)
sumo_conf.save(conf.sumo_folder)
print("- Conf file generated")


chromosoms = []
for inter in conf.intersections:
    print("==> Enter chromosome for intersection", inter.id, "(type :", type(inter).__name__, ")")
    csv_chrom = str(input())
    splited_chrom = csv_chrom.split(",")
    chromosoms.append([int(value) for value in splited_chrom])

sumo_cfg = os.path.join(conf.sumo_folder, conf.sumo_cfg_file)
traci.start(["sumo-gui", "-c", sumo_cfg])

for i in range(len(conf.intersections)):
    conf.intersections[i].apply_chromosom(chromosoms[i])

while traci.simulation.getMinExpectedNumber() > 0:
    traci.simulationStep() 
    for j in range(len(conf.intersections)):
        conf.intersections[j].step_callback()
    time.sleep(1)



