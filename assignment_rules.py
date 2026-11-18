"""Model 2: deal students into groups so each group gets a mix of skill kinds.

Biggest cluster first, sorted by id inside a cluster, dealt round-robin to
groups 1..n_groups without restarting the count between clusters.
"""
from cluster_model import predict_cluster

SKILLS = ["skill_programming", "skill_data_stats", "skill_frontend_design", "skill_business_pitch"]


def assign_groups(students, n_groups=8):
    """students: list of dicts with "id" and the four skill keys.
    Returns a list of {"id", "cluster", "group"}."""
    by_cluster = {}
    for s in students:
        c = predict_cluster([s[k] for k in SKILLS])
        by_cluster.setdefault(c, []).append(s)

    order = sorted(by_cluster, key=lambda c: (-len(by_cluster[c]), c))
    result, i = [], 0
    for c in order:
        for s in sorted(by_cluster[c], key=lambda s: str(s["id"])):
            result.append({"id": s["id"], "cluster": c, "group": i % n_groups + 1})
            i += 1
    return result


if __name__ == "__main__":
    import csv

    with open("class_dataset.csv", newline="", encoding="utf-8") as f:
        students = [{"id": r["netid"], **{k: float(r[k]) for k in SKILLS}} for r in csv.DictReader(f)]

    out = assign_groups(students)
    clusters = sorted({r["cluster"] for r in out})
    missing = 0
    print("group  size  " + "  ".join(f"c{c}" for c in clusters))
    for g in range(1, 9):
        rows = [r for r in out if r["group"] == g]
        counts = [sum(r["cluster"] == c for r in rows) for c in clusters]
        missing += 0 in counts
        print(f"{g:>5}  {len(rows):>4}  " + "  ".join(f"{n:>2}" for n in counts))
    print(f"\nGroups missing a cluster: {missing}")
