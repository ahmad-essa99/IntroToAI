from simulator import Simulator
from enums import AgentType


# NOTE: i should add termination of simulation if current people cant be reached by any agent
# user should choose number of agent and their type and their initial poisiton

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


def test_f(test_num, agent_types_and_loc):
    simulator = Simulator()
    read_and_parse_input_file(simulator, f"tests/test_{test_num}.txt")
    simulator.test_init(agent_types_and_loc)
    simulator.start_agents_loop()
    return simulator

if __name__ == "__main__":

    simulator = test_f(test_num=15, agent_types_and_loc = [(AgentType.GREEDY,1), (AgentType.A_STAR,1), (AgentType.REAL_TIME_A_STAR,1)])




