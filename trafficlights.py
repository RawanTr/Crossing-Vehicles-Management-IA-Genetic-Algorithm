from intersections.intersection import Intersection
import libsumo as traci
import random

class TFIntersection(Intersection):

    def __init__(self, id: str, center: list[float], visibility: float, mutation_proba : float, mutation_max : int, logic_id : str, phases : list[str], min_phase_time : float, cycle_time : float) -> None:
        super().__init__(id, center, visibility, mutation_proba, mutation_max)

        self.logic_id = logic_id
        self.phases = phases
        self.min_phase_time = min_phase_time
        self.cycle_time = cycle_time

    
    def get_default_chromosom(self) -> list[float]:

        phases = traci.trafficlight.getCompleteRedYellowGreenDefinition(self.id)[0].phases
        return [phase.duration for phase in phases]


    def apply_chromosom(self, chromosom : list[float]):
        
        phases = [traci.TraCIPhase(chromosom[i], self.phases[i], chromosom[i], chromosom[i]) for i in range(len(self.phases))]
        logic = traci.TraCILogic(self.logic_id, 0, 0, phases)
        traci.trafficlight.setProgramLogic(self.id, logic)


    def sanitize_chromosom(self, chromosom : list[float]) -> list[float]:

        indexes = [i for i in range(len(chromosom))]
        while sum(chromosom) != self.cycle_time:
            index = random.choices(indexes, k=1)[0]
            if sum(chromosom) > self.cycle_time:
                if chromosom[index] > self.min_phase_time:
                    chromosom[index] -= 1
            else:
                chromosom[index] += 1

        return chromosom
        
    
    def get_initial_chromosoms(self, n : int) -> list[list[float]]:
        
        initials = []
        max_phase_time = self.cycle_time - len(self.phases)*self.min_phase_time
        for i in range(n):
            chromosom = [random.randint(self.min_phase_time, max_phase_time) for j in range(len(self.phases))]
            chromosom = self.sanitize_chromosom(chromosom)
            initials.append(chromosom)
        
        return initials
    
    

    def mutation(self, chromosom: list[float]) -> list[float]:
        
        rand_number = random.random()
        if rand_number > self.mutation_max:
            return chromosom
        
        rand_index = random.randint(0, len(chromosom)-1)
        rand_modif = random.randint(1,self.mutation_max)
        rand_number = random.random()
        if rand_number >= 0.5:
            if chromosom[rand_index] - rand_modif >= self.min_phase_time:
                chromosom[rand_index] -= rand_modif
        else:
            chromosom[rand_index] += rand_modif

        return self.sanitize_chromosom(chromosom)
    

    def get_meaning(self) -> str:
        return "phases : " + str(self.phases)