## this is a separate test of the energy system (additinal enegry system). It has been added to AIR_eng_01


import pypsa
import numpy as np
import pandas as pd

import matplotlib as mpl
import matplotlib.pyplot as plt
# mpl.use('macosx')



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
    capital_cost=10,
    p_nom=200,
    p_max_pu=[0, 0, 0, 0.2, 0.3,0.4,0.4,0.3,0.2,0,0,0],
    p_nom_extendable=True
)

network_energy.add(
    "Generator",
    "AIR gen",
    bus="demand bus",
    carrier="air hydro",
    capital_cost=10,
    p_nom_extendable=True
)

network_energy.add(
    "Store", "batt demand", bus="demand bus", e_cyclic=False, e_nom_extendable=True,
    capital_cost=10)

network_energy.add("Load", "energy load", bus="demand bus", p_set=[0, 0, 0, 20,10,5,5,10,10,20,0,0])


m = network_energy.optimize.create_model()
gen_AIR= m['Generator-p'].loc[:,"AIR gen"]
# sum_link=link_AIR.sum('snapshot')
m.add_constraints(gen_AIR==[0,0,0,0,0,0,0,10,10,10,10,10], name='AIR energy gen')


# network.optimize(network.snapshots)
network_energy.optimize.solve_model(solver_name='glpk')

# print("Objective:", network.objective)

# network.generators_t.p.plot.area(figsize=(9, 4))

fig, ax_e = plt.subplots()

ax_e.plot(network_energy.snapshots, network_energy.generators_t.p,label=['solar','AIR'])
ax_e.plot(network_energy.snapshots, network_energy.stores_t.p,label='batt')

ax_e.plot(network_energy.snapshots, network_energy.loads_t.p,label='energy load')
ax_e.legend()

# network.generators_t.p, network.loads_t.p, network.links_t.p0, network.stores_t.e

plt.show()

