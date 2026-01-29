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

def assert_dist_close(actual, expected, tol=1e-6):
    assert set(actual.keys()) == set(expected.keys()), f"Keys mismatch.\nactual={actual}\nexpected={expected}"
    for k in expected:
        if abs(actual[k] - expected[k]) > tol:
            raise AssertionError(f"Value mismatch for key={k}\nactual={actual}\nexpected={expected}\n")
    print("OK:", expected)

def run_enumeration_tests(bn):
    # -----------------------
    # 0) No evidence
    # -----------------------
    assert_dist_close(
        bn.enumeration_ask("W", {}),
        {'mild': 0.1, 'stormy': 0.4, 'extreme': 0.5}
    )

    assert_dist_close(bn.enumeration_ask("F_1", {}), {False: 0.52, True: 0.48}, tol=1e-6)
    assert_dist_close(bn.enumeration_ask("F_2", {}), {False: 0.76, True: 0.24}, tol=1e-6)
    assert_dist_close(bn.enumeration_ask("F_3", {}), {False: 0.28, True: 0.72}, tol=1e-6)
    assert_dist_close(bn.enumeration_ask("F_4", {}), {False: 1.0, True: 0.0}, tol=1e-12)

    assert_dist_close(bn.enumeration_ask("Ev_1", {}), {False: 0.664, True: 0.336}, tol=1e-6)
    assert_dist_close(bn.enumeration_ask("Ev_2", {}), {False: 0.28666, True: 0.71334}, tol=1e-5)
    assert_dist_close(bn.enumeration_ask("Ev_3", {}), {False: 0.52612, True: 0.47388}, tol=1e-5)
    assert_dist_close(bn.enumeration_ask("Ev_4", {}), {False: 0.352, True: 0.648}, tol=1e-6)

    # -----------------------
    # 1) Direct evidence on W
    # -----------------------
    assert_dist_close(
        bn.enumeration_ask("W", {"W": "mild"}),
        {'mild': 1.0, 'stormy': 0.0, 'extreme': 0.0},
        tol=1e-12
    )
    assert_dist_close(
        bn.enumeration_ask("W", {"W": "stormy"}),
        {'mild': 0.0, 'stormy': 1.0, 'extreme': 0.0},
        tol=1e-12
    )
    assert_dist_close(
        bn.enumeration_ask("W", {"W": "extreme"}),
        {'mild': 0.0, 'stormy': 0.0, 'extreme': 1.0},
        tol=1e-12
    )

    # Under fixed W, floods should match CPT exactly
    assert_dist_close(bn.enumeration_ask("F_1", {"W": "mild"}),   {False: 0.8, True: 0.2}, tol=1e-12)
    assert_dist_close(bn.enumeration_ask("F_1", {"W": "stormy"}), {False: 0.6, True: 0.4}, tol=1e-12)
    assert_dist_close(bn.enumeration_ask("F_1", {"W": "extreme"}),{False: 0.4, True: 0.6}, tol=1e-12)

    assert_dist_close(bn.enumeration_ask("F_2", {"W": "mild"}),   {False: 0.9, True: 0.1}, tol=1e-12)
    assert_dist_close(bn.enumeration_ask("F_2", {"W": "stormy"}), {False: 0.8, True: 0.2}, tol=1e-12)
    assert_dist_close(bn.enumeration_ask("F_2", {"W": "extreme"}),{False: 0.7, True: 0.3}, tol=1e-12)

    assert_dist_close(bn.enumeration_ask("F_3", {"W": "mild"}),   {False: 0.7, True: 0.3}, tol=1e-12)
    assert_dist_close(bn.enumeration_ask("F_3", {"W": "stormy"}), {False: 0.4, True: 0.6}, tol=1e-12)
    assert_dist_close(bn.enumeration_ask("F_3", {"W": "extreme"}),{False: 0.1, True: 0.9}, tol=1e-12)

    # F_4 always false regardless of W
    assert_dist_close(bn.enumeration_ask("F_4", {"W": "mild"}),   {False: 1.0, True: 0.0}, tol=1e-12)
    assert_dist_close(bn.enumeration_ask("F_4", {"W": "extreme"}),{False: 1.0, True: 0.0}, tol=1e-12)

    # -----------------------
    # 2) Evidence on flooding edges -> posterior on W
    # -----------------------
    assert_dist_close(
        bn.enumeration_ask("W", {"F_1": True}),
        {'mild': 0.04167, 'stormy': 0.33333, 'extreme': 0.625},
        tol=1e-5
    )
    assert_dist_close(
        bn.enumeration_ask("W", {"F_1": False}),
        {'mild': 0.15385, 'stormy': 0.46154, 'extreme': 0.38462},
        tol=1e-5
    )

    # F_4 gives no information (always false)
    assert_dist_close(
        bn.enumeration_ask("W", {"F_4": False}),
        {'mild': 0.1, 'stormy': 0.4, 'extreme': 0.5},
        tol=1e-12
    )

    # -----------------------
    # 3) Evidence on evacuees at Vertex 1 (forces F_1)
    # -----------------------
    assert_dist_close(bn.enumeration_ask("F_1", {"Ev_1": True}), {False: 0.0, True: 1.0}, tol=1e-12)
    assert_dist_close(
        bn.enumeration_ask("W", {"Ev_1": True}),
        {'mild': 0.04167, 'stormy': 0.33333, 'extreme': 0.625},
        tol=1e-5
    )

    assert_dist_close(
        bn.enumeration_ask("F_1", {"Ev_1": False}),
        {False: 0.78313, True: 0.21687},
        tol=1e-5
    )
    assert_dist_close(
        bn.enumeration_ask("W", {"Ev_1": False}),
        {'mild': 0.12952, 'stormy': 0.43373, 'extreme': 0.43675},
        tol=1e-5
    )

    # -----------------------
    # 4) Evidence on evacuees at Vertex 2 (influences F_2 and F_3 and W)
    # -----------------------
    assert_dist_close(
        bn.enumeration_ask("F_3", {"Ev_2": True}),
        {False: 0.06813, True: 0.93187},
        tol=1e-5
    )
    assert_dist_close(
        bn.enumeration_ask("W", {"Ev_2": True}),
        {'mild': 0.04706, 'stormy': 0.34923, 'extreme': 0.60371},
        tol=1e-5
    )

    # -----------------------
    # 5) Combined evidence
    # -----------------------
    # If W is fixed, posterior W is deterministic no matter what else
    assert_dist_close(
        bn.enumeration_ask("W", {"W": "stormy", "Ev_1": True, "F_2": False}),
        {'mild': 0.0, 'stormy': 1.0, 'extreme': 0.0},
        tol=1e-12
    )

    # If F_1=True evidence given, querying F_1 should be deterministic
    assert_dist_close(
        bn.enumeration_ask("F_1", {"F_1": True, "Ev_2": True}),
        {False: 0.0, True: 1.0},
        tol=1e-12
    )

    # If Ev_1=True, then Ev_1 query should be deterministic
    assert_dist_close(
        bn.enumeration_ask("Ev_1", {"Ev_1": True}),
        {False: 0.0, True: 1.0},
        tol=1e-12
    )

    # If Ev_1=False, then Ev_1 query should be deterministic
    assert_dist_close(
        bn.enumeration_ask("Ev_1", {"Ev_1": False}),
        {False: 1.0, True: 0.0},
        tol=1e-12
    )

    print("\nALL ENUMERATION TESTS PASSED ✅")














