from enum import Enum

import matplotlib.pyplot as plt

from .solver import Solver, NotAllocatedError


class Label(Enum):
    CLOSED_FACILITIES = 0
    USERS = 1
    CENTERS = 2


class Language(Enum):
    ENGLISH = 0
    SPANISH = 1


LANGS_DICT = {
    Language.ENGLISH: {
        Label.CLOSED_FACILITIES: "Closed facilities",
        Label.USERS: "Users",
        Label.CENTERS: "Centers",
    },
    Language.SPANISH: {
        Label.CLOSED_FACILITIES: "Instalaciones cerradas",
        Label.USERS: "Usuarios",
        Label.CENTERS: "Centros",
    },
}


def plot_solver(
    solver: Solver,
    with_annotations: bool = True,
    with_assignments: bool = True,
    axis: bool = False,
    dpi: int | None = None,
    filename: str = "",
    language=Language.ENGLISH,
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
        label=LANGS_DICT[language][Label.CLOSED_FACILITIES],
        linewidths=0.2,
        alpha=0.8,
        edgecolors="black",
    )

    # plot users
    ax.scatter(
        [u.x for u in solver.instance.users],
        [u.y for u in solver.instance.users],
        color="tab:blue",
        label=LANGS_DICT[language][Label.USERS],
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
            label=f"{LANGS_DICT[language][Label.CENTERS]} ($S$)",
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
                "goldenrod"
                if alphath.index == solver.critical_allocation.index
                and alphath.distance == solver.solution.obj_func
                else "darkgray"
            )
            ax.plot(
                (user.x, facility.x),
                (user.y, facility.y),
                color=color,
                linestyle=":",
                linewidth=1,
                alpha=0.9,
            )

    ax.legend(loc=(1.01, 0))
    if dpi:
        fig.set_dpi(dpi)

    if not axis:
        ax.set_axis_off()

    if filename:
        fig.savefig(filename, bbox_inches="tight")

    plt.show()
