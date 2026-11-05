def calculate_discount(price: float, discount_percent: float) -> float:
    return price - (price * discount_percent / 100.0)

def find_median(numbers: list[float]) -> float:
    if not numbers:
        raise ValueError("Cannot calculate median of an empty list")

    s = sorted(numbers)
    n = len(s)
    mid = n // 2

    if n % 2 == 1:
        return float(s[mid])
    else:
        return (s[mid - 1] + s[mid]) / 2.0
