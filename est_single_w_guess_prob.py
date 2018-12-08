from fvs import *
import os
import pickle

def est_num_itr(alg, graph, weights, opt, samples):
    n = 0
    for _ in range(samples):
        n += alg(graph, weights, opt)
    return n / float(samples)

if __name__ == "__main__":
    path = "data/"
    files = os.listdir(path)
    if not files:
        file_no = 0
    else:
        file_no = int(files[-1][:-7], 10) + 1

    num_graphs = 10
    samples = 100
    n = 10
    p = 0.5
    max_weight = 100
    alg_deg = lambda g, w, opt: sample_num_itr_wra(g, w, opt, p=prob_deg)
    alg_deg_weight = lambda g, w, opt: sample_num_itr_wra(g, w, opt, p=prob_deg_weights)

    # estimated expected number of iterations until an optimal fvs is found
    max_exp_itrs_d = 0
    max_exp_itrs_dw = 0
    for i in range(samples):
        # generate instance
        graph, weights = generate_random_fvs_instance(n, p, max_weight)
        # find optimal
        optF, optW = optimal_fvs(graph, weights)
        print("opt fvs: " + str(optF))
        print("opt weight: ", optW)
        # estimate degree
        exp_itrs_d = est_num_itr(alg_deg, graph, weights, optW, samples)
        max_exp_itrs_d = max(max_exp_itrs_d, exp_itrs_d)
        print("expected number of iterations for degree: " + str(exp_itrs_d))
        print("max expected iterations for degree: " + str(max_exp_itrs_d))
        # estimate weight degree
        exp_itrs_dw = est_num_itr(alg_deg_weight, graph, weights, optW, samples)
        max_exp_itrs_dw = max(max_exp_itrs_dw, exp_itrs_dw)
        print("expected number of iterations for degree/weight: " + str(exp_itrs_dw))
        print("max expected iterations for degree/weight: " + str(max_exp_itrs_dw))
        file_name = path + "{0:0=10d}".format(file_no) + ".pickle"
        with open(file_name, 'wb') as f:
            pickle.dump((graph, weights, optF, optW, samples, exp_itrs_d, exp_itrs_dw), f)
        file_no += 1
