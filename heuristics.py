import networkx as nx
import dwave_networkx as dnx
import igraph as ig
import pulp as plp
from pulp import GLPK
import numpy as np
import pandas as pd
import scipy.sparse as sp
import time
print(nx.__version__)


def greedy_search(adj, wts):
    '''
    Return MWIS set and the total weights of MWIS
    :param adj: adjacency matrix (sparse)
    :param wts: weights of vertices
    :return: mwis, total_wt
    '''
    wts = np.array(wts).flatten()
    verts = np.array(range(wts.size))
    ranks = np.argsort(-wts.flatten())
    wts_desc = wts[ranks]
    verts_desc = verts[ranks]
    mwis = set()
    nb_is = set()
    total_ws = 0.0
    for i in ranks:
        if i in nb_is:
            continue
        _, nb_set = np.nonzero(adj[i])
        mwis.add(i)
        nb_is = nb_is.union(set(nb_set))
    total_ws = np.sum(wts[list(mwis)])
    return mwis, total_ws


def dist_greedy_search(adj, wts, epislon=0.5):
    '''
    Return MWIS set and the total weights of MWIS
    :param adj: adjacency matrix (sparse)
    :param wts: weights of vertices
    :param epislon: 0<epislon<1, to determin alpha and beta
    :return: mwis, total_wt
    '''
    alpha = 1.0 + (epislon / 3.0)
    beta = 3.0 / epislon
    wts = np.array(wts).flatten()
    verts = np.array(range(wts.size))
    mwis = set()
    remain = set(verts.flatten())
    nb_is = set()
    while len(remain) > 0:
        seta = set()
        for v in remain:
            _, nb_set = np.nonzero(adj[v])
            nb_set = set(nb_set).intersection(remain)
            if len(nb_set) == 0:
                seta.add(v)
                continue
            w_bar_v = wts[list(nb_set)].max()
            if wts[v] >= w_bar_v / alpha:
                seta.add(v)
        mis_i = set()
        for v in seta:
            _, nb_set = np.nonzero(adj[v])
            nb_set = set(nb_set)
            if len(mis_i.intersection(nb_set)) == 0:
                mis_i.add(v)
                nb_is = nb_is.union(nb_set)
        mwis = mwis.union(mis_i)
        remain = remain - mwis - nb_is
    total_ws = np.sum(wts[list(mwis)])
    return mwis, total_ws


def local_greedy_search(adj, wts):
    '''
    Return MWIS set and the total weights of MWIS
    :param adj: adjacency matrix (sparse)
    :param wts: weights of vertices
    :return: mwis, total_wt
    '''
    wts = np.array(wts).flatten()
    verts = np.array(range(wts.size))
    mwis = set()
    remain = set(verts.flatten())
    vidx = list(remain)
    nb_is = set()
    while len(remain) > 0:
        for v in remain:
            # if v in nb_is:
            #     continue
            _, nb_set = np.nonzero(adj[v])
            nb_set = set(nb_set).intersection(remain)
            if len(nb_set) == 0:
                mwis.add(v)
                continue
            nb_list = list(nb_set)
            nb_list.sort()
            wts_nb = wts[nb_list]
            w_bar_v = wts_nb.max()
            if wts[v] > w_bar_v:
                mwis.add(v)
                nb_is = nb_is.union(set(nb_set))
            elif wts[v] == w_bar_v:
                i = list(wts_nb).index(wts[v])
                nbv = nb_list[i]
                if v < nbv:
                    mwis.add(v)
                    nb_is = nb_is.union(set(nb_set))
            else:
                pass
        remain = remain - mwis - nb_is
    total_ws = np.sum(wts[list(mwis)])
    return mwis, total_ws


def local_greedy_search_count(adj, wts):
    '''
    Return MWIS set and the total weights of MWIS and steps it takes
    :param adj: adjacency matrix (sparse)
    :param wts: weights of vertices
    :return: mwis, total_wt, step
    '''
    wts = np.array(wts).flatten()
    verts = np.array(range(wts.size))
    mwis = set()
    remain = set(verts.flatten())
    vidx = list(remain)
    nb_is = set()
    step = 0
    while len(remain) > 0:
        for v in remain:
            # if v in nb_is:
            #     continue
            _, nb_set = np.nonzero(adj[v])
            nb_set = set(nb_set).intersection(remain)
            if len(nb_set) == 0:
                mwis.add(v)
                continue
            nb_list = list(nb_set)
            nb_list.sort()
            wts_nb = wts[nb_list]
            w_bar_v = wts_nb.max()
            if wts[v] > w_bar_v:
                mwis.add(v)
                nb_is = nb_is.union(set(nb_set))
            elif wts[v] == w_bar_v:
                i = list(wts_nb).index(wts[v])
                nbv = nb_list[i]
                if v < nbv:
                    mwis.add(v)
                    nb_is = nb_is.union(set(nb_set))
            else:
                pass
        remain = remain - mwis - nb_is
        step += 1
    total_ws = np.sum(wts[list(mwis)])
    return mwis, total_ws, step


