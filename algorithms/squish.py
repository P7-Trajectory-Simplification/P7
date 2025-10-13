# from algorithms.great_circle_math import point_to_great_circle, great_circle_distance
# from vessel_log import VesselLog


# def calc_sed(a: VesselLog, target: VesselLog, b: VesselLog) -> float:
#     a_tuple = a.get_coords()
#     b_tuple = b.get_coords()
#     target_tuple = target.get_coords()

#     return point_to_great_circle(a_tuple, b_tuple, target_tuple)


# def find_min_sed(buff: list[(VesselLog, float)]) -> int:
#     index = 1
#     for i in range(2,len(buff)-1):
#         if buff[i][1] < buff[index][1]:
#             index = i
#     return index


# def squish(points: list[VesselLog], buff: list, buff_size: int = 1000):
#     print(len(points))
#     for i in range(0, len(points)):
#         buff.append([points[i], float('inf')])
#         length = len(buff)
#         if length >= 3:
#             buff[length - 2][1] = calc_sed(buff[length-3][0], buff[length-2][0], buff[length-1][0])
#         if length == buff_size:
#             index = find_min_sed(buff)
#             del buff[index]
#             length = len(buff)
#             if 1 < index:
#                 buff[index-1][1] = calc_sed(buff[index - 2][0], buff[index - 1][0], buff[index][0])
#             if index < length - 1:
#                 buff[index][1] = calc_sed(buff[index - 1][0], buff[index][0], buff[index + 1][0])


from algorithms.great_circle_math import point_to_great_circle, great_circle_distance
from vessel_log import VesselLog


def calc_sed(a: VesselLog, target: VesselLog, b: VesselLog) -> float:
    a_tuple = a.get_coords()
    b_tuple = b.get_coords()
    target_tuple = target.get_coords()

    return point_to_great_circle(a_tuple, b_tuple, target_tuple)


def find_min_sed(buff: list[(VesselLog, float)]) -> int:
    index = 1
    for i in range(2,len(buff)-1):
        if buff[i][1] < buff[index][1]:
            index = i
    return index


def squish(points: list[VesselLog], buff: list, buff_size: int = 1000):
    print(len(points))
    for i in range(0, len(points)):
        buff.append([points[i], float('inf')])
        length = len(buff)
        if length >= 3:
            buff[length - 2][1] = calc_sed(buff[length-3][0], buff[length-2][0], buff[length-1][0])
        if length == buff_size:
            index = find_min_sed(buff)
            del buff[index]
            length = len(buff)
            if 1 < index:
                buff[index-1][1] = calc_sed(buff[index - 2][0], buff[index - 1][0], buff[index][0])
            if index < length - 1:
                buff[index][1] = calc_sed(buff[index - 1][0], buff[index][0], buff[index + 1][0])




