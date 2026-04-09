from fastapi import HTTPException


def validate_basic(min_qty: int, max_qty: int | None, price: float):
    if min_qty < 1:
        raise HTTPException(400, "min_qty must be >= 1")

    if max_qty is not None and max_qty < min_qty:
        raise HTTPException(400, "max_qty must be >= min_qty")

    if price < 0:
        raise HTTPException(400, "price must be >= 0")


def is_overlap(e_min, e_max, n_min, n_max):
    e_max = e_max if e_max is not None else float("inf")
    n_max = n_max if n_max is not None else float("inf")

    return not (n_max < e_min or n_min > e_max)


async def validate_no_overlap(rows, min_qty, max_qty):
    for r in rows:
        if is_overlap(r["min_qty"], r["max_qty"], min_qty, max_qty):
            raise HTTPException(
                400,
                f"Overlapping with existing range {r['min_qty']} - {r['max_qty']}"
            )