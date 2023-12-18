RESOLUTION_DPI = 300
ANTIALIASING = 3


def mm_to_px(*args):
    x = args
    if len(args) == 1:
        x = args[0]
    if isinstance(x, int) or isinstance(x, float):
        return int(RESOLUTION_DPI * ANTIALIASING * 0.03937 * x)

    return type(x)([mm_to_px(i) for i in x])


def text_into_lines(draw, font, text, max_width):
    tokens = text.split(" ")
    sizes = [draw.textbbox((0, 0), token, font) for token in tokens]
    lines = [[]]
    width = 0
    space_width = draw.textbbox((0, 0), " ", font)[2]
    for token, size in zip(tokens, sizes):
        if width + size[2] > max_width:
            lines.append([])
            width = 0
        lines[-1].append(token)
        width += size[2] + space_width
    lines = [" ".join(line) for line in lines]
    return "\n".join(lines)