def local_greedy_search_stats(adj, wts):
    '''
    Return MWIS set and the total weights of MWIS and steps it takes
    :param adj: adjacency matrix (sparse)
    :param wts: weights of vertices
    :return: mwis, total_wt, step
    '''
    wts = np.array(wts).flatten()
    verts = np.array(range(wts.size))
    mwis = set()
    remain = set(verts.flatten())
    vidx = list(remain)
    nb_is = set()
    step = 0
    p2p = 0
    bst = 0
    while len(remain) > 0:
        bst += len(remain)
        for v in remain:
            # if v in nb_is:
            #     continue
            _, nb_set = np.nonzero(adj[v])
            nb_set = set(nb_set).intersection(remain)
            p2p += len(nb_set)
            if len(nb_set) == 0:
                mwis.add(v)
                continue
            nb_list = list(nb_set)
            nb_list.sort()
            wts_nb = wts[nb_list]
            w_bar_v = wts_nb.max()
            if wts[v] > w_bar_v:
                mwis.add(v)
                nb_is = nb_is.union(set(nb_set))
            elif wts[v] == w_bar_v:
                i = list(wts_nb).index(wts[v])
                nbv = nb_list[i]
                if v < nbv:
                    mwis.add(v)
                    nb_is = nb_is.union(set(nb_set))
            else:
                pass
        remain = remain - mwis - nb_is
        step += 1
    total_ws = np.sum(wts[list(mwis)])
    bst += len(list(mwis))
    return mwis, total_ws, step, p2p, bst


def local_greedy_search_overhead(adj, wts):
    '''
    Return MWIS set and the total weights of MWIS and steps it takes
    :param adj: adjacency matrix (sparse)
    :param wts: weights of vertices
    :return: mwis, total_wt, step
    '''
    wts = np.array(wts).flatten()
    verts = np.array(range(wts.size))
    mwis = set()
    overheads = {}
    oh_vec = np.zeros_like(wts)
    remain = set(verts.flatten())
    vidx = list(remain)
    nb_is = set()
    step = 0
    p2p = 0
    bst = 0
    while len(remain) > 0:
        bst += len(remain)
        for v in remain:
            # if v in nb_is:
            #     continue
            _, nb_set = np.nonzero(adj[v])
            nb_set = set(nb_set).intersection(remain)
            p2p += len(nb_set)
            oh_vec[v] += len(nb_set)
            if len(nb_set) == 0:
                mwis.add(v)
                continue
            nb_list = list(nb_set)
            nb_list.sort()
            wts_nb = wts[nb_list]
            w_bar_v = wts_nb.max()
            if wts[v] > w_bar_v:
                mwis.add(v)
                nb_is = nb_is.union(set(nb_set))
                oh_vec[v] += 1 # mute signaling
            elif wts[v] == w_bar_v:
                i = list(wts_nb).index(wts[v])
                nbv = nb_list[i]
                if v < nbv:
                    mwis.add(v)
                    nb_is = nb_is.union(set(nb_set))
                    oh_vec[v] += 1  # mute signaling
            else:
                pass
        remain = remain - mwis - nb_is
        step += 1
    total_ws = np.sum(wts[list(mwis)])
    bst += len(list(mwis))
    return mwis, total_ws, step, p2p, bst, oh_vec


