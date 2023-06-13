# _α_-neighbor _p_-center problem (ANPCP)

The _α_-neighbor _p_-center problem (ANPCP) is a location problem in which the goal is to select $p$ centers such that the maximum distance of a user to its $\alpha$-th closest open facility is minimized.
This is the repository of the source code used for an undergraduate thesis and a future research paper, whose main goal are to design efficient heuristic and metaheuristic procedures to solve the ANPCP.

A heuristic is any approach to problem solving that employs a practical method that is not guaranteed to be optimal, perfect, or rational, but is nevertheless sufficient for reaching an immediate, short-term goal or approximation.

The ANPCP arises in the modeling of the placement of emergency facilities, such as fire stations or hospitals, where the aim is to have a minimum guaranteed response time between a customer or demand point and its center by considering a notion of fault tolerance, i.e., providing backup centers in case one of them fails to respond to an emergency.
This ensures that even if up to $\alpha - 1$ facilities fail, every customer has an open facility close to it.

# Thesis

A Greedy Randomized Adaptive Search Procedure (GRASP) is proposed to solve the ANPCP.
The key component of this metaheuristic is a fast local search algorithm, which provides reasonable quality solutions in less time than a greedy interchange due to the use of data structures that store how the assignments between users and centers behave after a swap of facilities, allowing to reuse these expensive computations by accessing them instead of recalculating them.
This algorithm is referred to as the Alpha Fast Vertex Substitution (A-FVS) method, which is an adaptation from an algorithm with the same name designed for the PCP.
We experimentally show that the A-FVS is significantly faster than a generic greedy interchange for all the tested cases (750 times faster for the largest instance), as well as the results of using our proposed GRASP to solve instances from the well-known TSPLIB library.

The research concerning this thesis goes up to the development of the A-FVS algorithm and the experimentation with the proposed GRASP without extra components, as can be seen in its paper.

## Abstract

We present an enhanced implementation of the vertex substitution local search procedure for the ANPCP.
The heuristic, called Alpha Fast Vertex Substitution (A-FVS), is significantly faster due to the use of data structures that store how the assignments between users and centers behave after a swap of facilities, allowing to reuse these expensive computations by accessing them instead of recalculating them.
This intelligent way of exploiting the structure of the objective function led to significant computational speed-up times for all cases.
The A-FVS is integrated as a local search phase into a Greedy Randomized Adaptive Search Procedure (GRASP).
Empirical evidence shows that GRASP outperforms A-FVS.

The thesis file is available in PDF at [Releases](https://github.com/netotz/alpha-neighbor-p-center-problem/releases/tag/thesis).
Or download it directly [here](https://github.com/netotz/alpha-neighbor-p-center-problem/releases/download/thesis/anpcp-thesis.pdf).

# Blog posts

- [Decomposing an objective function](https://netotz.github.io/posts/decomposing-of/)
- [The process of designing a new algorithm](https://netotz.github.io/posts/a-fvs/)

# Source code

I've been using interactive programming most of the time, you can notice there are a lot of Jupyter Notebooks in the code.
Some of them will fail to run now because I've changed the code many times.
I didn't want to delete them though because this repository is more like a history of the changes made to the codebase used for the research.

The code here is not intended to be a production application ready to be used or a package to be installed, but simply a proof of the experiments and tests conducted for the research.

The `debugger.py` file contains some common lines of code that will run the solver and related classes.

There are some CLI scripts that I used to run long experiments with GRASP, they are the files starting with `anpcp/grasp_*.py`.
Then I used some Jupyter Notebooks to load the results of the experiments and filter the data to generate LaTeX tables.

The folder `anpcp/nb_results/` is full of output files, generated from the conducted experiments.

# Common acronyms

| Acronym |                                   Full name |
| :------ | ------------------------------------------: |
| PCP     |                          $p$-center problem |
| ANPCP   |        $\alpha$-neighbor $p$-center problem |
| PDP     |                      $p$-dispersion problem |
| PMP     |                          $p$-median problem |
| FAGI    |       Fast Algorithm for Greedy Interchange |
| FVS     |                    Fast Vertex Substitution |
| A-FVS   |              Alpha Fast Vertex Substitution |
| GRASP   | Greedy Randomized Adaptive Search Procedure |
