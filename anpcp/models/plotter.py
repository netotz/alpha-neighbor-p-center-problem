from typing import Optional

import matplotlib.pyplot as plt

from models.solver import Solver, NotAllocatedError


def plot_solver(
    solver: Solver,
    with_annotations: bool = True,
    with_assignments: bool = True,
    axis: bool = False,
    dpi: Optional[int] = None,
    filename: str = "",
) -> None:
    fig, ax = plt.subplots()
    # plot closed facilities
    ax.scatter(
        [
            f.x
            for f in solver.instance.facilities
            if f.index in solver.solution.closed_facilities
        ],
        [
            f.y
            for f in solver.instance.facilities
            if f.index in solver.solution.closed_facilities
        ],
        marker="s",
        color="gray",
        label="Closed facilities",
        linewidths=0.2,
        alpha=0.8,
        edgecolors="black",
    )

    # plot users
    ax.scatter(
        [u.x for u in solver.instance.users],
        [u.y for u in solver.instance.users],
        color="tab:blue",
        label="Users",
        linewidths=0.3,
        alpha=0.8,
        edgecolors="black",
    )

    # plot centers (open facilities)
    if solver.solution.open_facilities:
        ax.scatter(
            [
                f.x
                for f in solver.instance.facilities
                if f.index in solver.solution.open_facilities
            ],
            [
                f.y
                for f in solver.instance.facilities
                if f.index in solver.solution.open_facilities
            ],
            marker="s",
            color="red",
            label="Centers ($S$)",
            linewidths=0.3,
            alpha=0.8,
            edgecolors="black",
        )

    # plot indexes of nodes
    if with_annotations:
        for u in solver.instance.users:
            ax.annotate(u.index, (u.x, u.y))

        for f in solver.instance.facilities:
            ax.annotate(f.index, (f.x, f.y))

    # plot assignments
    if with_assignments:
        for user in solver.instance.users:
            try:
                alphath = solver.get_kth_closest(user.index, solver.alpha)
            except NotAllocatedError:
                continue

            facility = solver.instance.facilities[alphath.index]
            color = (
                "orange"
                if alphath.index == solver.solution.critical_allocation.index
                and alphath.distance == solver.solution.get_obj_func()
                else "gray"
            )
            ax.plot(
                (user.x, facility.x),
                (user.y, facility.y),
                color=color,
                linestyle=":",
                alpha=0.5,
            )

    ax.legend(loc=(1.01, 0))
    if dpi:
        fig.set_dpi(dpi)

    if not axis:
        ax.set_axis_off()

    if filename:
        fig.savefig(filename, bbox_inches="tight")

    plt.show()