def local_greedy_search_nstep(adj, wts, nstep=1):
    '''
    Return MWIS set and the total weights of MWIS
    :param adj: adjacency matrix (sparse)
    :param wts: weights of vertices
    :return: mwis, total_wt
    '''
    wts = np.array(wts).flatten()
    verts = np.array(range(wts.size))
    mwis = set()
    remain = set(verts.flatten())
    vidx = list(remain)
    nb_is = set()
    step = nstep
    while len(remain) > 0 and step:
        for v in remain:
            _, nb_set = np.nonzero(adj[v])
            nb_set = set(nb_set).intersection(remain)
            if len(nb_set) == 0:
                mwis.add(v)
                continue
            nb_list = list(nb_set)
            nb_list.sort()
            wts_nb = wts[nb_list]
            w_bar_v = wts_nb.max()
            if wts[v] > w_bar_v:
                mwis.add(v)
                nb_is = nb_is.union(set(nb_set))
            elif wts[v] == w_bar_v:
                i = list(wts_nb).index(wts[v])
                nbv = nb_list[i]
                if v < nbv:
                    mwis.add(v)
                    nb_is = nb_is.union(set(nb_set))
            else:
                pass
        remain = remain - mwis - nb_is
        step -= 1
    total_ws = np.sum(wts[list(mwis)])
    return mwis, total_ws, nb_is


def get_all_mis(adj):
    # G = ig.Graph()
    # G.Read_Adjacency(adj)
    g2 = ig.Graph.Adjacency(adj)
    # assert G.get_adjacency() == g2.get_adjacency()
    mis_all1 = g2.maximal_independent_vertex_sets()
    mis_all = np.zeros((len(adj), len(mis_all1)))
    for i in range(len(mis_all1)):
        mis_all[mis_all1[i],i] = 1
    return mis_all


def get_mwis(mis_all, wts):
    wts1 = np.expand_dims(wts, axis=1)
    utilities = np.multiply(mis_all,wts1).sum(axis=0)
    idx = np.argmax(utilities)
    return np.nonzero(mis_all[:, idx])[0], utilities[idx]


def mlp_gurobi(adj, wts, timeout=300):
    wts = np.array(wts).flatten()
    opt_model = plp.LpProblem(name="MIP_Model")
    x_vars = {i: plp.LpVariable(cat=plp.LpBinary, name="x_{0}".format(i)) for i in range(wts.size)}
    set_V = set(range(wts.size))
    constraints = {}
    ei = 0
    for j in set_V:
        _, set_N = np.nonzero(adj[j])
        # print(set_N)
        for i in set_N:
            constraints[ei] = opt_model.addConstraint(
                plp.LpConstraint(
                    e=plp.lpSum([x_vars[i], x_vars[j]]),
                    sense=plp.LpConstraintLE,
                    rhs=1,
                    name="constraint_{0}_{1}".format(j,i)))
            ei += 1
    objective = plp.lpSum(x_vars[i] * wts[i] for i in set_V )
    opt_model.sense = plp.LpMaximize
    opt_model.setObjective(objective)
    opt_model.solve(solver=plp.apis.GUROBI(mip=True, msg=False,
                                           timeLimit=timeout*1.1,
                                           # NodeLimit=35000,
                                           ImproveStartTime=timeout))
    opt_df = pd.DataFrame.from_dict(x_vars, orient="index", columns=["variable_object"])
    opt_df["solution_value"] = opt_df["variable_object"].apply(lambda item: item.varValue)
    solu = opt_df[opt_df['solution_value'] > 0].index.to_numpy()
    return solu, wts[solu].sum(), plp.LpStatus[opt_model.status]


def gradient_projection(adj, wts, ita=1.0):
    adj_theta0 = adj.astype(float).copy()
    cf0, cf1 = adj_theta0.nonzero()
    D = np.amax(adj.sum(1))
    nE = cf0.size
    discount = ita/(D*np.sqrt(nE))
    for i in range(cf0.size):
        adj_theta0[cf0[i], cf1[i]] = np.amax([wts[cf0[i]], wts[cf1[i]]])
    vec_relax = np.zeros(wts.shape)
    for i in range(wts.size):
        pts = adj_theta0[i,:].sum() - wts[i]
        if pts > ita:
            vec_relax[i] = ita/pts
        else:
            vec_relax[i] = 1.0
    while True:
        adj_theta1 = adj_theta0.copy()
        for j in range(wts.size):
            cf0, cf1 = adj_theta1.nonzero()
            for i in range(cf0.size):
                adj_theta1[cf0[i], cf1[i]] = adj_theta0[cf0[i], cf1[i]] - discount*(1 - vec_relax[cf0[i]] - vec_relax[cf1[i]])
            pts = adj_theta1[j, :].sum() - wts[j]
            if pts > ita:
                vec_relax[j] = ita/pts
            else:
                vec_relax[j] = 1.0
        delta = np.amax(np.abs(adj_theta0 - adj_theta1))
        if delta < 0.001:
            break
        adj_theta0 = adj_theta1.copy()
    return vec_relax


