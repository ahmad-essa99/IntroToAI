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

tests_dir = "tests"
tests_file_name_format = "test_{}.txt"
tests_full_path_format = f"{tests_dir}/{tests_file_name_format}"

def test_f(test_num, agents_types, expected_scores=None, debug = False):
    simulator = Simulator(debug=debug)
    read_and_parse_input_file(simulator, tests_full_path_format.format(test_num))
    simulator.init_sim(agents_types=agents_types)
    simulator.start_agents_loop()

    if not expected_scores:
        return

    agent0_n_of_p_picked = simulator._first_agent._num_of_people_picked
    agent1_n_of_p_picked = simulator._second_agent._num_of_people_picked
    if agent0_n_of_p_picked == expected_scores[0] and agent1_n_of_p_picked == expected_scores[1]:
        print(f"{tests_dir} folder - test {test_num} for {agents_types} PASSED")
    else:
        print(f"{tests_dir} folder - test {test_num} for {agents_types} FAILED")
        print(f"expected {expected_scores}, actual result {(agent0_n_of_p_picked, agent1_n_of_p_picked)}")

if __name__ == "__main__":
    test_num = 1
    simulator = test_f(test_num=test_num, agents_types=AgentType.ADVERSARIAL, expected_scores=(1,0))
    simulator = test_f(test_num=test_num, agents_types=AgentType.SEMI_COOPERATIVE, expected_scores=(1, 1))
    simulator = test_f(test_num=test_num, agents_types=AgentType.FULLY_COOPERATIVE, expected_scores=(1, 1))
    print("----------------------------------------------------------------")

    test_num = 2
    simulator = test_f(test_num=test_num, agents_types=AgentType.ADVERSARIAL, expected_scores=(3,0))
    simulator = test_f(test_num=test_num, agents_types=AgentType.SEMI_COOPERATIVE, expected_scores=(3, 0))
    simulator = test_f(test_num=test_num, agents_types=AgentType.FULLY_COOPERATIVE, expected_scores=(1, 3))
    print("----------------------------------------------------------------")

    test_num = 3
    simulator = test_f(test_num=test_num, agents_types=AgentType.ADVERSARIAL, expected_scores=(8,0))
    simulator = test_f(test_num=test_num, agents_types=AgentType.SEMI_COOPERATIVE, expected_scores=(8, 0))
    simulator = test_f(test_num=test_num, agents_types=AgentType.FULLY_COOPERATIVE, expected_scores=(2, 6))
    print("----------------------------------------------------------------")

    test_num = 4
    simulator = test_f(test_num=test_num, agents_types=AgentType.ADVERSARIAL, expected_scores=(5,4))
    simulator = test_f(test_num=test_num, agents_types=AgentType.SEMI_COOPERATIVE, expected_scores=(5, 4))
    simulator = test_f(test_num=test_num, agents_types=AgentType.FULLY_COOPERATIVE, expected_scores=(4, 5))
    print("----------------------------------------------------------------")






