from algcfg import GeneticConfig
from intersections import TFIntersection, AutoIntersection
from roufilebuilder import RouFile
from sumoconfbuilder import SumoConfFile
from population import Population
from tqdm import tqdm
import libsumo as traci
import time
import random
import csv
import os


class GeneticAlgorithm():
    
    def __init__(self, conf : GeneticConfig) -> None:
        self.conf = conf

        self.intersections = self.conf.intersections
        self.populations : list[Population] = []
        
        self.__generate_rou_file()
        self.__generate_conf_file()
        print("==> Sumofiles generated")


    def __generate_rou_file(self):

        rou_file = RouFile()
        # Vehicle type definition
        rou_file.new_vehicle_type("car",1.0,5.0,4.0,2.5,50.0,0.5,"passenger")

        # Routes definition
        for route in self.conf.routes:
            rou_file.new_route(route.label, route.edges) # Nord vers Sud

        # Generate a number of vehicle 
        for i in range(len(self.conf.routes)):
            for j in range(self.conf.routes[i].vehicles):
                rou_file.new_vehicle("veh{}_{}".format(i,j), self.conf.routes[i].label, "car", random.randint(0, self.conf.duration), (1,0,0))

        # Save file
        rou_file.save(self.conf.sumo_folder)
        print("- Rou file generated")


    def __generate_conf_file(self):

        sumo_conf = SumoConfFile(self.conf.net_file)
        sumo_conf.save(self.conf.sumo_folder)
        print("- Conf file generated")

    
    def __generate_initial_pops(self):
        
        for i in range(len(self.intersections)):

            print("==> Creating initial pop for intersection {}".format(self.intersections[i].id), "(intersection of type", type(self.intersections[i]).__name__, ")")
            pop = Population()
            chromosoms = self.intersections[i].get_initial_chromosoms(self.conf.initial_pop_size)

            for j in tqdm(range(len(chromosoms))):
                fitness = self._compute_fitness(i, chromosoms[j])
                pop.insert(chromosoms[j], fitness)
            
            self.populations.append(pop)

        print("==> Initial populations defined")
            
    
    def _compute_fitness(self, intersection_index : int, chromosom : list[float]) -> float:
        
        data_per_vehicule = {}

        # Launch simulation
        conf_file_path = os.path.join(self.conf.sumo_folder, self.conf.sumo_cfg_file)
        if self.conf.gui:
            traci.start(["sumo-gui", "-c", conf_file_path])
        else:
            traci.start(["sumo", "-c", conf_file_path])
        
        # Freeze other intersections with the best chromosom or the default chromosom:
        for i in range(len(self.intersections)):

            if i != intersection_index:

                try:
                    best = self.populations[i].get_best_chrom()
                except:
                    best = self.intersections[i].get_default_chromosom()

                self.intersections[i].apply_chromosom(best)
        
        # Apply chromosom to the good intersection
        self.intersections[intersection_index].apply_chromosom(chromosom)

        # Run simulation step by step and compute cost
        while traci.simulation.getMinExpectedNumber() > 0:

            vehicles_in_inter = self._step(intersection_index)
            
            if self.conf.fitness_mode == "co2":
                for vehicle in vehicles_in_inter:
                    if vehicle in data_per_vehicule:
                        data_per_vehicule[vehicle] += traci.vehicle.getCO2Emission(vehicle)
                    else:
                        data_per_vehicule[vehicle] = traci.vehicle.getCO2Emission(vehicle)
            
            elif self.conf.fitness_mode == "consumption":
                for vehicle in vehicles_in_inter:
                    if vehicle in data_per_vehicule:
                        data_per_vehicule[vehicle] += traci.vehicle.getFuelConsumption(vehicle)
                    else:
                        data_per_vehicule[vehicle] = traci.vehicle.getFuelConsumption(vehicle)

            else:
                for vehicle in vehicles_in_inter:
                    if vehicle in data_per_vehicule:
                        data_per_vehicule[vehicle] += 1
                    else:
                        data_per_vehicule[vehicle] = 1

        traci.close()

        try:
            result = sum(data_per_vehicule.values())
        except:
            result = 10000
        
        return result

    

    def _step(self, watch_inter_id : int) -> list[str]:

        # Step
        traci.simulationStep()

        # Call all callbacks
        for i in range(len(self.intersections)):
            self.intersections[i].step_callback()

        # Get vehicles in the target intersection
        id_and_pos = []
        ids = traci.vehicle.getIDList()
        for id in ids:
            pos = traci.vehicle.getPosition(id)
            id_and_pos.append((id, pos))
        
        vehicles_in_inter = []
        for couple in id_and_pos:
            if self.intersections[watch_inter_id].contains(couple[1]):
                vehicles_in_inter.append(couple[0])
        
        return vehicles_in_inter
    


    def _crossing(self, chromosom_a : list[float], chromosom_b : list[float]) -> list[list[float]]:
        
        parts = self.conf.crossing_points + 1
        loc = int(len(chromosom_a)/parts)

        # Cut chromosoms
        sub_lists_a = []
        sub_lists_b = []
        for i in range(parts):
            if i == parts - 1: 
                sub_lists_a.append(chromosom_a[i * loc:])
                sub_lists_b.append(chromosom_b[i * loc:])
                continue
            sub_lists_a.append(chromosom_a[i * loc: (i+1) * loc])
            sub_lists_b.append(chromosom_b[i * loc: (i+1) * loc])
        
        # Crossing
        chromosom_a = []
        chromosom_b = []
        
        if self.conf.crossing_mode == "random":
            for j in range(len(sub_lists_a)):
                if random.random() <= 0.5:
                    chromosom_a.extend(sub_lists_a[j])
                    chromosom_b.extend(sub_lists_b[j])
                else:
                    chromosom_a.extend(sub_lists_b[j])
                    chromosom_b.extend(sub_lists_a[j])
        else:
            for j in range(len(sub_lists_a)):
                if j%2 == 0:
                    chromosom_a.extend(sub_lists_a[j])
                    chromosom_b.extend(sub_lists_b[j])
                else:
                    chromosom_a.extend(sub_lists_b[j])
                    chromosom_b.extend(sub_lists_a[j])
        
        return [chromosom_a, chromosom_b]
            


    def _update_pops(self):
        
        for i in range(len(self.intersections)):
            parents = self.populations[i].get_parents(self.conf.parents_number)
            children = []

            while len(children) < self.conf.children_number:
                couple = random.choices(parents, k=2)
                crossed = self._crossing(couple[0], couple[1])

                children.append(self.intersections[i].mutation(crossed[0]))
                children.append(self.intersections[i].mutation(crossed[1]))
    
            
            if len(children) > self.conf.children_number:
                children.pop()
            
            for child in children:
                fitness = self._compute_fitness(i, child)
                self.populations[i].insert(child, fitness)

            self.populations[i].del_worst_chromosoms(len(children))
            if self.conf.debug:
                print(self.populations[i])


    def _save_in_csv(self):

        if self.conf.output_file == "":
            return
    
        with open(self.conf.output_file, "a", newline="", encoding="utf-8", errors="replace") as csv_file:
            writer = csv.writer(csv_file)

            for i in range(len(self.intersections)):
                row = [self.intersections[i].id, self.populations[i].get_best_fitness(), self.populations[i].average_fitness(), *self.populations[i].get_best_chrom()]
                writer.writerow(row)


    def run(self):

        start_time = time.time()
        self.__generate_initial_pops()
        self._save_in_csv()

        print("==> Starting training")
        for i in tqdm(range(self.conf.iterations)):
            self._update_pops()
            self._save_in_csv()
        
        end_time = time.time()
        
        for i in range(len(self.intersections)):
            print("The best solution for the", self.intersections[i].id, "intersection is :", self.populations[i].get_best_chrom(), "for", self.intersections[i].get_meaning())

        print("Execution time :", time.strftime("%H hours %M minutes %S seconds", time.gmtime(end_time-start_time)))
        
