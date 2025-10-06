from math import sqrt

def euclidean_distance(p1, p2):
    return sqrt((p1.x - p2.x) ** 2 + (p1.y - p2.y) ** 2)


def synchronous_euclidean_distance(p1, p2, p):
    # Linear interpolation of expected position of p between p1 and p2
    if p2.t == p1.t:
        return euclidean_distance(p, p1)
    ratio = (p.t - p1.t) / (p2.t - p1.t)
    x_interp = p1.x + ratio * (p2.x - p1.x)
    y_interp = p1.y + ratio * (p2.y - p1.y)
    return sqrt((p.x - x_interp) ** 2 + (p.y - y_interp) ** 2)


def update_sed(buffer, i):
    if 0 < i < len(buffer) - 1:
        buffer[i].sed = synchronous_euclidean_distance(buffer[i-1], buffer[i+1], buffer[i])
    else:
        buffer[i].sed = float('inf')