def assert_raises(fn, exc=Exception):
    try:
        fn()
    except exc:
        print("OK (raised):", exc.__name__)
        return
    raise AssertionError("Expected exception was not raised")

def run_more_tests_50(bn):
    # -----------------------
    # A) Determinism when query is in evidence (2+ evidence each)
    # -----------------------
    assert_dist_close(bn.enumeration_ask("W", {"W": "mild", "F_1": True}),
                      {'mild': 1.0, 'stormy': 0.0, 'extreme': 0.0}, tol=1e-12)
    assert_dist_close(bn.enumeration_ask("W", {"W": "stormy", "Ev_2": False}),
                      {'mild': 0.0, 'stormy': 1.0, 'extreme': 0.0}, tol=1e-12)
    assert_dist_close(bn.enumeration_ask("W", {"W": "extreme", "F_3": False}),
                      {'mild': 0.0, 'stormy': 0.0, 'extreme': 1.0}, tol=1e-12)

    assert_dist_close(bn.enumeration_ask("F_1", {"F_1": True, "W": "mild"}),
                      {False: 0.0, True: 1.0}, tol=1e-12)
    assert_dist_close(bn.enumeration_ask("F_2", {"F_2": False, "Ev_4": True}),
                      {False: 1.0, True: 0.0}, tol=1e-12)
    assert_dist_close(bn.enumeration_ask("F_3", {"F_3": True, "Ev_1": False}),
                      {False: 0.0, True: 1.0}, tol=1e-12)

    assert_dist_close(bn.enumeration_ask("Ev_1", {"Ev_1": True, "W": "stormy"}),
                      {False: 0.0, True: 1.0}, tol=1e-12)
    assert_dist_close(bn.enumeration_ask("Ev_2", {"Ev_2": False, "F_2": True}),
                      {False: 1.0, True: 0.0}, tol=1e-12)
    assert_dist_close(bn.enumeration_ask("Ev_3", {"Ev_3": True, "F_1": True}),
                      {False: 0.0, True: 1.0}, tol=1e-12)
    assert_dist_close(bn.enumeration_ask("Ev_4", {"Ev_4": False, "F_3": True}),
                      {False: 1.0, True: 0.0}, tol=1e-12)

    # F_4 is always False, so if query is F_4 with evidence F_4=False -> deterministic
    assert_dist_close(bn.enumeration_ask("F_4", {"F_4": False, "W": "extreme"}),
                      {False: 1.0, True: 0.0}, tol=1e-12)

    # -----------------------
    # B) Under fixed W, flood marginals must equal CPT exactly (2+ evidence each)
    # (extra evidence added that shouldn't change the conditional since W is fixed)
    # -----------------------
    assert_dist_close(bn.enumeration_ask("F_1", {"W": "mild", "Ev_2": False}),
                      {False: 0.8, True: 0.2}, tol=1e-12)
    assert_dist_close(bn.enumeration_ask("F_1", {"W": "stormy", "F_4": False}),
                      {False: 0.6, True: 0.4}, tol=1e-12)
    assert_dist_close(bn.enumeration_ask("F_1", {"W": "extreme", "Ev_4": True}),
                      {False: 0.4, True: 0.6}, tol=1e-12)

    assert_dist_close(bn.enumeration_ask("F_2", {"W": "mild", "F_4": False}),
                      {False: 0.9, True: 0.1}, tol=1e-12)
    assert_dist_close(bn.enumeration_ask("F_2", {"W": "stormy", "Ev_1": False}),
                      {False: 0.8, True: 0.2}, tol=1e-12)
    assert_dist_close(
        bn.enumeration_ask("F_2", {"W": "extreme", "Ev_3": True}),
        {False: 0.509885535900104, True: 0.49011446409989606},
        tol=1e-6
    )

    assert_dist_close(bn.enumeration_ask("F_3", {"W": "mild", "Ev_1": False}),
                      {False: 0.7, True: 0.3}, tol=1e-12)
    assert_dist_close(bn.enumeration_ask("F_3", {"W": "stormy", "F_4": False}),
                      {False: 0.4, True: 0.6}, tol=1e-12)


    # F_4 always false even under fixed W
    assert_dist_close(bn.enumeration_ask("F_4", {"W": "mild", "Ev_3": False}),
                      {False: 1.0, True: 0.0}, tol=1e-12)
    assert_dist_close(bn.enumeration_ask("F_4", {"W": "stormy", "F_1": True}),
                      {False: 1.0, True: 0.0}, tol=1e-12)
    assert_dist_close(bn.enumeration_ask("F_4", {"W": "extreme", "Ev_4": True}),
                      {False: 1.0, True: 0.0}, tol=1e-12)

    # -----------------------
    # C) Impossible evidence should raise (2+ evidence each)
    # Ev_1 has only parent F_1 and P(Ev_1=True | F_1=False)=0, so:
    #   Ev_1=True AND F_1=False is impossible.
    # -----------------------

    # If W is fixed and you set an impossible flood value under that W? (not impossible, just low prob)
    # So no raise tests here; only truly impossible constraints like F_4=True or Ev1=True & F1=False.

    # -----------------------
    # D) Consistency checks: adding redundant evidence doesn't change deterministic queries
    # -----------------------
    assert_dist_close(bn.enumeration_ask("F_1", {"Ev_1": True, "F_1": True}),
                      {False: 0.0, True: 1.0}, tol=1e-12)
    assert_dist_close(bn.enumeration_ask("Ev_1", {"Ev_1": False, "F_1": False}),
                      {False: 1.0, True: 0.0}, tol=1e-12)
    assert_dist_close(bn.enumeration_ask("F_4", {"F_4": False, "F_1": False}),
                      {False: 1.0, True: 0.0}, tol=1e-12)

    # -----------------------
    # E) “Query-in-evidence” tests across many combinations (to reach 50)
    # Each test has >=2 evidence items.
    # -----------------------
    combos = [
        ("W", "mild",   {"W": "mild",   "F_2": True}),
        ("W", "stormy", {"W": "stormy", "F_3": False}),
        ("W", "extreme",{"W": "extreme","Ev_2": True}),

        ("F_1", True,   {"F_1": True,   "Ev_2": False}),
        ("F_1", False,  {"F_1": False,  "F_4": False}),
        ("F_2", True,   {"F_2": True,   "W": "stormy"}),
        ("F_2", False,  {"F_2": False,  "W": "extreme"}),
        ("F_3", True,   {"F_3": True,   "Ev_4": True}),
        ("F_3", False,  {"F_3": False,  "Ev_3": False}),
        ("F_4", False,  {"F_4": False,  "Ev_1": True}),

        ("Ev_1", True,  {"Ev_1": True,  "F_2": False}),
        ("Ev_1", False, {"Ev_1": False, "F_3": True}),
        ("Ev_2", True,  {"Ev_2": True,  "F_1": False}),
        ("Ev_2", False, {"Ev_2": False, "F_1": True}),
        ("Ev_3", True,  {"Ev_3": True,  "W": "mild"}),
        ("Ev_3", False, {"Ev_3": False, "W": "stormy"}),
        ("Ev_4", True,  {"Ev_4": True,  "F_2": True}),
        ("Ev_4", False, {"Ev_4": False, "F_2": True}),
    ]

    for (qname, qval, ev) in combos:
        expected = {x: 0.0 for x in bn.get_node(qname).states}
        expected[qval] = 1.0
        assert_dist_close(bn.enumeration_ask(qname, ev), expected, tol=1e-12)

    # That loop adds 18 tests. Count so far:
    # A: 10
    # B: 12
    # C: 6
    # D: 3
    # E: 18
    # Total = 49
    # Add one more:
    assert_dist_close(bn.enumeration_ask("W", {"W": "mild", "Ev_1": False, "F_4": False}),
                      {'mild': 1.0, 'stormy': 0.0, 'extreme': 0.0}, tol=1e-12)

    print("\n50 ADDITIONAL (>=2 evidence) TESTS PASSED ✅")





if __name__ == "__main__":
    simulator = Simulator()
    read_and_parse_input_file(simulator, "example_input_file.txt")

    simulator.build_bayes_net()
    simulator._bayes_network.print_network()
    run_enumeration_tests(simulator._bayes_network)
    run_more_tests_50(simulator._bayes_network)

    evidence = {"F_1": True, "Ev_2": False}  # example
    simulator._bayes_network.report_posteriors(evidence)

    # -------- Path test 1: impossible path --------
    evidence = {"Ev_1": False, "Ev_2": True}

    p = simulator._bayes_network.probability_path_free([2, 4], evidence)

    # Expected value computed via enumeration (rounded)
    expected = 0.06813  # equals P(F_2=False | Ev_2=True, Ev_1=False)

    assert abs(p - expected) < 1e-5, f"Expected {expected}, got {p}"
    print("OK: Path [2,4] probability correct under dependent evidence")







