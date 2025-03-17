import random
from copy import deepcopy

def safe_randrange(start, stop):
    """
    Returns a random integer in the range [start, stop).
    If stop <= start, returns start.
    """
    if stop <= start:
        return start
    try:
        return random.randrange(start, stop)
    except ValueError:
        return start

def optimize_with_lp(project):
    """
    A basic greedy row-fill algorithm that handles each piece and its quantity.
    (Replace this with your actual LP-based optimization logic.)
    """
    stock_w = project.stock_width
    stock_h = project.stock_height
    pieces = project.pieces.all()

    layout = []
    x_cursor = 0
    y_cursor = 0
    max_row_height = 0

    for piece in pieces:
        for _ in range(piece.quantity):
            w = piece.width
            h = piece.height
            # If the piece doesn't fit in the current row, move to the next row
            if x_cursor + w > stock_w:
                x_cursor = 0
                y_cursor += max_row_height
                max_row_height = 0
            # If the piece cannot be placed vertically, mark it as unplaced
            if y_cursor + h > stock_h:
                layout.append({"piece_id": piece.id, "placed": False})
                continue
            layout.append({
                "piece_id": piece.id,
                "placed": True,
                "x": x_cursor,
                "y": y_cursor,
                "width": w,
                "height": h
            })
            x_cursor += w
            if h > max_row_height:
                max_row_height = h

    total_area = stock_w * stock_h
    used_area = sum(item["width"] * item["height"] for item in layout if item.get("placed"))
    utilization = (used_area / total_area) * 100.0
    return {"layout": layout, "utilization": utilization}

def optimize_with_ga(project):
    """
    A dummy Genetic Algorithm (GA) implementation that shuffles pieces.
    In production, replace with proper crossover and mutation logic.
    """
    stock_w = project.stock_width
    stock_h = project.stock_height
    items = []
    for piece in project.pieces.all():
        for _ in range(piece.quantity):
            items.append({
                "piece_id": piece.id,
                "width": piece.width,
                "height": piece.height
            })

    # If there are fewer than 2 items, fallback to LP optimization.
    if len(items) < 2:
        return optimize_with_lp(project)

    def place_items(order):
        x_cursor = 0
        y_cursor = 0
        max_row_height = 0
        layout = []
        for item in order:
            w = item["width"]
            h = item["height"]
            if x_cursor + w > stock_w:
                x_cursor = 0
                y_cursor += max_row_height
                max_row_height = 0
            if y_cursor + h > stock_h:
                layout.append({"piece_id": item["piece_id"], "placed": False})
            else:
                layout.append({
                    "piece_id": item["piece_id"],
                    "placed": True,
                    "x": x_cursor,
                    "y": y_cursor,
                    "width": w,
                    "height": h
                })
                x_cursor += w
                if h > max_row_height:
                    max_row_height = h
        used_area = sum(l["width"] * l["height"] for l in layout if l.get("placed"))
        util = (used_area / (stock_w * stock_h)) * 100.0
        return layout, util

    population_size = 20
    generations = 15
    population = []
    for _ in range(population_size):
        order = deepcopy(items)
        random.shuffle(order)
        population.append(order)

    best_layout = []
    best_util = 0.0
    for _ in range(generations):
        results = []
        for individual in population:
            layout, util = place_items(individual)
            results.append((individual, layout, util))
        results.sort(key=lambda x: x[2], reverse=True)
        if results[0][2] > best_util:
            best_util = results[0][2]
            best_layout = results[0][1]
        # Selection: choose the top half of the population
        top_half = [r[0] for r in results[:population_size // 2]]
        new_population = []
        while len(new_population) < population_size:
            parent1 = random.choice(top_half)
            parent2 = random.choice(top_half)
            # Ensure there are enough items to choose a cut point.
            if len(items) > 1:
                cut = random.randint(1, len(items) - 1)
            else:
                cut = 1
            child = parent1[:cut] + [item for item in parent2 if item not in parent1[:cut]]
            # Mutation: swap two elements with a 10% chance
            if len(child) >= 2 and random.random() < 0.1:
                i, j = random.sample(range(len(child)), 2)
                child[i], child[j] = child[j], child[i]
            new_population.append(child)
        population = new_population

    return {"layout": best_layout, "utilization": best_util}

def optimize_with_hybrid(project):
    """
    A simple hybrid approach that chooses the best result from LP and GA.
    """
    lp_result = optimize_with_lp(project)
    ga_result = optimize_with_ga(project)
    if lp_result["utilization"] >= ga_result["utilization"]:
        return lp_result
    return ga_result

def optimize_project(project):
    """
    Dispatcher to call the appropriate optimization method based on project.algorithm.
    """
    method = project.algorithm.lower()
    if method == 'lp':
        return optimize_with_lp(project)
    elif method == 'ga':
        return optimize_with_ga(project)
    elif method == 'hybrid':
        return optimize_with_hybrid(project)
    else:
        raise ValueError("Unknown optimization method: " + method)

def parse_default_pieces(piece_str):
    """
    Converts a string like '50x30:2, 40x10:3' into a list of dictionaries.
    This is useful if your FurnitureTemplate.default_pieces is stored as plain text.
    """
    pieces = []
    for part in piece_str.split(","):
        part = part.strip()
        if not part:
            continue
        try:
            dims, qty = part.split(":")
            w, h = dims.split("x")
            pieces.append({
                "width": float(w),
                "height": float(h),
                "quantity": int(qty)
            })
        except Exception as e:
            # Optionally log the error or raise a validation error.
            continue
    return pieces
