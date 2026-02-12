# Programming Assignment 4 — Hurricane Evacuation (Belief-State MDP)

Python: **3.11**

This project solves the "Hurricane Evacuation" decision problem by:

1. Parsing the input graph with independent edge flooding probabilities.
2. Building the **explicit belief-state MDP** (up to 20 vertices, up to 10 floodable edges).
3. Running **value iteration** to compute an optimal policy over belief-states.
4. Running simulations: sample a flooded/clear graph instance and follow the computed policy.

## Install

No external dependencies are required.

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .\.venv\Scripts\activate
```

## Run

```bash
python -m  main --input example_input_file.txt
```

Optional arguments:

```bash
python -m  main --input <file> --start 1 --target 5 --sims 5 --seed 123 --print-limit 500
```

If `#Start` / `#Target` are missing in the file and you do not pass `--start/--target`, the program will prompt for them.

## Input format

Supported directives:

```text
#V n
#E<i> v1 v2 W<weight> [F <prob>]
#K<i> v
#EC <equip_time>
#UC <unequip_time>
#FF <slow_factor>
#Start <s>
#Target <t>
```

Notes:
- If `F <prob>` is missing on an edge, it is treated as never flooded.
- Flooding events are independent.
- The agent observes the true status of **all floodable edges incident to the vertex it is currently at** (arrival observation).

## Output

The program prints:
- Summary of the parsed problem.
- Expected optimal time from start (before the initial observation at the start vertex).
- A printout of reachable belief-states (limited by `--print-limit`) with `V(b)` and the optimal action.
- Simulation traces for `--sims` sampled instances.