def mwis_mip_edge_relax(adj, wts):
    wts = np.array(wts).flatten()
    opt_model = plp.LpProblem(name="MIP_Model", sense=plp.LpMaximize)
    x_vars = {i: plp.LpVariable(lowBound=0.0, upBound=1.0,  name="x_{0}".format(i)) for i in range(wts.size)}
    set_V = set(range(wts.size))
    constraints = {}
    ei = 0
    for j in set_V:
        _, set_N = np.nonzero(adj[j])
        for i in set_N:
            constraints[ei] = opt_model.addConstraint(
                plp.LpConstraint(
                    e=plp.lpSum([x_vars[i], x_vars[j]]),
                    sense=plp.LpConstraintLE,
                    rhs=1,
                    name="constraint_{0}_{1}".format(j, i)))
            ei += 1

    objective = plp.lpSum(x_vars[i] * wts[i] for i in set_V)
    opt_model.setObjective(objective)
    # opt_model.solve(solver=plp.apis.GUROBI(mip=False, msg=True))
    opt_model.solve(solver=GLPK(msg=True))
    opt_df = pd.DataFrame.from_dict(x_vars, orient="index", columns=["variable_object"])
    opt_df["solution_value"] = opt_df["variable_object"].apply(lambda item: item.varValue)
    solu_relax = opt_df['solution_value'].to_numpy()
    return solu_relax


def mwis_mip_clique_relax(adj, wts):
    g = nx.from_scipy_sparse_matrix(adj)
    max_cliques = list(nx.algorithms.clique.find_cliques(g))
    opt_model = plp.LpProblem(name="MIP_Model", sense=plp.LpMaximize)
    x_vars = {i: plp.LpVariable(lowBound=0.0, upBound=1.0,  name="x_{0}".format(i)) for i in range(wts.size)}
    set_V = set(range(wts.size))
    constraints = {}
    ei = 0
    for j in range(len(max_cliques)):
        clique = max_cliques[j]
        constraints[ei] = opt_model.addConstraint(
            plp.LpConstraint(
                e=plp.lpSum(x_vars[i] for i in clique),
                sense=plp.LpConstraintLE,
                rhs=1.0,
                name="constraint_{0}".format(j)))
        ei += 1

    objective = plp.lpSum(x_vars[i] * wts[i] for i in set_V)
    opt_model.setObjective(objective)
    # opt_model.solve(solver=plp.apis.GUROBI(mip=False, msg=True))
    opt_model.solve(solver=GLPK(msg=True))
    opt_df = pd.DataFrame.from_dict(x_vars, orient="index", columns=["variable_object"])
    opt_df["solution_value"] = opt_df["variable_object"].apply(lambda item: item.varValue)
    solu_relax = opt_df['solution_value'].to_numpy()
    return solu_relax


def mp_greedy(adj, wts):
    wts = np.array(wts).flatten()
    solu_relax = mwis_mip_clique_relax(adj, wts)
    print(solu_relax)

    vec_x = np.full_like(wts, fill_value=np.nan)
    vec_x[solu_relax == 0.0] = 0
    vec_x[solu_relax == 1.0] = 1
    N = wts.size
    for n in range(N):
        vec_x1 = vec_x.copy()
        Vi = np.argwhere(np.isnan(vec_x1))
        if Vi.size == 0:
            break
        for v in Vi:
            neighbors = adj[v, :].toarray()[0, :].nonzero()[0]
            vec_nb = vec_x1[neighbors]
            if (vec_nb == 1.0).astype(float).sum() > 0:
                vec_x[v] = 0
            elif wts[v] > np.amax(wts[neighbors]):
                vec_x[v] = 1
            elif wts[v] == np.amax(wts[neighbors]):
                vn = np.argmax(wts[neighbors])
                if v < neighbors[vn]:
                    vec_x[v] = 1
            elif (vec_nb == 0.0).astype(int).sum() == neighbors.size:
                vec_x[v] = 1
            else:
                pass
        Vn = np.argwhere(np.isnan(vec_x))
        if Vn.size == Vi.size:
            v = np.argmax(wts[Vn])
            vec_x[Vn[v]] = 1

    solu = (vec_x == 1.0).astype(int).nonzero()[0]
    return set(solu), wts[solu].sum()


