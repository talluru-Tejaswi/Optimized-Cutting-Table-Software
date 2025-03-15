import json
import random
from copy import deepcopy

def optimize_with_lp(project):
    """
    A basic greedy row-fill algorithm that handles each piece and its quantity.
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
            if x_cursor + w > stock_w:
                x_cursor = 0
                y_cursor += max_row_height
                max_row_height = 0
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
    used_area = sum(item["width"] * item["height"] for item in layout if item["placed"])
    utilization = (used_area / total_area) * 100.0
    return {"layout": layout, "utilization": utilization}

def optimize_with_ga(project):
    """
    A dummy Genetic Algorithm (GA) implementation that shuffles the pieces.
    In production, implement proper crossover and mutation.
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
                layout.append({"piece_id": item["piece_id"], "placed": True, "x": x_cursor, "y": y_cursor, "width": w, "height": h})
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
        # Selection: top half
        top_half = [r[0] for r in results[:population_size//2]]
        new_population = []
        while len(new_population) < population_size:
            parent1 = random.choice(top_half)
            parent2 = random.choice(top_half)
            cut = random.randint(1, len(items) - 1)
            child = parent1[:cut] + [item for item in parent2 if item not in parent1[:cut]]
            # Mutation: swap two elements with a chance
            if random.random() < 0.1:
                i, j = random.sample(range(len(child)), 2)
                child[i], child[j] = child[j], child[i]
            new_population.append(child)
        population = new_population

    return {"layout": best_layout, "utilization": best_util}
