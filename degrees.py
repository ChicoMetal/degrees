import csv
import sys

import copy
from util import Node, StackFrontier, QueueFrontier

# Maps names to a set of corresponding person_ids
names = {}

# Maps person_ids to a dictionary of: name, birth, movies (a set of movie_ids)
people = {}

# Maps movie_ids to a dictionary of: title, year, stars (a set of person_ids)
movies = {}

# Path checked
known_path = []

def load_data(directory):
    """
    Load data from CSV files into memory.
    """

    # Load people
    with open(f"{directory}/people.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            people[row["id"]] = {
                "name": row["name"],
                "birth": row["birth"],
                "id": row["id"],
                "movies": set()
            }
            if row["name"].lower() not in names:
                names[row["name"].lower()] = {row["id"]}
            else:
                names[row["name"].lower()].add(row["id"])

    # Load movies
    with open(f"{directory}/movies.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            movies[row["id"]] = {
                "title": row["title"],
                "year": row["year"],
                "stars": set()
            }

    # Load stars
    with open(f"{directory}/stars.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                people[row["person_id"]]["movies"].add(row["movie_id"])
                movies[row["movie_id"]]["stars"].add(row["person_id"])
            except KeyError:
                pass


def main():
    if len(sys.argv) > 2:
        sys.exit("Usage: python degrees.py [directory]")
    directory = sys.argv[1] if len(sys.argv) == 2 else "large"

    # Load data from files into memory
    print("Loading data...")
    load_data(directory)
    print("Data loaded.")

    source = person_id_for_name(input("Name: "))
    if source is None:
        sys.exit("Person not found.")
    target = person_id_for_name(input("Name: "))
    if target is None:
        sys.exit("Person not found.")

    path = shortest_path(source, target)

    print("Path: ", path)


def check_target(source):
    stack_frontier = StackFrontier()
    for neighbor in neighbors_for_person(source):
        stack_frontier.add(neighbor)


def shortest_path(source, target):
    """
    Returns the shortest list of (movie_id, person_id) pairs
    that connect the source to the target.

    If no possible path, returns None.
    """
    node = bfs(source, target)

    if node is None:
        return None

    path = []
    while(True):
        if node is None or node.get_parent() is None:
            break

        path.insert(0, (get_action(node), get_person_name(node)))
        node = copy.deepcopy(node.get_parent())

    return path


def bfs(source, target):
    """Search source movies and look for target adding the people related with the source in the frontier"""
    source_info  = people[source]

    lvl = 0
    # stack = StackFrontier()
    stack = QueueFrontier()
    source_info["lvl"] = lvl
    source_info["id"] = source

    source_node = Node(source_info, None, None)
    stack.add(source_node)

    while(True):

        if stack.empty():
            return None

        node_from_stack = stack.remove()

        person_id = get_person_id(node_from_stack)

        if person_id == target:
            return node_from_stack

        neighbors = neighbors_for_person(person_id)

        node_parent = copy.deepcopy(node_from_stack)
        for movie, person in neighbors:
            if person == person_id:
                continue

            new_state = copy.deepcopy(people[person])
            new_state["lvl"] = lvl # assign values to the state this way cause some referential issues
            new_node = Node(new_state, node_parent, movie)

            if person == target:
                return new_node

            if not verify_known_path(node_from_stack, new_node):
                add_known_path(node_from_stack, new_node)
                stack.add(new_node)

        lvl += 1


def person_id_for_name(name):
    """
    Returns the IMDB id for a person's name,
    resolving ambiguities as needed.
    """
    person_ids = list(names.get(name.lower(), set()))
    if len(person_ids) == 0:
        return None
    elif len(person_ids) > 1:
        print(f"Which '{name}'?")
        for person_id in person_ids:
            person = people[person_id]
            name = person["name"]
            birth = person["birth"]
            print(f"ID: {person_id}, Name: {name}, Birth: {birth}")
        try:
            person_id = input("Intended Person ID: ")
            if person_id in person_ids:
                return person_id
        except ValueError:
            pass
        return None
    else:
        return person_ids[0]


def neighbors_for_person(person_id):
    """
    Returns (movie_id, person_id) pairs for people
    who starred with a given person.
    """
    movie_ids = people[person_id]["movies"]
    neighbors = set()
    for movie_id in movie_ids:
        for person_id in movies[movie_id]["stars"]:
            neighbors.add((movie_id, person_id))
    return neighbors


def verify_known_path(node_origin, node_destiny):
    """Verify if the path is known"""
    path = get_person_id(node_origin) + ":" + get_person_id(node_destiny)
    inverse_path = get_person_id(node_destiny) + ":" + get_person_id(node_origin)
    return path in known_path or inverse_path in known_path


def add_known_path(node_origin, node_destiny):
    """Add a path to the known paths"""
    path = get_person_id(node_origin) + ":" + get_person_id(node_destiny)
    inverse_path = get_person_id(node_destiny) + ":" + get_person_id(node_origin)
    known_path.append(path)
    known_path.append(inverse_path)

def get_person_id(node):
    """Return a person ID"""
    return node.get_state()["id"]

def get_person_name(node):
    """Get person name"""
    return node.get_state()["name"]

def get_action(node):
    """Return the action"""
    return node.get_action()


if __name__ == "__main__":
    main()
