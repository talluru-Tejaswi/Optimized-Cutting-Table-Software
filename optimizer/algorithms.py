from rectpack import newPacker
import random
from pulp import LpProblem, LpVariable, lpSum, LpMinimize, LpBinary


class OptimizerEngine:
    def __init__(self, project):
        self.project = project
        self.stock_w = project.stock_width
        self.stock_h = project.stock_height
        self.stock_depth = getattr(project, "stock_depth", 5.0)
        self.material = project.material_type.lower()
        self.kerf = (project.tool_config.thickness or 0.0) + self._extra_kerf()
        self.pieces_raw = list(self.project.pieces.all())

    def _extra_kerf(self):
        return {
            "wood": 0.0,
            "plastic": 0.1,
            "metal": 0.2,
        }.get(self.material, 0.0)

    def _expand_pieces(self):
        expanded = []
        for piece in self.pieces_raw:
            for _ in range(piece.quantity):
                expanded.append({
                    "id": piece.id,
                    "width": piece.width,
                    "height": piece.height
                })
        return expanded

    def _calc_util(self, layout):
        used = sum(p["width"] * p["height"] for p in layout if p.get("placed"))
        total = self.stock_w * self.stock_h
        return round(min((used / total) * 100.0, 100.0), 2)

    def optimize_lp(self):
        pieces = self._expand_pieces()
        problem = LpProblem("CuttingOptimizationLP", LpMinimize)

        layout = []
        placements = []
        w_vars, h_vars = [], []

        for i, p in enumerate(pieces):
            w = p["width"]
            h = p["height"]

            x = LpVariable(f"x_{i}", lowBound=0)
            y = LpVariable(f"y_{i}", lowBound=0)
            rot = LpVariable(f"rot_{i}", cat=LpBinary)

            w_rot = rot * h + (1 - rot) * w
            h_rot = rot * w + (1 - rot) * h

            w_vars.append(w_rot)
            h_vars.append(h_rot)
            placements.append((x, y, rot))

            problem += x + w_rot <= self.stock_w
            problem += y + h_rot <= self.stock_h

        for i in range(len(pieces)):
            for j in range(i + 1, len(pieces)):
                xi, yi, _ = placements[i]
                xj, yj, _ = placements[j]
                wi, hi = w_vars[i], h_vars[i]
                wj, hj = w_vars[j], h_vars[j]

                # Apply each non-overlap condition separately (safe with Lp)
                b1 = LpVariable(f"b1_{i}_{j}", cat=LpBinary)
                b2 = LpVariable(f"b2_{i}_{j}", cat=LpBinary)
                b3 = LpVariable(f"b3_{i}_{j}", cat=LpBinary)
                b4 = LpVariable(f"b4_{i}_{j}", cat=LpBinary)

                M = max(self.stock_w, self.stock_h) * 2

                problem += xi + wi <= xj + M * (1 - b1)
                problem += xj + wj <= xi + M * (1 - b2)
                problem += yi + hi <= yj + M * (1 - b3)
                problem += yj + hj <= yi + M * (1 - b4)

                problem += b1 + b2 + b3 + b4 >= 1

        problem += lpSum(h_vars)
        problem.solve()

        for i, p in enumerate(pieces):
            x_val = placements[i][0].varValue
            y_val = placements[i][1].varValue
            rot_val = placements[i][2].varValue

            if x_val is not None and y_val is not None:
                x = round(x_val, 2)
                y = round(y_val, 2)
                rotated = int(round(rot_val)) == 1

                w = p["width"]
                h = p["height"]
                width = w if not rotated else h
                height = h if not rotated else w

                if width > 0 and height > 0:
                    layout.append({
                        "piece_id": p["id"],
                        "placed": True,
                        "x": x,
                        "y": y,
                        "z": 0,
                        "width": width,
                        "height": height,
                        "x_mid": x + width / 2,
                        "y_mid": y + height / 2
                    })

        return {
            "layout": layout,
            "utilization": self._calc_util(layout)
        }

    def optimize_ga(self, pop_size=20, generations=10):
        base_pieces = self._expand_pieces()

        def clone_piece(p):
            return {
                "id": p.get("id", -1),
                "width": p.get("width", 0),
                "height": p.get("height", 0)
            }

        def clone_population(pop):
            return [clone_piece(p) for p in pop]

        def place(pieces):
            packer = newPacker(rotation=True)
            for p in pieces:
                w = p.get("width", 0)
                h = p.get("height", 0)
                if w > 0 and h > 0:
                    packer.add_rect(w + self.kerf, h + self.kerf, rid=p.get("id", -1))

            packer.add_bin(self.stock_w, self.stock_h)
            try:
                packer.pack()
            except AssertionError:
                return [], 0.0

            layout = []
            for rect in packer.rect_list():
                x, y, w, h, _, pid = rect
                layout.append({
                    "piece_id": pid,
                    "id": pid,
                    "placed": True,
                    "x": x,
                    "y": y,
                    "z": 0.0,
                    "width": w - self.kerf,
                    "height": h - self.kerf,
                    "x_mid": x + (w - self.kerf) / 2,
                    "y_mid": y + (h - self.kerf) / 2
                })
            return layout, self._calc_util(layout)

        population = []
        for _ in range(pop_size):
            shuffled = clone_population(base_pieces)
            random.shuffle(shuffled)
            population.append(shuffled)

        best_layout = []
        best_util = 0.0

        for _ in range(generations):
            results = [place(ind) for ind in population]
            results.sort(key=lambda x: x[1], reverse=True)

            if results[0][1] > best_util:
                best_util = results[0][1]
                best_layout = results[0][0]

            top_half = [ind for ind, _ in results[:pop_size // 2]]
            new_population = []

            for _ in range(pop_size):
                p1 = random.choice(top_half)
                p2 = random.choice(top_half)
                cut = random.randint(1, len(base_pieces) - 1)

                p1_ids = {p.get("id", -1) for p in p1[:cut]}
                child = p1[:cut]

                for p in p2:
                    if p.get("id", -1) not in p1_ids:
                        child.append(clone_piece(p))

                if len(child) >= 2 and random.random() < 0.1:
                    i, j = random.sample(range(len(child)), 2)
                    child[i], child[j] = child[j], child[i]

                new_population.append(child)

            population = new_population

        return {
            "layout": best_layout,
            "utilization": best_util
        }

    def optimize_hybrid(self):
        lp = self.optimize_lp()
        ga = self.optimize_ga()
        return lp if lp["utilization"] >= ga["utilization"] else ga
