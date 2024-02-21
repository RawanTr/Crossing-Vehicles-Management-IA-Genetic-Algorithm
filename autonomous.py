from intersections.intersection import Intersection
from copy import deepcopy
import libsumo as traci
import random
import math

class AutoIntersection(Intersection):

    def __init__(self, id: str, center: list[float], visibility: float, mutation_proba : float, mutation_max : int, from_edges_id: list[str],
                  from_edges_len: list[float], to_edges_id : list[str], edge_priority_range: float, maximum : int) -> None:
        super().__init__(id, center, visibility, mutation_proba, mutation_max)

        self.from_edges_id = from_edges_id
        self.from_edges_len = from_edges_len
        self.to_edges_id = to_edges_id

        self.maximum = maximum
        self.max_vehicles = []
        self.priorities = []

        self.waiting_time = {}
        self.cursor = random.randint(0,len(from_edges_id)-1)
        self.edge_priority_range = edge_priority_range
        #the vehicles that will cross the intersection
        self.veh_tocross = []
    

    def mutation(self, chromosom : list[float]) -> list[float]:

        rand_number = random.random()
        if rand_number > self.mutation_proba:
            return chromosom
        
        rand_index = random.randint(0, len(chromosom)-1)
        rand_modif = random.randint(1, self.mutation_max)
        rand_number = random.random()
        if rand_number >= 0.5:
            if chromosom[rand_index] - rand_modif >= 1:
                chromosom[rand_index] -= rand_modif
        else:
            chromosom[rand_index] += rand_modif
            
        return self.sanitize_chromosom(chromosom)
    

    def sanitize_chromosom(self, chromosom : list[float]) -> list[float]:

        for i in range(len(chromosom)):
            if chromosom[i] > self.maximum:
                chromosom[i] = self.maximum

        return chromosom
    

    def get_initial_chromosoms(self, n : int) -> list[list[float]]:

        initials = []
        for i in range(n):
            initials.append([random.randint(1, self.maximum) for j in range(len(self.from_edges_id))])
        
        return initials
   
    
    def get_default_chromosom(self) -> list[float]:

        avg_vehicles_nb = int(self.max_vehicles / 2)
        return [avg_vehicles_nb for i in range(len(self.edges))]


    def apply_chromosom(self, chromosom : list[float]):
        self.max_vehicles = chromosom


    def step_callback(self, *args):
        
        self._update_waiting_time()

        if len(self.veh_tocross) == 0:
            self._update_priorities()
            self._switch_edge()
            self._update_veh_tocross()

        self._verify_vehicles_tocross()
        self._maintain_stop()

    
    def get_edges(self):
        return self.from_edges_id

    
    def _update_waiting_time(self):
        
        for i in range(len(self.from_edges_id)):
            veh_and_dists = self._get_veh_and_dist_on_edge(self.from_edges_id[i])
            vehicles = [couple[0] for couple in veh_and_dists]
            for vehicle in vehicles:
                if vehicle not in self.waiting_time:
                    self.waiting_time[vehicle] = 1
                else:
                    self.waiting_time[vehicle] += 1


    #set stop for the lanes
    def _maintain_stop(self):
        
        for i in range(len(self.from_edges_id)):
            veh_and_dists = self._get_veh_and_dist_on_edge(self.from_edges_id[i])
            vehicles = [couple[0] for couple in veh_and_dists]
            stop = self.from_edges_len[i]-2
            
            for vehicle in vehicles:
                if vehicle not in self.veh_tocross:
                    traci.vehicle.setStop(vehicle, self.from_edges_id[i], stop, duration=10, startPos=stop, until=10)
                else:
                    try:
                        traci.vehicle.setStop(vehicle, self.from_edges_id[i], stop, duration=0, startPos=stop, until=0)
                    except:
                        pass



    #renvoyer la liste des vehicules sur une voie en ordre de plus proche au plus loin
    def _get_veh_and_dist_on_edge(self, edge_id : str):

        veh_and_dists = []

        vehicules = traci.vehicle.getIDList()
        for veh in vehicules:
            lane = traci.vehicle.getLaneID(veh).split("_")[0]
            if lane == edge_id:
                dist = self._distance(traci.vehicle.getPosition(veh))
                if dist <= self.edge_priority_range:
                    veh_and_dists.append((veh, dist))

        return sorted(veh_and_dists, key= lambda x: x[1])
        
    
    def _verify_vehicles_tocross(self):

        leaving_vehicles = []
        for edge in self.to_edges_id:
            leaving_vehicles.extend(self._get_veh_and_dist_on_edge(edge))
        
        for couple in leaving_vehicles:
            if couple[0] in self.veh_tocross and couple[1] > 8.0:
                self.veh_tocross.remove(couple[0])

            
    #les vehicules qui doivent passer
    def _update_veh_tocross(self):

        number = self.max_vehicles[self.cursor]
        veh_and_dists = self._get_veh_and_dist_on_edge(self.from_edges_id[self.cursor])

        vehicles_tocross = [couple[0] for couple in veh_and_dists][:number]
        for veh in vehicles_tocross:
            del self.waiting_time[veh]
            

        self.veh_tocross = vehicles_tocross
        



    def _distance(self, pos):
        return math.sqrt(math.pow((pos[0]-self.center.x),2)+math.pow((pos[1]-self.center.y),2))


    #changer de voie
    def _switch_edge(self):

        other_edges_id = deepcopy(self.from_edges_id)
        other_priorities = deepcopy(self.priorities)

        other_edges_id.pop(self.cursor)
        other_priorities.pop(self.cursor)
        
        new_selected_id = other_edges_id[other_priorities.index(max(other_priorities))]
        self.cursor = self.from_edges_id.index(new_selected_id)


    def _update_priorities(self):
        
        new_priorities = []
        for edge in self.from_edges_id:
            veh_and_dists = self._get_veh_and_dist_on_edge(edge)
            priority = 0
            for couple in veh_and_dists:
                priority += ((self.visibility - couple[1]) + (self.waiting_time[couple[0]] * 2))
            new_priorities.append(priority)

        self.priorities = new_priorities