def mwis_mip_edge_dual(adj, wts):
    wts = np.array(wts).flatten()
    g = nx.from_scipy_sparse_matrix(adj)
    max_cliques = list(nx.algorithms.clique.find_cliques(g))
    opt_model = plp.LpProblem(name="MIP_Model", sense=plp.LpMinimize)
    x0, x1 = adj.nonzero()
    x_vars = {(x0[i], x1[i]): plp.LpVariable(lowBound=0.0, name="x_{0}_{1}".format(x0[i], x1[i])) for i in range(x0.size)}
    constraints = {}
    ei = 0
    for v in range(wts.size):
        neighbors = adj[v, :].toarray()[0, :].nonzero()[0]
        constraints[ei] = opt_model.addConstraint(
            plp.LpConstraint(
                e=plp.lpSum(x_vars[(v,i)] for i in neighbors),
                sense=plp.LpConstraintGE,
                rhs=wts[v],
                name="constraint_{0}".format(v)))
        ei += 1

    objective = plp.lpSum(x_var for x_var in x_vars.values())
    opt_model.setObjective(objective)
    # opt_model.solve(solver=plp.apis.GUROBI(mip=False, msg=True))
    opt_model.solve(solver=GLPK(msg=True))
    opt_df = pd.DataFrame.from_dict(x_vars, orient="index", columns=["variable_object"])
    opt_df["solution_value"] = opt_df["variable_object"].apply(lambda item: item.varValue)
    opt_df["name"] = opt_df["variable_object"].apply(lambda item: item.name)
    opt_df.set_index("name", inplace=True)
    solu_relax = adj.copy().astype(float)
    x0, x1 = solu_relax.nonzero()
    for i in range(x0.size):
        idx = 'x_{}_{}'.format(x0[i], x1[i])
        solu_relax[x0[i], x1[i]] = opt_df.loc[idx, 'solution_value']
    return solu_relax


def mp_color09(adj, wts, tao=0.0):
    solu_relax = mwis_mip_edge_dual(adj, wts)

    vec_x = np.full_like(wts, fill_value=np.nan)
    vec_c = np.zeros(wts.shape) # 0: green, 1: gray, 2: orange, 3: red
    for v in range(wts.size):
        val = solu_relax[v,:].sum() - wts[v]
        if val > tao:
            vec_x[v] = 0
            vec_c[v] = 1
    while True:
        Vi = np.argwhere(np.isnan(vec_x))
        if Vi.size == 0:
            break
        for v in Vi:
            neighbors = adj[v, :].toarray()[0, :].nonzero()[0]
            graynodes = neighbors[vec_c[neighbors] == 1]
            if graynodes.size > 0 and np.amax(solu_relax[v,graynodes]) > tao:
                vec_x[v] = 1
                vec_c[v] = 2
            oragnodes = neighbors[vec_c[neighbors] == 2]
            if oragnodes.size > 0:
                vec_x[v] = 0
                vec_c[v] = 1
        Vn = np.argwhere(np.isnan(vec_x))
        if Vn.size == Vi.size:
            break
    vec_x[vec_c==0] = 1
    vec_c[vec_c==0] = 3

    solu = (vec_x==1.0).astype(int).nonzero()[0]
    return set(solu), wts[solu].sum()


def mp_ising(adj, wts):
    NT = 128
    e_max = 5.0
    e_min = -5.0
    e_step = abs(e_max-e_min)/NT
    N = wts.size
    A = 10
    B = A/3
    uni = np.array([-1,1], dtype=float)
    spins = uni[np.random.randint(0, 2, size=wts.size)]
    for e in np.arange(e_min, e_max+e_step, e_step):
        beta = 10.0**e
        flip = spins.copy()
        # for v in range(N):
        #     neighbors = adj[v, :].toarray()[0, :].nonzero()[0]
        #     flipped = -flip[v]
        #     H_diff = 2*A*np.sum(wts[neighbors] * flip[neighbors])*wts[v]*flipped - 2*B*wts[v]*flipped
        #     if H_diff < 0:
        #         spins[v] = flipped
        #     elif np.random.uniform(0, 1) < np.exp(-beta * H_diff):
        #         spins[v] = flipped
        #     else:
        #         pass
        vec_r = np.random.uniform(0, 1, size=wts.size)
        vec_m = (vec_r < 1/N).astype(float)
        marked = np.nonzero(vec_m)[0]
        for v in marked:
            neighbors = adj[v, :].toarray()[0, :].nonzero()[0]
            if np.sum(vec_m[neighbors]) == 0 or vec_r[v] > np.amax(vec_r[neighbors]):
                flipped = abs(flip[v] - 1)
                H_flip = np.sum(flipped*flip[neighbors])*N - (float(N/3))*(np.sum(wts[neighbors]*flip[neighbors]) + wts[v]*flipped)
                H_prev = np.sum(flip[v]*flip[neighbors])*N - (float(N/3))*(np.sum(wts[neighbors]*flip[neighbors]) + wts[v]*flip[v])
                H_diff = H_flip - H_prev
                if H_diff < 0:
                    spins[v] = flipped
                elif np.random.uniform(0,1) < np.exp(-beta*H_diff):
                    spins[v] = flipped
                else:
                    pass
    # final check
    solu0 = np.nonzero(spins)[0]
    # indices = np.argsort(wts[solu0])
    # solu0 = solu0[indices]
    # while True:
    #     adj_1 = adj.copy()
    #     adj_1 = adj_1[solu0, :]
    #     adj_1 = adj_1[:, solu0]
    #     if adj_1.sum() == 0:
    #         break
    #     cf0, cf1 = adj_1.nonzero()
    #     if wts[solu0[cf0[0]]] > wts[solu0[cf1[0]]]:
    #         todel = cf1[0]
    #     else:
    #         todel = cf0[0]
    #     solu0 = np.delete(solu0, todel)
    wts_1 = wts[solu0]
    adj_1 = adj.toarray()
    adj_1 = adj_1[solu0, :]
    adj_1 = adj_1[:, solu0]
    adj_1 = sp.csr_matrix(adj_1)
    solu1, util1 = greedy_search(adj_1, wts_1)
    solu = solu0[list(solu1)]
    return set(solu), wts[solu].sum()



