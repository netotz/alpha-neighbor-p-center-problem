from dataclasses import dataclass
from typing import List, Optional

import numpy as np
from scipy import spatial

from .point import Point

@dataclass()
class Instance:
    alpha: int
    p: int
    points: List[Point]
    distances: Optional[np.ndarray] = None
    
    
    def calculate_distances(self) -> None:
        self.distances = spatial.distance_matrix(
            [[p.x, p.y] for p in self.points],
            [[p.x, p.y] for p in self.points],
        )
