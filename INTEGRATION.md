# INTEGRATION.md: adding the group model to the app

For the agent working inside the app repo (`pipf26-pd-lab2`: Flask + psycopg2 + Postgres). You have not seen the model repo, and you don't need it.

**Rules: do not edit `model/cluster_model.py` or `model/assignment_rules.py`; change the app to fit them. Backend only, so no changes to `templates/`. Add no packages: no scikit-learn, no pandas.**

## 1. What these two files do
`cluster_model.py` holds 3 k-means centroids as plain numbers and gives a student a skill "kind" (cluster 0, 1 or 2) from their four 1–5 ratings. `assignment_rules.py` takes the whole class, gets each student's kind, orders the kinds from largest to smallest, and deals the students round-robin into 8 groups so every group gets a mix. Neither file imports any package.

## 2. Files to copy
```
model/
  cluster_model.py
  assignment_rules.py
  INTEGRATION.md
```
`assignment_rules.py` does `from cluster_model import predict_cluster`, which fails with `ModuleNotFoundError` when it's imported from the app root. Fix it in `app.py` without editing the model files:
```python
import sys
sys.path.insert(0, str(ROOT / "model"))
from assignment_rules import assign_groups
import cluster_model
```

## 3. The two functions
- `predict_cluster(skills)` takes a list of 4 numbers in this order: programming, data_stats, frontend_design, business_pitch. It returns an int.
  Example: `predict_cluster([4, 4, 4, 5])` returns `2`.
- `assign_groups(students, n_groups=8)` takes a list of dicts with keys `id`, `skill_programming`, `skill_data_stats`, `skill_frontend_design`, `skill_business_pitch`. It returns a list of `{"id", "cluster", "group"}`, where groups are numbered 1–8.
  Example: `assign_groups([{"id": "ab123", "skill_programming": 4, "skill_data_stats": 4, "skill_frontend_design": 4, "skill_business_pitch": 5}])` returns `[{"id": "ab123", "cluster": 2, "group": 1}]`.

## 4. Where the data comes from
The models were built from `data/class_dataset.csv`. The app reads Postgres; `load_class_dataset.py` loads that same CSV into the tables defined in `schema.sql`.

| model input | CSV column | Postgres |
|---|---|---|
| `id` | `netid` | `students.netid` (VARCHAR, unique). **Not** `student_id`, which is a SERIAL surrogate key the CSV doesn't have |
| skill ratings | `skill_programming`, `skill_data_stats`, `skill_frontend_design`, `skill_business_pitch` | `students` columns with the same names, stored as INTEGER 1–5 |
| name (output only) | `name` | `students.name` |

Differences from the CSV: the column names are identical, but the values arrive from psycopg2 as Python ints rather than strings. Pass them as they are, since `predict_cluster` casts them to float. Everything needed is in `students`; no joins are required.

Query:
```sql
SELECT netid, name, skill_programming, skill_data_stats,
       skill_frontend_design, skill_business_pitch
FROM students ORDER BY netid;
```
Use the existing `get_connection()`.

## 5. Backend: add `GET /api/groups`
Read every student with the query above, build the input dicts (`id` = netid), call `assign_groups(students)`, and return JSON with `jsonify`:
```json
{
  "n_groups": 8,
  "groups": [{"group": 1, "members": ["Name A", "Name B"], "cluster_counts": {"0": 2, "1": 2, "2": 1}}],
  "clusters": [{"cluster": 0, "students": 14, "centroid": [1.79, 2.50, 2.43, 4.29]}],
  "groups_missing_a_cluster": 0
}
```
- `members`: names, looked up by netid.
- `centroid`: from `cluster_model.CENTROIDS`, rounded to 2 decimals.
- `groups_missing_a_cluster`: the number of groups with 0 students from at least one cluster.
- **Never return any one person's cluster** (no name-to-cluster pairs).
Leave the existing `/` route unchanged.

## 6. Frontend
Nothing yet. A later page can show `groups` as 8 cards (member names and a small bar of `cluster_counts`) and use `clusters` as a legend. Suggested cluster names: 0 = Pitchers, 1 = Coders, 2 = All-rounders.

## 7. Packaging
The `Dockerfile` copies only `app.py` and `templates/`. Add this after `COPY templates/ templates/`:
```
COPY model/ model/
```
`.dockerignore` excludes `*.md` and `data/`. That's fine, because the endpoint reads Postgres, not the CSV, and the image doesn't need `INTEGRATION.md`. `requirements.txt` needs no changes.

## 8. Test
```
python app.py
curl http://localhost:5000/api/groups
```
Expected result (from the model repo's run, 34 students, k = 3):
- 8 groups, with sizes 5, 5, 4, 4, 4, 4, 4, 4
- clusters with 14, 12 and 8 students
- `"groups_missing_a_cluster": 0`
