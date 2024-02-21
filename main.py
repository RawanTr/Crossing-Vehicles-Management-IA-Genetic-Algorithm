from genetic import GeneticAlgorithm
from algcfg import GeneticConfig
import sys
import os

try:
    config_file = sys.argv[1]
except:
    print("==> You must pass a configuration file as first argument.")
    sys.exit(1)

if not os.path.exists(config_file):
    print("==> The configuration file does not exit.")
    sys.exit(1)

try:
    output_file = sys.argv[2]
except:
    output_file = ""

conf = GeneticConfig()
conf.load_from_file(config_file)
conf.set_output_file_and_mkdirs(output_file)
print("==> Configuration loaded")

alg = GeneticAlgorithm(conf)
alg.run()


