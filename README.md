## IntroToAI

Python version: 3.11

## Setup
```bash
git clone https://github.com/ahmad-essa99/IntroToAI.git
cd IntroToAI
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt

## General

in this assignment we have used several major algorithms:
1. shortest path by Dijkstra (for stupid greedy, thief agent and for simulator initial setup)
2. MST value for heuristic calculation
3. greedy search
4. A* and real time A*


the simulator starts by reading and parsing input file , from the input file + user input we get:
1. static info: 
	1.1 graph structure(including verticies, edges, weights, flooded/not flooded edges) 
	1.2 some constants (equip/unequip time , slowing factor)
	1.3 agents types and info

2. "world state" info, such as:
	2.1 stuck people locations
	2.2 kits locations
	2.3 agents locations (and equipped/not equipped)


as a setup our simulator runs 1 Dijkstra from each target vertex and stores results,
this result is very helpful for every agent that computes MST heuristic on the relaxed graph. 
- this is a TRADE OFF: if we remove it our code will still work (but it will consume more time during execution time , and less time during setup)

then we loop over all our agents, for each agent we call:
	agent.make_move() -> this returns an op that simulator can perform on the same agent
			     and update world state accordingly.

	for example: make_move for agent 2 can return (TRAVERSE, 3) or (EQUIP) ..

every agent implements make_move() method, all 3 agents use the same heuristic function:

given a state S (current_vertex, is_equipped, targeted_vertices, kits_locations)

we compute an MST on the relaxed graph(no flooded edges), when we compute it we take into account (current_vertex + targeted_vertices)
this computation on a small verticies set, is very fast (especially with our setup above).

MST on the relaxed graph is admissible because: given current vertex, this is the shortest way to visit all targets
(we use relaxed graph meaning we consider all edges are not flooded , this means that REAL cost is at least what we are computing , or even more)

so for a state S, we compute MST(S + targeted_vertices)
then h(S) = 
if not is_equipped -> MST
else -> min(slowing_factor * MST, MST + unequip time)
	- if is_equipped then heuristic value is slowing_factor * MST OR agent can unequip and then traverse with MST cost , se we
 	  take minimum of two cases.
