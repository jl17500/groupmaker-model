"""Model 1: the fitted cluster model. No imports, no packages.

Centroids come from fit_clusters.py (k-means, k=3, unscaled).
Column order: skill_programming, skill_data_stats, skill_frontend_design, skill_business_pitch.
"""

CENTROIDS = [
    [1.7857, 2.5000, 2.4286, 4.2857],
    [3.4167, 3.1667, 2.1667, 2.4167],
    [3.8750, 4.0000, 4.2500, 4.6250],
]


def predict_cluster(skills):
    """skills: four 1-5 ratings in the order above. Returns the nearest centroid's number."""
    best, best_dist = 0, None
    for i, c in enumerate(CENTROIDS):
        dist = sum((float(s) - v) ** 2 for s, v in zip(skills, c))
        if best_dist is None or dist < best_dist:
            best, best_dist = i, dist
    return best
