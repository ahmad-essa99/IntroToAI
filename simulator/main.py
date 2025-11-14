from simulator import Simulator


if __name__ == "__main__":
    simulator = Simulator()
    simulator.read_and_parse_input_file("example_input_file.txt")
    simulator.temp_init_agents() # replace with user prompt