def test_heuristic():
    # Create a random graph
    t = time.time()
    graph = nx.generators.random_graphs.fast_gnp_random_graph(120, 0.05)
    for u in graph:
        graph.nodes[u]['weight'] = np.random.uniform(0, 1)  # np.square(np.random.randn())
        graph.nodes[u]['id'] = u
    print("Time to create graph: {}".format(time.time()-t))
    # Run Neighborhood Removal
    adj = nx.adjacency_matrix(graph)
    weights = np.array([graph.nodes[u]['weight'] for u in graph])
    vertices = np.array(range(len(weights)))

    t = time.time()
    mwis, total_wt = mp_greedy(adj, weights)
    print("Time of message passing (MP Greedy): {}".format(time.time()-t))
    print("Original Graph: {} nodes, {} edges.".format(graph.number_of_nodes(), graph.number_of_edges()))
    print("Partial MWIS Solution:\nTotal Weights: {}, IS size: {}\n{}".format(total_wt, len(mwis), mwis))
    print(dnx.is_independent_set(graph, list(mwis)))

    t = time.time()
    mwis, total_wt = mp_ising(adj, weights)
    print("Time of message passing (Ising): {}".format(time.time()-t))
    print("Original Graph: {} nodes, {} edges.".format(graph.number_of_nodes(), graph.number_of_edges()))
    print("Partial MWIS Solution:\nTotal Weights: {}, IS size: {}\n{}".format(total_wt, len(mwis), mwis))
    print(dnx.is_independent_set(graph, list(mwis)))

    t = time.time()
    mwis, total_wt = greedy_search(adj, weights)
    print("Time of greedy search: {}".format(time.time()-t))
    print("Original Graph: {} nodes, {} edges.".format(graph.number_of_nodes(), graph.number_of_edges()))
    print("Partial MWIS Solution:\nTotal Weights: {}, IS size: {}\n{}".format(total_wt, len(mwis), mwis))
    print(dnx.is_independent_set(graph, list(mwis)))

    t = time.time()
    mwis, total_wt = dist_greedy_search(adj, weights, 0.1)
    print("Time of distributed greedy approximation: {}".format(time.time()-t))
    print("Original Graph: {} nodes, {} edges.".format(graph.number_of_nodes(), graph.number_of_edges()))
    print("Partial MWIS Solution:\nTotal Weights: {}, IS size: {}\n{}".format(total_wt, len(mwis), mwis))
    print(dnx.is_independent_set(graph, list(mwis)))

    t = time.time()
    mwis, total_wt = local_greedy_search(adj, weights)
    print("Time of local greedy approximation: {}".format(time.time()-t))
    print("Original Graph: {} nodes, {} edges.".format(graph.number_of_nodes(), graph.number_of_edges()))
    print("Partial MWIS Solution:\nTotal Weights: {}, IS size: {}\n{}".format(total_wt, len(mwis), mwis))
    print(dnx.is_independent_set(graph, list(mwis)))


if __name__ == "__main__":
    test_heuristic()
