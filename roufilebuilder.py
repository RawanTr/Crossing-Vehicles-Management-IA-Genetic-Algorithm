import os

class Route():

    def __init__(self, label : str, vehicles : int, edges : list[str]) -> None:
        self.label = label
        self.vehicles = vehicles
        self.edges = edges



class RouFile():

    def __init__(self) -> None:
        self.rows = ["<routes>"]
        self.vehicles = []
        
    def new_route(self, id : str, edges : list):
        edge_str = ""
        for edge in edges:
            edge_str = edge_str + str(edge) + " "
        self.rows.append("\t<route id=\"{}\" edges=\"{}\"/>".format(id, edge_str))

    def new_vehicle_type(self, id : str, accel : float, decel : float, length : float , minGap : float, maxSpeed : float, sigma : float, gui_shape : str) -> str:
        self.rows.append("\t<vType id=\"{}\" accel=\"{}\" decel=\"{}\" length=\"{}\" minGap=\"{}\" maxSpeed=\"{}\" sigma=\"{}\"/>".format(id, accel,
            decel, length, minGap, maxSpeed, sigma, gui_shape))


    def new_vehicle(self, id : str, route_id : str, type_id : str, depart : int, color_rgb : tuple = (1,1,1)):
        color_str = "{},{},{}".format(color_rgb[0], color_rgb[1], color_rgb[2])
        self.vehicles.append((depart, "\t<vehicle depart=\"{}\" id=\"{}\" route=\"{}\" type=\"{}\" color=\"{}\"/>".format(depart, id, route_id, type_id, color_str)))


    def save(self, folder : str, name : str = "generated.rou.xml"):
        
        sorted_vehicles = sorted(self.vehicles, key=lambda x : x[0])
        vehicle_balises = [x[1] for x in sorted_vehicles]
        self.rows.extend(vehicle_balises)
        self.rows.append("</routes>")

        with open(os.path.join(folder, name),"w") as rou_file:
            for row in self.rows:
                rou_file.write(row + "\n")
