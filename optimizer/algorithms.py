# optimizer/algorithms.py

def optimize_with_lp(project):
    """
    A simplified greedy algorithm that attempts to fill the stock material 
    row by row with the given pieces. This simulates an LP approach.
    """
    stock_w = project.stock_width
    stock_h = project.stock_height
    pieces = project.pieces.all()  # Assumes you have a related Piece model

    x_cursor = 0
    y_cursor = 0
    max_row_height = 0

    layout = []
    for piece in pieces:
        # Assume each piece is used once; if quantity > 1, you could loop accordingly.
        w = piece.width
        h = piece.height

        # If piece doesn't fit in current row, start a new row.
        if x_cursor + w > stock_w:
            x_cursor = 0
            y_cursor += max_row_height
            max_row_height = 0

        # Check if there is enough vertical space.
        if y_cursor + h > stock_h:
            layout.append({
                "piece_id": piece.id,
                "placed": False,
                "reason": "Not enough vertical space"
            })
            continue

        # Place the piece
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

    # Calculate utilization.
    total_stock_area = stock_w * stock_h
    used_area = sum(item["width"] * item["height"] for item in layout if item.get("placed"))
    utilization = (used_area / total_stock_area) * 100.0

    return {
        "layout": layout,
        "utilization": utilization,
        "stock_width": stock_w,
        "stock_height": stock_h
    }
