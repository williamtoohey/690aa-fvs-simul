from fvs import *
import os
import pickle

path = "C:/Users/agiera/linux/cs690AA/690aa-fvs-simul/data/"
files = os.listdir(path)
if not files:
    file_no = 0
else:
    file_no = int(files[-1][:-7], 10) + 1

samples = 20
n = 8
p = 0.5
max_weight = 100
p_func = prob_deg_weights

# total number of function calls to `prob_alg`
total_itr = 0
# estimated expected number of iterations until an optimal fvs is found
exp_itr = 0.0
for i in range(samples):
    graph, weights = generate_random_fvs_instance(n, p, max_weight)
    size = len(graph.nodes())
    optF, optW = optimal_fvs(graph, weights)
    print("opt fvs: " + str(optF))
    print("opt weight: ", optW)
    fvs, w, itrs = sample_num_itr_wra(graph, weights, optW, p=p_func)
    total_itr += itrs
    exp_itr = total_itr / (i+1.0)
    print("sol fvs: " + str(fvs))
    print("sol weight: " + str(w))
    print("expected number of iterations: " + str(exp_itr))
    file_name = path + "{0:0=10d}".format(file_no) + ".pickle"
    with open(file_name, 'wb') as f:
        pickle.dump((graph, weights, optF, optW, fvs, w, itrs), f)
    file_no += 1
