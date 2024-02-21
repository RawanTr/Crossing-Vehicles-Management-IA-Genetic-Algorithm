from roufilebuilder import Route
from intersections import TFIntersection, Intersection , AutoIntersection
import sumolib
import json
import csv
import os

class GeneticConfig():

    def __init__(self) -> None:

        # Sumo's configuration
        self.gui = False
        self.debug = False
        self.sumo_folder = "sumofiles"
        self.sumo_cfg_file = "conf.sumocfg"
        self.net_file = "unknown.net.xml"
        self.duration = 600
        self.fitness_mode = ""

        # Genetic algorithm's configuration
        self.iterations = 100
        self.parents_number = 4
        self.children_number = 4
        self.crossing_points = 1
        self.crossing_mode = "classic"
        self.initial_pop_size = 8

        # Output CSV file
        self.output_file = ""

        # Network
        self.net = None

        # Intersections and routes
        self.intersections = []
        self.routes = []


    def load_from_file(self, file : str = "config.json"):
        with open(file, 'r') as json_file:
            values = json.load(json_file)

        # Sumo configuration 
        self.gui = values["gui"]
        self.debug = values["debug"]
        self.sumo_folder = values["sumo_folder"]
        self.sumo_cfg_file = values["sumo_cfg_file"]
        self.net_file = values["net_file"]
        self.duration = values["duration"]
        self.fitness_mode = values["fitness_mode"]

        # Genetic algorithm's configuration
        self.iterations = values["iterations"]
        self.parents_number = values["parents_number"]
        self.children_number = values["children_number"]
        self.crossing_points = values["crossing_points"]
        self.crossing_mode = values["crossing_mode"]
        self.initial_pop_size = values["initial_pop_size"]

        self.net = sumolib.net.readNet(os.path.join(self.sumo_folder, self.net_file))

        # Intersections and routes
        self.intersections = [self._load_intersection(inter) for inter in values["intersections"]]
        self.routes = [self._load_route(rou) for rou in values["routes"]]

        # Unload network
        self.net = None


    def set_output_file_and_mkdirs(self, fp : str):

        if fp != "":
            if os.path.dirname(fp) != "":
                os.makedirs(os.path.dirname(fp), exist_ok=True)
            with open(fp, "w") as csv_file:
                pass
        self.output_file = fp
            


    def _load_route(self, route : dict) -> Route:
        return Route(route["label"], route["vehicles"], route["edges"])


    def _load_intersection(self, inter : dict) -> Intersection:
        
        if inter["kind"] == "tf":
            return TFIntersection(
                inter["id"],
                self.net.getNode(inter["id"]).getCoord(),
                inter["visibility"],
                inter["mutation_proba"],
                inter["mutation_max"],
                inter["id"],
                inter["phases"],
                inter["min_phase_time"],
                inter["cycle_time"]
            )
        if inter["kind"] == "auto":

            from_edges_id=[]
            from_edges_len=[]
            to_edges_id = []

            edges = self.net.getEdges()
            for edge in edges:
                if edge.getToNode().getID() == inter["id"]:
                    from_edges_id.append(edge.getID())
                    from_edges_len.append(edge.getLength())
                    continue
                
                if edge.getFromNode().getID() == inter["id"]:
                    to_edges_id.append(edge.getID())
            

            return AutoIntersection(
                inter["id"],
                self.net.getNode(inter["id"]).getCoord(),
                inter["visibility"],
                inter["mutation_proba"],
                inter["mutation_max"],
                from_edges_id,
                from_edges_len,
                to_edges_id,
                inter["edge_priority_range"],
                inter["maximum"],
            )
        # Others intersections...
        