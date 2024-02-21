from copy import deepcopy

class Population():

    def __init__(self) -> None:
        self.data = []


    def insert(self, chromosom : list[float], fitness : float):

        chromosom = deepcopy(chromosom)
        i = 0
        while i < len(self.data) and fitness > self.data[i][1]:
            i += 1

        self.data.insert(i, [chromosom, fitness])


    def join(self, other):
        
        data = deepcopy(other.data)
        for couple in data:
            self.insert(couple[0], couple[1])


    def del_worst_chromosoms(self, n : int):
        
        max_del = min(n, len(self.data))
        for i in range(max_del):
            self.data.pop()


    def get_best_chrom(self) -> list[float]:
        return deepcopy(self.data[0][0])
    
    def get_best_fitness(self) -> float:
        return self.data[0][1]
    
    
    def get_parents(self, n) -> list[list[float]]:

        parents = []
        for i in range(n):
            parents.append(deepcopy(self.data[i][0]))
        return parents
    
    def average_fitness(self) -> float:
        all_fitness = [couple[1] for couple in self.data]
        if len(all_fitness) == 0:
            return 0
        return sum(all_fitness)/len(all_fitness)
    

    def __add__(self, other):
        
        new_pop = Population()
        new_pop.data = self.data

        for couple in other.data:
            new_pop.insert(couple[0], couple[1])
        return new_pop
    

    def __len__(self):
        return len(self.data)


    def __str__(self) -> str:
        return str(self.data)