import math
import itertools
from random import randint
from typing import Iterable, List, Tuple

import matplotlib.pyplot as plt

Point = Tuple[int, int]


def get_distance(point1: Point, point2: Point) -> float:
    return math.dist(point1, point2)


def generate_randoms(n: int, xmax: int, ymax: int) -> List[Point]:
    return [
        (randint(0, xmax), randint(0, ymax))
        for _ in range(n)
    ]


def config_plot_points(points: Iterable[Point], color: str) -> None:
    x = [p[0] for p in points]
    y = [p[1] for p in points]
    plt.scatter(
        x, y,
        c=color, edgecolors='black',
        linewidths=0.5, alpha=0.9
    )


def config_plot_line(c: Point, s: Point, dist: float, color: str, lw: float, ls: str) -> None:
    if c is None or s is None:
        return
    x = [s[0], c[0]]
    y = [s[1], c[1]]
    plt.plot(
        x, y,
        ls=ls, color=color, linewidth=lw
    )
    plt.annotate(
        f'{dist:.2f}',
        # midpoints
        (
            (sum(x) / 2) + 1,
            (sum(y) / 2) + 1
        )
    )


def eval_obj_func(alpha: int, clients: List[Point], facilities: List[Point]) -> float:
    max_c_dist = 0
    c_max = None
    s_c_max = None
    for c in clients:
        min_subset_dist = math.inf
        subset_min = None
        for subset in itertools.combinations(facilities, alpha):
            max_s_dist = 0
            s_max = None
            for s in subset:
                if (dist := get_distance(s, c)) > max_s_dist:
                    max_s_dist = dist
                    s_max = s
                    print(f'New maximum for subset d(s, c): {max_s_dist}')
                
                config_plot_line(c, s, dist, 'gray', 1, ':')
                config_plot_line(c, subset_min, min_subset_dist, 'orange', 1.3, ':')
                config_plot_line(c_max, s_c_max, max_c_dist, 'yellowgreen', 1.6, '--')
                plt.scatter(
                    c[0], c[1],
                    c='skyblue', edgecolors='black',
                    marker='*', linewidths=0.5, s=12**2
                )
                plt.scatter(
                    [s[0] for s in subset], [s[1] for s in subset],
                    c='red', edgecolors='black',
                    marker='X', linewidths=0.5, s=12**2
                )
                config_plot_points(set(clients) - set([c]), 'skyblue')
                config_plot_points(set(facilities) - set(subset), 'red')
                plt.show()

            if max_s_dist < min_subset_dist:
                min_subset_dist = max_s_dist
                subset_min = s_max
                print(f'New minimum, client allocated: {min_subset_dist}')
        if min_subset_dist > max_c_dist:
            max_c_dist = min_subset_dist
            s_c_max = subset_min
            c_max = c
            print(f'New objective function value: {max_c_dist}')
    
    config_plot_line(c_max, s_c_max, max_c_dist, 'yellowgreen', 1.6, '--')
    config_plot_points(clients, 'skyblue')
    config_plot_points(facilities, 'red')
    plt.show()

    return max_c_dist
