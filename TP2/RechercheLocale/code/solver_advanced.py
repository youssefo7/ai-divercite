import copy
import random
import math
import time
from schedule import Schedule
from collections import defaultdict

# % OUARAD (2117136)
# % FARHAT (2153946)

def evaluate_solution(solution, num_courses):
    # Evaluate the quality of a solution by considering the number of timeslots used and the balance of courses across the timeslots.
    
    num_timeslots = len(set(solution.values()))
    timeslot_counts = defaultdict(int)
    for timeslot in solution.values():     
        timeslot_counts[timeslot] += 1

    normalized_timeslot_counts = [count / num_courses for count in timeslot_counts.values()]
    std_dev = math.sqrt(sum((x - sum(normalized_timeslot_counts) / num_timeslots)**2 for x in normalized_timeslot_counts) / num_timeslots)

    return num_timeslots+std_dev

def find_neighboring_solution(schedule, current_solution):
#find a neighbor solution by moving one class to a different time slot, making sure no new conlicts are introduced
    new_solution = copy.deepcopy(current_solution)
    courses = list(new_solution.keys())
    random.shuffle(courses)
    for course in courses:
        for new_timeslot in range(len(set(current_solution.values()))):
            if new_timeslot != new_solution[course]:
                new_solution[course] = new_timeslot
                if count_conflicts(schedule, new_solution) == 0:
                    new_cost = evaluate_solution(new_solution, len(schedule.course_list))
                    return new_solution, new_cost
                new_solution[course] = current_solution[course]
    return current_solution, evaluate_solution(current_solution, len(schedule.course_list))

def simulated_annealing(schedule, initial_solution, max_iterations=1000, initial_temperature=100.0, cooling_rate=0.99):
    """Implement a simulated annealing algorithm to optimize the number of timeslots used."""
    current_solution = initial_solution
    best_solution = current_solution.copy()
    temperature = initial_temperature

    for _ in range(max_iterations):
        new_solution, new_cost = find_neighboring_solution(schedule, current_solution)
        if new_cost < evaluate_solution(current_solution, len(schedule.course_list)):
            current_solution = new_solution
            if new_cost < evaluate_solution(best_solution, len(schedule.course_list)):
                best_solution = new_solution
        else:
            acceptance_probability = min(1, pow(math.e, -(new_cost - evaluate_solution(current_solution, len(schedule.course_list))) / temperature))
            if random.random() < acceptance_probability:
                current_solution = new_solution
        temperature *= cooling_rate
    
    return best_solution

def solve(schedule):

    start_time = time.time()
    best_solution = None
    best_cost = float('inf')

    while time.time() - start_time < 280:  # DO random restart until almost 5 min time limit is up
        # Generate an initial solution
        current_solution = initialize_solution(schedule)
        
        # Run simulated annealing on the initial solution
        final_solution = simulated_annealing(schedule, current_solution, max_iterations=500)
        final_cost = evaluate_solution(final_solution, len(schedule.course_list))
        
        #check if this solution is the best we've found so far
        if final_cost < best_cost:
            best_solution = final_solution
            best_cost = final_cost


    return best_solution

def initialize_solution(schedule):
    #assign the courses one by one to a timeslot making sure no conflicts are generated
    solution = {}
    courses = list(schedule.course_list) 
    random.shuffle(courses)  # Shuffle courses to start with a different order each time

    for course in courses:
        assigned = False
        time_slot = 1
        
        while not assigned:
            conflicts = schedule.get_node_conflicts(course)
            # Check if the current timeslot has no conflicts with already assigned courses
            if all(solution.get(conflicting_course) != time_slot for conflicting_course in conflicts):
                solution[course] = time_slot  # Assign the course to this timeslot
                assigned = True
            else:
                time_slot += 1  # Try the next timeslot if there's a conflict
    
    return solution


def count_conflicts(schedule, solution):
    conflict_count = 0
    for course_a, course_b in schedule.conflict_list:
        #if both courses are assigned to the same timeslot
        if solution[course_a] == solution[course_b]:
            conflict_count += 1
    return conflict_count
