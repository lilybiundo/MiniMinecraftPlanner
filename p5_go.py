import json
with open('Crafting.json') as f:
	Crafting = json.load(f)

# List of items that can be in your inventory:
print "Crafting['Items']"
print Crafting['Items']
# example: ['bench', 'cart', ..., 'wood', 'wooden_axe', 'wooden_pickaxe']

# List of items in your initial inventory with amounts:
print "Crafting['Initial']"
print Crafting['Initial']
# {'coal': 4, 'plank': 1}

# List of items needed to be in your inventory at the end of the plan:
# (okay to have more than this; some might be satisfied by initial inventory)
print "Crafting['Goal']"
print Crafting['Goal']
# {'stone_pickaxe': 2}

# Dict of crafting recipes (each is a dict):
print Crafting['Recipes']['craft stone_pickaxe at bench']
# example:
# {	'Produces': {'stone_pickaxe': 1},
#	'Requires': {'bench': True},
#	'Consumes': {'cobble': 3, 'stick': 2},
#	'Time': 1
# }


def make_checker(rule):
	# this code runs once
	# do something with rule['Consumes'] and rule['Requires']
	def check(state):
		# this code runs millions of times
		return True # or False
	
	return True
	
def make_effector(rule):
	# this code runs once
	# do something with rule['Produces'] and rule['Consumes']
	def effect(state):
		# this code runs millions of times
		return next_state
	
	return True
	
	
from collections import namedtuple
Recipe = namedtuple('Recipe',['name','check','effect','cost'])

all_recipes = []

for name, rule in Crafting['Recipes'].items():
	checker = make_checker(rule)
	effector = make_effector(rule)
	recipe = Recipe(name, checker, effector, rule['Time'])
	all_recipes.append(recipe)

from heapq import heappush, heappop	
def search(graph, initial, is_goal, limit, heuristic):
	dist = {}
	dist[initial] = 0
	prev = {}
	prev[initial] = None
	queue = []
	heappush(queue, (dist[initial], initial))
	finished = False
	
	counter = 0;
	while queue and counter < limit:
		counter += 1
		bdist, state = heappop(queue)
		
		#print str(bdist) + " " + str(state)
		
		if is_goal(state):
			finished = True
			break
			
		neighbors = graph(state) # returns list of (action, next_state, cost) tuples
		
		for n in neighbors:
			alt = bdist + n[2] + heuristic(n[1])
			#print str(n) + " " + str(alt)
			if n[1] not in dist or alt < dist[n[1]]:
				dist[n[1]] = alt
				prev[n[1]] = state
				#print "Prev of " + str(n[1]) + " = " + str(prev[n[1]])
				heappush(queue, (dist[n[1]], n[1]))

				
	if finished:
		plan = []
		total_cost = bdist
		while state:
			#print state
			plan.append(state)
			state = prev[state]
		plan.reverse()
		
	else:
		print "No valid path found"
		plan = []
		total_cost = 0

	return total_cost, plan
	
print "Testing A* search"
t_initial = 'a'
t_limit = 20
edges = {'a': {'b': 1, 'c': 10}, 'b':{'c':1}}

def t_graph(state):
	for next_state, cost in edges[state].items():
		yield ((state, next_state), next_state, cost)
		
def t_is_goal(state):
	return state == 'c'
	
def t_heuristic(state):
	return 0

print search(t_graph, t_initial, t_is_goal, t_limit, t_heuristic)