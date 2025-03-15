# optimizer/algorithms.py

import random

def optimize_with_lp(project):
    """
    Simplified example of a 2D cutting approach using an LP-like strategy.
    For demonstration only—this won't handle all edge cases or large inputs.
    """
    # 1) Collect project data
    stock_w = project.stock_width
    stock_h = project.stock_height
    pieces = project.pieces.all()  # Query the related Piece objects

    # 2) For simplicity, do a naive "row fill" approach (pretending it's LP).
    #    We'll place each piece in the next available (x, y) without overlap.
    #    A real LP would define variables & constraints using pulp or ortools.

    x_cursor = 0
    y_cursor = 0
    max_row_height = 0

    layout = []
    for piece in pieces:
        w = piece.width
        h = piece.height
        # If piece won't fit in the current row, move to next row
        if x_cursor + w > stock_w:
            x_cursor = 0
            y_cursor += max_row_height
            max_row_height = 0

        # Check if we still fit vertically
        if y_cursor + h > stock_h:
            # Not enough space; in a real scenario, we might set piece as "not placed"
            layout.append({
                "piece_id": piece.id,
                "placed": False
            })
            continue

        # Place piece at (x_cursor, y_cursor)
        layout.append({
            "piece_id": piece.id,
            "placed": True,
            "x": x_cursor,
            "y": y_cursor,
            "width": w,
            "height": h
        })

        # Update cursors
        x_cursor += w
        if h > max_row_height:
            max_row_height = h

    # 3) Calculate some simple stats
    total_area = stock_w * stock_h
    used_area = 0
    for item in layout:
        if item["placed"]:
            used_area += item["width"] * item["height"]
    utilization = used_area / total_area * 100.0

    # Return result as a dict
    return {
        "layout": layout,
        "utilization": utilization,
        "stock_width": stock_w,
        "stock_height": stock_h
    }

def optimize_with_ga(project):
    """
    Simplified Genetic Algorithm example. We'll just randomize an ordering of pieces
    and place them greedily to see if we can reduce 'waste' by trying multiple permutations.
    """

    stock_w = project.stock_width
    stock_h = project.stock_height
    pieces = list(project.pieces.all())

    best_layout = None
    best_util = 0.0

    # Genetic parameters
    population_size = 20
    generations = 30

    # Helper: place pieces in a given order (greedy row fill) and return (layout, util)
    def place_pieces_in_order(pieces_order):
        x_cursor = 0
        y_cursor = 0
        max_row_h = 0
        layout = []
        total_area = stock_w * stock_h
        used_area = 0

        for p in pieces_order:
            w = p.width
            h = p.height
            if x_cursor + w > stock_w:
                x_cursor = 0
                y_cursor += max_row_h
                max_row_h = 0

            if y_cursor + h > stock_h:
                # Can't place, skip
                layout.append({"piece_id": p.id, "placed": False})
                continue

            layout.append({
                "piece_id": p.id,
                "placed": True,
                "x": x_cursor,
                "y": y_cursor,
                "width": w,
                "height": h
            })
            used_area += w * h
            x_cursor += w
            if h > max_row_h:
                max_row_h = h

        utilization = used_area / total_area * 100.0
        return layout, utilization

    # Initialize population with random permutations
    population = []
    for _ in range(population_size):
        perm = pieces[:]
        random.shuffle(perm)
        population.append(perm)

    for gen in range(generations):
        # Evaluate fitness
        fitnesses = []
        for individual in population:
            _, util = place_pieces_in_order(individual)
            fitnesses.append(util)

        # Track best
        gen_best_util = max(fitnesses)
        if gen_best_util > best_util:
            idx = fitnesses.index(gen_best_util)
            best_individual = population[idx]
            best_layout, best_util = place_pieces_in_order(best_individual)

        # Selection: pick top half
        ranked = sorted(zip(population, fitnesses), key=lambda x: x[1], reverse=True)
        top_half = [x[0] for x in ranked[: population_size // 2]]

        # Crossover & mutation to form new population
        new_population = []
        while len(new_population) < population_size:
            parent1 = random.choice(top_half)
            parent2 = random.choice(top_half)
            # Crossover (simple one-cut)
            cut = random.randint(1, len(pieces) - 1)
            child = parent1[:cut] + [p for p in parent2 if p not in parent1[:cut]]

            # Mutation (swap two random pieces)
            if random.random() < 0.1:
                i, j = random.sample(range(len(child)), 2)
                child[i], child[j] = child[j], child[i]

            new_population.append(child)

        population = new_population

    # Return best found
    return {
        "layout": best_layout,
        "utilization": best_util,
        "stock_width": stock_w,
        "stock_height": stock_h
    }
