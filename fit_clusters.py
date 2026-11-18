"""Fit k-means on the four skill ratings.

  python fit_clusters.py          -> Stage 1: inertia for k=1..6 and elbow.png
  python fit_clusters.py --k 3    -> Stages 2-3: centroids, counts, cluster column,
                                     writes cluster_model.py and checks it matches
"""
import argparse

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.cluster import KMeans

SKILLS = ["skill_programming", "skill_data_stats", "skill_frontend_design", "skill_business_pitch"]


def elbow(X):
    print(f"Students: {len(X)}")
    ks, inertias = list(range(1, 7)), []
    for k in ks:
        km = KMeans(n_clusters=k, n_init=10, random_state=0).fit(X)
        inertias.append(km.inertia_)
        print(f"k={k}  inertia={km.inertia_:.1f}")
    plt.plot(ks, inertias, marker="o")
    plt.xlabel("k (number of clusters)")
    plt.ylabel("inertia")
    plt.title("Elbow plot")
    plt.savefig("elbow.png", dpi=120, bbox_inches="tight")
    print("Saved elbow.png")


def write_model_file(centroids):
    rows = ",\n".join("    [" + ", ".join(f"{v:.4f}" for v in c) + "]" for c in centroids)
    code = f'''"""Model 1: the fitted cluster model. No imports, no packages.

Centroids come from fit_clusters.py (k-means, k={len(centroids)}, unscaled).
Column order: {", ".join(SKILLS)}.
"""

CENTROIDS = [
{rows},
]


def predict_cluster(skills):
    """skills: four 1-5 ratings in the order above. Returns the nearest centroid's number."""
    best, best_dist = 0, None
    for i, c in enumerate(CENTROIDS):
        dist = sum((float(s) - v) ** 2 for s, v in zip(skills, c))
        if best_dist is None or dist < best_dist:
            best, best_dist = i, dist
    return best
'''
    with open("cluster_model.py", "w", encoding="utf-8") as f:
        f.write(code)
    print("Wrote cluster_model.py")


def fit(df, k):
    X = df[SKILLS]
    km = KMeans(n_clusters=k, n_init=10, random_state=0).fit(X)
    df["cluster"] = km.labels_
    print(f"Students: {len(df)}, k={k}\n")
    print("cluster  " + "  ".join(s.replace("skill_", "") for s in SKILLS) + "  students")
    for i, c in enumerate(km.cluster_centers_):
        n = int((df["cluster"] == i).sum())
        print(f"{i:>7}  " + "  ".join(f"{v:.2f}" for v in c) + f"  {n}")
    df.to_csv("class_dataset_with_clusters.csv", index=False)

    write_model_file(km.cluster_centers_)
    import importlib, cluster_model
    importlib.reload(cluster_model)
    match = sum(cluster_model.predict_cluster(r) == lab for r, lab in zip(X.values.tolist(), km.labels_))
    print(f"\npredict_cluster matches k-means for {match} of {len(df)} students")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--k", type=int)
    a = p.parse_args()
    data = pd.read_csv("class_dataset.csv")
    fit(data, a.k) if a.k else elbow(data[SKILLS])
