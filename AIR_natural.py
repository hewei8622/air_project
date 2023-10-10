import pypsa
import numpy as np
import pandas as pd

import matplotlib as mpl
import matplotlib.pyplot as plt
# mpl.use('macosx')

network = pypsa.Network()
network.set_snapshots(np.arange(0, 12))

network.add("Carrier", "water")
network.add("Carrier", "ice")

network.add("Bus", "ice bus", carrier="ice")
network.add("Bus", "water bus", carrier="water")

network.add(
    "Generator",
    "glacier",
    bus="ice bus",
    carrier="ice",
    capital_cost=0,
    p_nom=100,
    p_max_pu=[0.0, 0.2, 0.3, 0.3, 0.4,0,0,0,0,0,0,0],
    p_nom_extendable=False
)


# network.add("Load", "ice load", bus="ice bus", p_set=[0.0, 10, 30, 10])

#
# network.add(
#     "Link",
#     "ice to water",
#     bus0="ice bus",
#     bus1="water bus",
#     capital_cost=10,
#     efficiency=1,
#     p_set=[0,0,0,0,0,0,0,20,20,20,20,20]
# )

network.add(
    "Link",
    "ice to water",
    bus0="ice bus",
    bus1="water bus",
    capital_cost=10,
    efficiency=1,
    p_nom_extendable = True
)

network.add("Load", "water load", bus="water bus", p_set=[0.0, 0, 0, 0,0,0,0,0,0,0,40,40])

network.add(
    "Store", "AIR", bus="ice bus", e_cyclic=False, e_nom_extendable=True, capital_cost=10)

network.add(
    "Store", "water store", bus="water bus", e_cyclic=False, e_nom_extendable=True,
    capital_cost=10, standing_loss=0.01)


m = network.optimize.create_model()
link_AIR= m['Link-p'].loc[:,"ice to water"]
# sum_link=link_AIR.sum('snapshot')
m.add_constraints(link_AIR==[0,0,0,0,0,0,0,20,20,20,20,20], name='AIR discharge')


# network.optimize(network.snapshots)
network.optimize.solve_model(solver_name='glpk')

# print("Objective:", network.objective)

# network.generators_t.p.plot.area(figsize=(9, 4))

fig, ax = plt.subplots()

ax.plot(network.snapshots, network.generators_t.p,label='glacier2AIR')
ax.plot(network.snapshots, network.loads_t.p,label='water load')
ax.plot(network.snapshots, network.links_t.p0, label='ice2water')
ax.legend()

fig, ax1 = plt.subplots()

ax1.plot(network.snapshots, network.stores_t.e,label=['AIR','water store'])
ax1.legend()

# network.generators_t.p, network.loads_t.p, network.links_t.p0, network.stores_t.e

plt.show()

