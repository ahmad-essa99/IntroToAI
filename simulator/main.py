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

def parse_bool(s: str) -> bool:
    s = s.strip().lower()
    if s in ("true", "t"):
        return True
    if s in ("false", "f"):
        return False
    raise ValueError("Boolean value must be true/false or t/f")


def print_evidence(evidence: dict):
    if not evidence:
        print("Current evidence: (empty)\n")
        return
    print("Current evidence:")
    if "W" in evidence:
        print(f"  W = {evidence['W']}")
    for k in sorted([k for k in evidence if k.startswith("F_")], key=lambda x: int(x.split("_")[1])):
        print(f"  {k} = {evidence[k]}")
    for k in sorted([k for k in evidence if k.startswith("Ev_")], key=lambda x: int(x.split("_")[1])):
        print(f"  {k} = {evidence[k]}")
    print()


def interactive_part2(simulator, input_file: str):
    # build everything
    read_and_parse_input_file(simulator, input_file)
    simulator.build_bayes_net()
    bn = simulator._bayes_network

    print("\n=== Part II Interactive Inference ===")
    print("Commands:")
    print("  reset                         -> clear evidence")
    print("  add W <mild|stormy|extreme>    -> add weather evidence")
    print("  add F <edge_id> <true|false>   -> add flooding evidence for edge")
    print("  add Ev <vertex_id> <true|false>-> add evacuees evidence for vertex")
    print("  show                          -> show current evidence")
    print("  reason                        -> print posteriors for W, all F, all Ev")
    print("  path <e1> <e2> ...             -> P(path free | evidence) for listed edge ids")
    print("  quit")
    print()

    evidence = {}

    while True:
        try:
            cmdline = input(">> ").strip()
        except EOFError:
            print("\nEOF - quitting.")
            break

        if not cmdline:
            continue

        parts = cmdline.split()
        cmd = parts[0].lower()

        if cmd == "quit":
            print("Bye.")
            break

        elif cmd == "reset":
            evidence.clear()
            print("Evidence cleared.\n")

        elif cmd == "show":
            print_evidence(evidence)

        elif cmd == "add":
            # add W mild
            # add F 2 true
            # add Ev 3 false
            if len(parts) < 3:
                print("Usage:\n  add W <mild|stormy|extreme>\n  add F <edge_id> <true|false>\n  add Ev <vertex_id> <true|false>\n")
                continue

            kind = parts[1].lower()

            try:
                if kind == "w":
                    if len(parts) != 3:
                        print("Usage: add W <mild|stormy|extreme>\n")
                        continue
                    w = parts[2].lower()
                    if w not in ("mild", "stormy", "extreme"):
                        print("Weather must be: mild | stormy | extreme\n")
                        continue
                    evidence["W"] = w
                    print(f"Added evidence: W={w}\n")

                elif kind == "f":
                    if len(parts) != 4:
                        print("Usage: add F <edge_id> <true|false>\n")
                        continue
                    eid = int(parts[2])
                    val = parse_bool(parts[3])
                    evidence[f"F_{eid}"] = val
                    print(f"Added evidence: F_{eid}={val}\n")

                elif kind == "ev":
                    if len(parts) != 4:
                        print("Usage: add Ev <vertex_id> <true|false>\n")
                        continue
                    vid = int(parts[2])
                    val = parse_bool(parts[3])
                    evidence[f"Ev_{vid}"] = val
                    print(f"Added evidence: Ev_{vid}={val}\n")

                else:
                    print("Unknown add type. Use: W / F / Ev\n")

            except ValueError as ve:
                print(f"Error: {ve}\n")

        elif cmd == "reason":
            # prints 1,2,3
            print_evidence(evidence)
            try:
                bn.report_posteriors(evidence)
            except ValueError as ve:
                print(f"Reasoning error: {ve}\n")

        elif cmd == "path":
            # path 1 4  (edge ids)
            if len(parts) < 2:
                print("Usage: path <edge_id> <edge_id> ...\n")
                continue
            try:
                edge_ids = [int(x) for x in parts[1:]]
                p = bn.probability_path_free(edge_ids, evidence)
                print_evidence(evidence)
                print(f"P(path free for edges {edge_ids} | evidence) = {p:g}\n")
            except ValueError as ve:
                print(f"Path error: {ve}\n")

        else:
            print("Unknown command. Try: reset, add, show, reason, path, quit\n")


# Example entry point
if __name__ == "__main__":
    simulator = Simulator()
    interactive_part2(simulator, "example_input_file.txt")
