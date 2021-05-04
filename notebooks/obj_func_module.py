import math
import itertools
from random import randint
from typing import List, Tuple

import matplotlib.pyplot as plt

Point = Tuple[int, int]

def get_distance(point1: Point, point2: Point) -> float:
    return math.dist(point1, point2)

def generate_randoms(n: int, xmax: int, ymax: int) -> List[Point]:
    return [
        (randint(0, xmax), randint(0, ymax))
        for _ in range(n)
    ]

def config_plot_points(points: List[Point], color: str) -> None:
    x = [p[0] for p in points]
    y = [p[1] for p in points]
    plt.scatter(
        x, y,
        facecolor=color, edgecolor='black',
        linewidth=0.3, alpha=0.9
    )

def plot_instance(clients: List[Point], facilities: List[Point], s: Point, c: Point, dist: float) -> None:
    config_plot_points(clients, 'skyblue')
    config_plot_points(facilities, 'red')

    x = [s[0], c[0]]
    y = [s[1], c[1]]
    plt.plot(
        x, y,
        ls=':', color='gray'
    )
    plt.annotate(
        f'{dist:.2f}',
        # midpoints
        (
            (sum(x) / 2) + 1,
            (sum(y) / 2) + 1
        )
    )

    plt.show()

def eval_obj_func(alpha: int, clients: List[Point], facilities: List[Point]) -> float:
    max_client_dist = 0
    for c in clients:
        print(f'\nCurrent client: {c}')
        min_subset_dist = math.inf
        for subset in itertools.combinations(facilities, alpha):
            print(f'\nCurrent subset: {subset}')
            max_distance = 0
            for s in subset:
                print(f'Point from subset: {s}')
                if (dist := get_distance(s, c)) > max_distance:
                    max_distance = dist
                    print(f'New maximum d(s, c): {max_distance}')
                plot_instance(clients, facilities, s, c, dist)
            if max_distance < min_subset_dist:
                min_subset_dist = max_distance
                print(f'New minimum d(c, S): {min_subset_dist}')
        if min_subset_dist > max_client_dist:
            max_client_dist = min_subset_dist
            print(f'New maximum distance: {max_client_dist}')
    
    return max_client_dist
