import matplotlib.pyplot as plt
import math
import sys
import csv


try:
    file = sys.argv[1]
except:
    print("==> You must pass a generated csv file as argument")


intersections = {}

with open(file, "r") as csv_file:
    for row in csv.reader(csv_file):
        if row[0] not in intersections:
            intersections[row[0]] = [[float(row[1])],[float(row[2])]]
        else:
            intersections[row[0]][0].append(float(row[1]))
            intersections[row[0]][1].append(float(row[2]))

if len(intersections) == 1:
    key = list(intersections.keys())[0]
    plt.plot(intersections[key][0], marker="o", color="green", label="Best solutions")
    plt.plot(intersections[key][1], marker="o", color="orange", label="Population average")
    plt.title("Evolution of fitness of intersection {}".format(key))
    plt.legend(loc="upper right")
    plt.show()

elif len(intersections) == 2:
    for i, key in enumerate(intersections.keys()):
        plt.subplot(1,2,i+1)
        plt.plot(intersections[key][0], marker="o", color="green", label="Best solutions")
        plt.plot(intersections[key][1], marker="o", color="orange", label="Population average")
        plt.title("Intersection {}".format(key))
        plt.xlabel("Simulation step")
        plt.ylabel("Fitness")
    plt.suptitle("Evolution of fitness")
    plt.tight_layout()
    plt.show()


elif len(intersections) > 2:
    grid_width = math.ceil(math.sqrt(len(intersections)))
    for i, key in enumerate(intersections.keys()):
        plt.subplot(grid_width, grid_width, i+1)
        plt.plot(intersections[key][0], marker="o", color="green", label="Best solutions")
        plt.plot(intersections[key][1], marker="o", color="orange", label="Population average")
        plt.title("Intersection {}".format(key))
        plt.xlabel("Simulation step")
        plt.ylabel("Fitness")
    plt.suptitle("Evolution of fitness")
    plt.tight_layout()
    plt.show()

else:
    print("Error: Cannot plot data")