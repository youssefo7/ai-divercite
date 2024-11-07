import matplotlib.pyplot as plt
import networkx as nx
import random as r
import time


def solve(schedule):
    """
    Your solution of the problem
    :param schedule: object describing the input
    :return: a list of tuples of the form (c,t) where c is a course and t a time slot. 
    """
    start_time = time.time()  # Start the timer
    
    # Call the solver function (you can choose either simulated_annealing or tabu_search here)
    result = sequential_greedy_solution(schedule)


    end_time = time.time()  # End the timer
    duration = end_time - start_time  # Calculate duration

    print(f"Solution computed in {duration:.2f} seconds")  # Print the time taken
    return result


def count_conflicts(schedule, solution):
    """Helper function to count the number of conflicts in a solution."""
    return sum(1 for a, b in schedule.conflict_list if solution[a] == solution[b])

def print_schedule(solution):
    """
    Prints the courses scheduled in each time slot.
    :param schedule: The schedule object (not directly used for this function, but could be extended for more details)
    :param solution: A dictionary where the keys are course names and the values are time slots.
    """
    # Create a dictionary to hold the courses for each time slot
    time_slot_courses = {}

    # Iterate over the solution to group courses by their time slot
    for course, time_slot in solution.items():
        if time_slot not in time_slot_courses:
            time_slot_courses[time_slot] = []
        time_slot_courses[time_slot].append(course)

    # Sort time slots and print each one with its corresponding courses
    for time_slot in sorted(time_slot_courses.keys()):
        print(f"Time Slot {time_slot}: ", ", ".join(time_slot_courses[time_slot]))

def sequential_greedy_solution(schedule):
    """
    Generates a solution by sequentially assigning each course to the first available time slot
    that does not create any conflicts.
    """
    solution = {}  # Dictionary to hold the course to timeslot mapping
    
    for course in schedule.course_list:
        assigned = False
        time_slot = 1
        
        # Try assigning the course to the lowest possible time slot without conflicts
        while not assigned:
            # Check if the current timeslot has conflicts with already assigned courses
            conflicts = schedule.get_node_conflicts(course)
            if all(solution.get(conflicting_course) != time_slot for conflicting_course in conflicts):
                # No conflicts, assign the course to this time slot
                solution[course] = time_slot
                assigned = True
            else:
                # Conflict found, try the next timeslot
                time_slot += 1
    print_schedule(solution)
    return solution
