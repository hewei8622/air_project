
## this is an example to use solar enegry to produce extra AIR using additional water sources
# rather than ones from glaciers

# a simple energy system (demand) has been added as network_energy


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

network.add("Bus", "solar bus", carrier="solar")




network.add(
    "Generator",
    "glacier",
    bus="ice bus",
    carrier="ice",
    capital_cost=0,
    p_nom=100,
    p_max_pu=[0.0, 0.2, 0.2, 0.2, 0,0,0,0,0,0,0,0],
    p_nom_extendable=False
)

network.add(
    "Generator",
    "solar",
    bus="solar bus",
    carrier="solar",
    capital_cost=0,
    p_nom=100,
    p_max_pu=[0, 0, 0, 0.2, 0.3,0.4,0.4,0.3,0.2,0,0,0],
    p_nom_extendable=True
)


# network.add("Load", "ice load", bus="ice bus", p_set=[0.0, 10, 30, 10])

#

network.add(
    "Link",
    "ice to water",
    bus0="ice bus",
    bus1="water bus",
    capital_cost=10,
    efficiency=1,
    p_nom_extendable = True
)

network.add(
    "Link",
    "solar to ice",
    bus0="solar bus",
    bus1="ice bus",
    capital_cost=10,
    efficiency=.5,
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

ax.plot(network.snapshots, np.array(network.generators.p_nom_opt['solar'])*np.array([0, 0, 0, 0.2, 0.3,0.4,0.4,0.3,0.2,0,0,0]),'--',label='solar')
ax.plot(network.snapshots, network.generators_t.p['glacier'],label='glacier2AIR')
ax.plot(network.snapshots, network.loads_t.p,label='water load')
ax.plot(network.snapshots, network.links_t.p0, label=['ice2water','solar2ice'])
ax.legend()

fig, ax1 = plt.subplots()
ax1.plot(network.snapshots, network.stores_t.e,label=['AIR','water store'])
ax1.legend()

# network.generators_t.p, network.loads_t.p, network.links_t.p0, network.stores_t.e
fig, ax2 = plt.subplots()
ax2.plot(network.snapshots, 0.5*np.array(network.links_t.p0['ice to water']),label='energy gen by AIR')
ax2.legend()




network_energy = pypsa.Network()
network_energy.set_snapshots(np.arange(0, 12))

network_energy.add("Carrier", "solar")
network_energy.add("Carrier", "air hydro")
network_energy.add("Carrier", "demand")


network_energy.add("Bus", "demand bus", carrier="demand")


network_energy.add(
    "Generator",
    "solar demand",
    bus="demand bus",
    carrier="solar",
    capital_cost=200,
    p_nom=20,
    p_max_pu=[0, 0, 0, 0.2, 0.3,0.4,0.4,0.3,0.2,0,0,0],
    p_nom_extendable=True
)

network_energy.add(
    "Generator",
    "AIR gen",
    bus="demand bus",
    carrier="air hydro",
    capital_cost=5,
    p_nom_extendable=True
)

network_energy.add(
    "Store", "batt demand", bus="demand bus", e_cyclic=False, e_nom_extendable=True,
    capital_cost=10)

network_energy.add("Load", "energy load", bus="demand bus", p_set=[0, 0, 0, 20,10,5,5,10,10,20,0,0])

m = network_energy.optimize.create_model()
gen_AIR= m['Generator-p'].loc[:,"AIR gen"]
# sum_link=link_AIR.sum('snapshot')
hydro_eff=0.5
m.add_constraints(gen_AIR==np.array(hydro_eff*np.array(network.links_t.p0['ice to water'])).tolist(), name='AIR energy gen')


# network.optimize(network.snapshots)
network_energy.optimize.solve_model(solver_name='glpk')

# print("Objective:", network.objective)

# network.generators_t.p.plot.area(figsize=(9, 4))

# print(network_energy.generators_t.p)
# print(network_energy.generators)


fig, ax_e = plt.subplots()
ax_e.plot(network_energy.snapshots, np.array(network_energy.generators.p_nom_opt['solar demand'])*np.array([0, 0, 0, 0.2, 0.3,0.4,0.4,0.3,0.2,0,0,0]),'--',label='solar')
ax_e.plot(network_energy.snapshots, network_energy.generators_t.p,label=['solar used','AIR'])
ax_e.plot(network_energy.snapshots, network_energy.stores_t.p,label='batt')

ax_e.plot(network_energy.snapshots, network_energy.loads_t.p,label='energy load')
ax_e.legend()


plt.show()

