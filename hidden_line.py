from PIL import Image, ImageDraw
import numpy as np


def rotateX(R, s):
    rad = np.deg2rad(s)
    Rx = np.array(
        [[1, 0, 0], [0, np.cos(rad), -np.sin(rad)], [0, np.sin(rad), np.cos(rad)]]
    )
    return R @ Rx


def rotateY(R, s):
    rad = np.deg2rad(s)
    Ry = np.array(
        [[np.cos(rad), 0, np.sin(rad)], [0, 1, 0], [-np.sin(rad), 0, np.cos(rad)]]
    )
    return R @ Ry


def rotateZ(R, s):
    rad = np.deg2rad(s)
    Rz = np.array(
        [[np.cos(rad), -np.sin(rad), 0], [np.sin(rad), np.cos(rad), 0], [0, 0, 1]]
    )
    return R @ Rz


def project(v, R, scale=1.0, sy=0.0, sz=0.0):
    v = np.asarray(v, dtype=float)
    Vr = R @ v
    y, z = Vr[1], Vr[2]
    return (scale * y + sy, scale * z + sz)


def get_visible(R):
    is_face_front = [True] * 6
    is_face_front[0] = bool((R @ [1, 0, 0])[0] < 0)
    is_face_front[3] = not is_face_front[0]
    is_face_front[1] = bool((R @ [0, 1, 0])[0] < 0)
    is_face_front[4] = not is_face_front[1]
    is_face_front[2] = bool((R @ [0, 0, 1])[0] < 0)
    is_face_front[5] = not is_face_front[2]

    is_edge_visible = [True] * 12

    is_edge_visible[0] = is_face_front[1] or is_face_front[2]
    is_edge_visible[1] = is_face_front[2] or is_face_front[4]
    is_edge_visible[2] = is_face_front[1] or is_face_front[5]
    is_edge_visible[3] = is_face_front[4] or is_face_front[5]
    is_edge_visible[4] = is_face_front[0] or is_face_front[2]
    is_edge_visible[5] = is_face_front[2] or is_face_front[3]
    is_edge_visible[6] = is_face_front[0] or is_face_front[5]
    is_edge_visible[7] = is_face_front[3] or is_face_front[5]
    is_edge_visible[8] = is_face_front[0] or is_face_front[1]
    is_edge_visible[9] = is_face_front[1] or is_face_front[3]
    is_edge_visible[10] = is_face_front[0] or is_face_front[4]
    is_edge_visible[11] = is_face_front[3] or is_face_front[4]

    return is_edge_visible


def draw_edges(draw, points, edges, R, sy, sz, draw_front):
    scale = 150

    is_edge_visible = get_visible(R)

    def project(v):
        v = np.asarray(v, dtype=float)
        Vr = R @ v
        y, z = Vr[1], Vr[2]
        return (scale * y + sy, scale * z + sz)

    for i, e in enumerate(edges):
        if is_edge_visible[i] ^ draw_front:
            continue
        p1 = project(points[e[0]])
        p2 = project(points[e[1]])
        draw.line([p1, p2], fill="black", width=2)


def draw_front_edges(draw, points, edges, R, sy, sz):
    draw_edges(draw, points, edges, R, sy, sz, True)


def draw_back_edges(draw, points, edges, R, sy, sz):
    draw_edges(draw, points, edges, R, sy, sz, False)


def draw(R, width, height, points, edges):
    img = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(img)
    draw_back_edges(draw, points, edges, R, width // 2, height // 2)
    cx, cy = width / 2, height / 2
    r = 150
    bbox = (cx - r, cy - r, cx + r, cy + r)
    draw.ellipse(bbox, fill="red", width=3)
    draw_front_edges(draw, points, edges, R, width // 2, height // 2)
    return img


def main():
    points = [
        (-1, -1, -1),
        (1, -1, -1),
        (-1, 1, -1),
        (1, 1, -1),
        (-1, -1, 1),
        (1, -1, 1),
        (-1, 1, 1),
        (1, 1, 1),
    ]

    edges = [
        (0, 1),
        (2, 3),
        (4, 5),
        (6, 7),
        (0, 2),
        (1, 3),
        (4, 6),
        (5, 7),
        (0, 4),
        (1, 5),
        (2, 6),
        (3, 7),
    ]

    R = np.eye(3)
    R = rotateY(R, 80)
    R = rotateX(R, 30)
    width = 512
    height = 512
    images = []
    for i in range(30):
        img = draw(R, width, height, points, edges)
        images.append(img)
        R = rotateX(R, 3)
    for i in range(30):
        img = draw(R, width, height, points, edges)
        images.append(img)
        R = rotateY(R, 3)
    for i in range(len(images)):
        filename = f"image.{i:03d}.png"
        images[i].save(filename)
        print(filename)


if __name__ == "__main__":
    main()
