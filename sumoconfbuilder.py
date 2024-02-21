import os

class SumoConfFile():
    def __init__(self, net_file_path : str, rou_file_path : str = "generated.rou.xml" ) -> None:
        self.rows = [
            "<?xml version=\"1.0\" encoding=\"UTF-8\"?>",
            "<configuration xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\" xsi:noNamespaceSchemaLocation=\"http://sumo.dlr.de/xsd/sumoConfiguration.xsd\">",
            "\t<input>",
            "\t\t<net-file value=\"{}\"/>".format(net_file_path),
            "\t\t<route-files value=\"{}\"/>".format(rou_file_path),
            "\t\t<gui-settings-file value=\"gui_settings_file.xml\"/>",
            "\t</input>",
            "</configuration>"
        ]
    
    def save(self, folder : str, name : str = "config.sumocfg"):
        with open(os.path.join(folder, name),"w") as rou_file:
            for row in self.rows:
                rou_file.write(row + "\n")