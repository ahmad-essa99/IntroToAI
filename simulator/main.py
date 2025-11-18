from simulator import Simulator

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

if __name__ == "__main__":
    simulator = Simulator()
    read_and_parse_input_file(simulator, "example_input_file.txt")
    simulator.temp_init_agents() # i need to replace it with user prompt
    simulator.start_agents_loop()
