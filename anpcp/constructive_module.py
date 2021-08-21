
from anpcp.models.instance import Instance
from typing import List


def generate_instances(amount: int, n: int, p: int, alpha: int) -> List[Instance]:
    return [
        Instance.random(n, p, alpha, 1000, 1000)
        for _ in range(amount)
    ]
