def get_date_range(start, end):
    result = f"{end.day}. {end.month}. {end.year}"

    if start == end:
        return result

    result = "- " + result
    if start.year != end.year:
        result = f"{start.year}. " + result
        result = f"{start.month}. " + result
        return f"{start.day}. " + result

    if start.month != end.month:
        result = f"{start.month}. " + result
        return f"{start.day}. " + result

    return f"{start.day}. " + result
