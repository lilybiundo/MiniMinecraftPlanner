import json
import time
with open('Crafting.json') as f:
	Crafting = json.load(f)

item_index = {}
item_i = 0
Items = Crafting['Items']

for item in Crafting['Items']:
	item_index[item] = item_i
	item_i += 1

state = ()
state_dict = {}

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
#print Crafting['Recipes'].items()#['craft stone_pickaxe at bench']
# example:
# {	'Produces': {'stone_pickaxe': 1},
#	'Requires': {'bench': True},
#	'Consumes': {'cobble': 3, 'stick': 2},
#	'Time': 1
# }


def make_checker(rule):
	# this code runs once
	# do something with rule['Consumes'] and rule['Requires']
	consumes, requires = rule.get('Consumes', {}), rule.get('Requires', {})
	consumption_pairs = [(item_index[item],consumes[item]) for item in consumes]
	requirement_pairs = [(item_index[item],1) for item in requires]
	both_pairs = consumption_pairs + requirement_pairs
	
	def check(state):
		# this code runs millions of times
		return all([state[i] >= v for i,v in both_pairs])
	
	return check
	
def make_effector(rule):
	# this code runs once
	# do something with rule['Produces'] and rule['Consumes']
	produces, consumes = rule.get('Produces', {}), rule.get('Consumes', {})
	delta_pairs = []
	for item in item_index:
		value = 0
		if item in produces:
			value += produces[item]
		if item in consumes:
			value -= consumes[item]
		delta_pairs.append(tuple([item_index[item], value]))		
	
	def effect(state):
		# this code runs millions of times
		return tuple([state[i] + delta for i, delta in delta_pairs])
	
	return effect
	
def inventory_to_tuple(d):
		return tuple(d.get(name, 0) for i,name in enumerate(Items))
			
def make_goal_checker(goal):
	
	def check(state):
		for item in goal:
			index = item_index[item]
			i_check = state[index]
			print "State: " + str(state) + " item: " + str(item)
			print "index: " + str(index) + " i_check: " + str(i_check)
			if i_check < goal[item]:
				return False
		return True
	
	return check
		

	
from collections import namedtuple
Recipe = namedtuple('Recipe',['name','check','effect','cost'])

all_recipes = []

for name, rule in Crafting['Recipes'].items():
	checker = make_checker(rule)
	effector = make_effector(rule)
	recipe = Recipe(name, checker, effector, rule['Time'])
	all_recipes.append(recipe)
	
def graph(state):
	for r in all_recipes:
		if r.check(state):
			yield (r.name, r.effect(state), r.cost)
			
def heuristic(state):
	return 0
	
from heapq import heappush, heappop	
def search(graph, initial, is_goal, limit, heuristic):
	dist = {}
	dist[initial] = 0
	prev = {}
	prev[initial] = None
	queue = []
	heappush(queue, (dist[initial], initial))
	finished = False
	
	t_start = time.time()
	t_deadline = t_start + limit
	while queue:
		bdist, state = heappop(queue)
		print "bdist: " + str(bdist) + " state: " + str(state)
		
		#print str(bdist) + " " + str(state)
		
		if is_goal(state):
			print "success?"
			finished = True
			break
			
		neighbors = graph(state) # returns list of (action, next_state, cost) tuples
		
		print "Neighbors: " + str(neighbors)
		
		for n in neighbors:
			alt = bdist + n[2] + heuristic(n[1])
			#print str(n) + " " + str(alt)
			if n[1] not in dist or alt < dist[n[1]]:
				dist[n[1]] = alt
				prev[n[1]] = state
				#print "Prev of " + str(n[1]) + " = " + str(prev[n[1]])
				heappush(queue, (dist[n[1]], n[1]))
				
		t_now = time.time()
		if t_now > t_deadline:
			break

				
	if finished:
		plan = []
		total_cost = bdist
		while state:
			print state
			plan.append(state)
			state = prev[state]
		plan.reverse()
		
	else:
		print "No valid path found"
		plan = []
		total_cost = 0

	return total_cost, plan
	
	
initial_state = inventory_to_tuple(Crafting['Initial'])

is_goal = make_goal_checker(Crafting['Goal'])

print search(graph, initial_state, is_goal, 5, heuristic)

"""
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
"""