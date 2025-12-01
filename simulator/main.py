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


def choose_third_agent_type():
    print("Choose third agent type:")
    print("  1) Human")
    print("  2) Stupid Greedy")
    print("  3) Thief")
    print("  4) Greedy Agent")
    print("  5) A* Agent")
    print("  6) Real Time A* Agent")
    choice = input("Enter your choice: ").strip()
    if choice == "1":
        return AgentType.HUMAN
    elif choice == "2":
        return AgentType.STUPID_GREEDY
    elif choice == "3":
        return AgentType.THIEF
    elif choice == "4":
        return AgentType.GREEDY
    elif choice == "5":
        return AgentType.A_STAR
    elif choice == "6":
        return AgentType.REAL_TIME_A_STAR
    else:
        print("Invalid choice, choose again")
        return choose_third_agent_type()

def choose_starting_vertex(simulator):
    while True:
        try:
            print(f"choose agent starting agent, from 1 to {simulator._num_of_vertices}: ")
            v = int(input(f"your choice: "))
            if v in simulator._graph._vertices:
                return v
            print(f"Vertex {v} does not exist - Valid vertices: {sorted(simulator._graph._vertices.keys())}")
        except ValueError:
            print("Please enter a valid integer vertex id")

if __name__ == "__main__":
    simulator = Simulator()
    read_and_parse_input_file(simulator, "example_input_file.txt")
    choosed_third_type = choose_third_agent_type()
    starting_vertex_id = choose_starting_vertex(simulator)
    agent_types_and_loc = [(AgentType.STUPID_GREEDY, 1), (AgentType.THIEF, 1), (choosed_third_type, starting_vertex_id)]
    simulator.init_sim(agent_types_and_loc)
    simulator.start_agents_loop()

