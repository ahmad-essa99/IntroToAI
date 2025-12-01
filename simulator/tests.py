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

tests_dir = "tests"
tests_file_name_format = "test_{}.txt"
tests_full_path_format = f"{tests_dir}/{tests_file_name_format}"

def test_f(test_num, agent_types_and_loc, expected_scores=None, debug = False):
    simulator = Simulator(debug=debug)
    read_and_parse_input_file(simulator, tests_full_path_format.format(test_num))
    simulator.test_init(agent_types_and_loc)
    simulator.start_agents_loop()

    if not expected_scores:
        return

    for num, agent in enumerate(simulator._agents):
        if agent._score == expected_scores[num]:
            print(f"{tests_dir} folder - test {test_num} for {agent._agent_type} PASSED")
        else:
            print(f"{tests_dir} folder - test {test_num} for {agent._agent_type} FAILED")


if __name__ == "__main__":
    tests_dir = "tests1"
    tests_file_name_format = "instance_{}.txt"
    tests_full_path_format = f"{tests_dir}/{tests_file_name_format}"
    test_num = 1
    simulator = test_f(test_num=test_num, agent_types_and_loc=[(AgentType.GREEDY, 1)], expected_scores=[3989])
    simulator = test_f(test_num=test_num, agent_types_and_loc=[(AgentType.A_STAR, 1)], expected_scores=[3992])
    simulator = test_f(test_num=test_num, agent_types_and_loc=[(AgentType.REAL_TIME_A_STAR, 1)], expected_scores=[3992])
    print("----------------------------------------------------------------")
    test_num = 2
    simulator = test_f(test_num=test_num, agent_types_and_loc=[(AgentType.GREEDY, 1)], expected_scores=[7982])
    simulator = test_f(test_num=test_num, agent_types_and_loc=[(AgentType.A_STAR, 1)], expected_scores=[7983])
    simulator = test_f(test_num=test_num, agent_types_and_loc=[(AgentType.REAL_TIME_A_STAR, 1)], expected_scores=[7983])
    print("----------------------------------------------------------------")

    test_num = 3
    simulator = test_f(test_num=test_num, agent_types_and_loc=[(AgentType.A_STAR, 1)], expected_scores=[5964])
    simulator = test_f(test_num=test_num, agent_types_and_loc=[(AgentType.REAL_TIME_A_STAR, 1)], expected_scores=[5959])
    print("----------------------------------------------------------------")

    test_num = 4
    simulator = test_f(test_num=test_num, agent_types_and_loc=[(AgentType.GREEDY, 1)], expected_scores=[10975])
    simulator = test_f(test_num=test_num, agent_types_and_loc=[(AgentType.A_STAR, 1)], expected_scores=[10981])
    simulator = test_f(test_num=test_num, agent_types_and_loc=[(AgentType.REAL_TIME_A_STAR, 1)], expected_scores=[10981])
    print("----------------------------------------------------------------")

    test_num = 5
    simulator = test_f(test_num=test_num, agent_types_and_loc=[(AgentType.A_STAR, 1)], expected_scores=[3978])
    simulator = test_f(test_num=test_num, agent_types_and_loc=[(AgentType.REAL_TIME_A_STAR, 1)],
                       expected_scores=[3975])
    print("----------------------------------------------------------------")





