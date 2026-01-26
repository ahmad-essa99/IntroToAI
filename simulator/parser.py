import re
from edge import Edge
from graph import Graph, ParsedProblem


def _strip_comments(line: str) -> str:
    line = line.strip()
    if not line:
        return ""
    if ";" in line:
        line = line.split(";", 1)[0].strip()
    return line


def parse_input(file_path: str) -> ParsedProblem:
    """Parse the input format.

    Supported directives (as in the assignment handout):
        - #V n
        - #E<id> v1 v2 W<weight> [F <prob>]
        - #K<id> v
        - #EC t
        - #UC t
        - #FF factor
        - #Start v
        - #Target v

    Notes:
        - If an edge line omits 'F <prob>', it is treated as never-flooded.
        - Kit directives are treated as 'kit exists at vertex'; multiplicity is ignored.
    """

    n_vertices: int | None = None
    edges: list[Edge] = []
    kits: set[int] = set()
    equip_cost: float | None = None
    unequip_cost: float | None = None
    slow_factor: float | None = None
    start: int | None = None
    target: int | None = None

    with open(file_path, "r", encoding="utf-8") as f:
        for raw in f:
            line = _strip_comments(raw)
            if not line:
                continue

            parts = line.split()
            head = parts[0]

            if head == "#V":
                if len(parts) != 2:
                    raise ValueError(f"Invalid #V line: {line}")
                n_vertices = int(parts[1])
                continue

            if re.fullmatch(r"#E\d+", head):
                # Example: #E3 3 4 W3 F 0.3
                if len(parts) < 4:
                    raise ValueError(f"Invalid edge line: {line}")
                eid = int(head[2:])
                v1 = int(parts[1])
                v2 = int(parts[2])
                if not parts[3].startswith("W"):
                    raise ValueError(f"Edge weight token must be W<val>: {line}")
                w = float(parts[3][1:])

                flood_prob = None
                if len(parts) >= 6:
                    # allow: ... F 0.2
                    if parts[4] != "F":
                        raise ValueError(f"Expected 'F <prob>' in edge line: {line}")
                    flood_prob = float(parts[5])

                edges.append(Edge(eid, v1, v2, w, flood_prob))
                continue

            if head.startswith("#K"):
                if len(parts) != 2:
                    raise ValueError(f"Invalid kit line: {line}")
                kits.add(int(parts[1]))
                continue

            if head == "#EC":
                equip_cost = float(parts[1])
                continue

            if head == "#UC":
                unequip_cost = float(parts[1])
                continue

            if head == "#FF":
                slow_factor = float(parts[1])
                continue

            if head == "#Start":
                start = int(parts[1])
                continue

            if head == "#Target":
                target = int(parts[1])
                continue

            raise ValueError(f"Unknown directive: {line}")

    if n_vertices is None:
        raise ValueError("Missing #V line")
    if equip_cost is None or unequip_cost is None or slow_factor is None:
        raise ValueError("Missing one or more constants: #EC #UC #FF")

    # Start/target can be provided by user in runtime; keep None here, fill in runner.
    start = start or None
    target = target or None

    g = Graph(n_vertices)
    for e in edges:
        g.add_edge(e)

    # Basic validation
    for v in kits:
        if v < 1 or v > n_vertices:
            raise ValueError(f"kit vertex out of range: {v}")

    return ParsedProblem(
        n_vertices=n_vertices,
        edges=edges,
        kits=kits,
        equip_cost=equip_cost,
        unequip_cost=unequip_cost,
        slow_factor=slow_factor,
        start=start,
        target=target,
    )
