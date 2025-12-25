from simulator import Simulator
from enums import AgentType


def read_and_parse_input_file(simulator, input_file_path):

    with open(input_file_path, "r") as input_file:
        for line in input_file:
            line = line.strip()

            if not line:
                continue

            if ";" in line:
                line = line.split(";")[0].strip()

            # line is not empty and clean
            simulator._handle_input_file_line(line)

    if not simulator._num_of_vertices == len(simulator._graph._vertices):
        print("input file missmatch")
        exit(1)


def choose_game_type():
    print("Choose Game type:")
    print("  1) Adversarial Game")
    print("  2) Semi Cooperative Game")
    print("  3) Fully Cooperative Game")
    choice = input("Enter your choice: ").strip()
    if choice == "1":
        return AgentType.ADVERSARIAL
    elif choice == "2":
        return AgentType.SEMI_COOPERATIVE
    elif choice == "3":
        return AgentType.FULLY_COOPERATIVE
    else:
        print("Invalid choice, choose again")
        return choose_game_type()

def choose_first_starting_vertex(simulator):
    while True:
        try:
            print(f"choose FIRST agent starting vertex, from 1 to {simulator._num_of_vertices}: ")
            v = int(input(f"your choice: "))
            if v in simulator._graph._vertices:
                return v
            print(f"Vertex {v} does not exist - Valid vertices: {sorted(simulator._graph._vertices.keys())}")
        except ValueError:
            print("Please enter a valid integer vertex id")

def choose_second_starting_vertex(simulator):
    while True:
        try:
            print(f"choose SECOND agent starting vertex, from 1 to {simulator._num_of_vertices}: ")
            v = int(input(f"your choice: "))
            if v in simulator._graph._vertices:
                return v
            print(f"Vertex {v} does not exist - Valid vertices: {sorted(simulator._graph._vertices.keys())}")
        except ValueError:
            print("Please enter a valid integer vertex id")

if __name__ == "__main__":
    simulator = Simulator(debug=True)
    read_and_parse_input_file(simulator, "example_input_file1.txt")
    choosed_game_type = choose_game_type()
    first_agent_starting_vertex = choose_first_starting_vertex(simulator)
    second_agent_starting_vertex = choose_second_starting_vertex(simulator)

    simulator.init_sim(choosed_game_type, first_agent_starting_vertex, second_agent_starting_vertex)
    simulator.start_agents_loop()

