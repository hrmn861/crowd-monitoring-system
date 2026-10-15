"""
Unit Tests for Zone Point-In-Polygon and Density Computations
"""

import pytest

def point_in_polygon(x: float, y: float, polygon: list) -> bool:
    """Ray-casting algorithm for point-in-polygon evaluation."""
    n = len(polygon)
    inside = False
    p1x, p1y = polygon[0]
    for i in range(n + 1):
        p2x, p2y = polygon[i % n]
        if y > min(p1y, p2y):
            if y <= max(p1y, p2y):
                if x <= max(p1x, p2x):
                    if p1y != p2y:
                        xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                    if p1x == p2x or x <= xinters:
                        inside = not inside
        p1x, p1y = p2x, p2y
    return inside

def compute_density(count: float, area_m2: float) -> float:
    if area_m2 <= 0:
        raise ValueError("Physical floor area must be greater than zero")
    return round(count / area_m2, 2)

def test_point_in_polygon():
    square_poly = [[0, 0], [100, 0], [100, 100], [0, 100]]
    # Inside center
    assert point_in_polygon(50, 50, square_poly) is True
    # Outside
    assert point_in_polygon(150, 50, square_poly) is False
    assert point_in_polygon(-10, 50, square_poly) is False

def test_compute_density():
    # 50 people in 25 m2 = 2.0 people/m2
    assert compute_density(50, 25.0) == 2.0
    # Zero count
    assert compute_density(0, 30.0) == 0.0

def test_compute_density_invalid_area():
    with pytest.raises(ValueError):
        compute_density(10, 0.0)
