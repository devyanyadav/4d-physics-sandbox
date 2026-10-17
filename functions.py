import numpy as np

def project(vertices, w_dist, z_dist,ESP):#w_dist and z_dist are distance from camera
    w = vertices[:, 3]
    if (w_dist-vertices[:,3] >= ESP).all() :
        xyz = vertices[:, :3] / (w_dist/(w_dist - w))[:, None] # projection math for w
        z = xyz[:, 2]
        if (z_dist-vertices[:,2] >=ESP).all():
            xy = xyz[:, :2] / (z_dist/(z_dist - z))[:, None]
            return xy
        else : 
            return None # projection math for z
    else : 
        return None


def edge_list(vertices): 
    edges= []
    for j in range(16): 
        for i in range(16): 
            if  (i,j) in edges or  (j,i) in edges : 
                continue
            diff = vertices[i] - vertices[j]
            diff_count = np.count_nonzero(diff)
            if diff_count == 1 :
                edges.append((i,j))
            

    return edges

def change_view_position(camera_position,tesseract_position): 
    tesseract_position = tesseract_position - camera_position
    camera_position = camera_position - camera_position
    return tesseract_position,camera_position

def change_view_orientation(camera_orientation,tesseract_vertices,tesseract_position): 
    tesseract_vertices = tesseract_vertices @ camera_orientation.T
    view_tesseract_position = tesseract_position @ camera_orientation.T
    return view_tesseract_position,tesseract_vertices

def half_side(vertices):
    vertices = np.asarray(vertices)
    return (vertices[:, 0].max() - vertices[:, 0].min()) / 2

def apply_walls(positions, velocities, half_sides,LO,HI):
    positions = positions.copy()
    velocities = velocities.copy()
    hits = []
    for i in range(len(positions)):
        for a in range(4):
            # lower wall: the lower face has crossed
            if positions[i][a] - half_sides[i] < LO:
                positions[i][a] = LO + half_sides[i]
                velocities[i][a] = abs(velocities[i][a])
                hits.append((i,a,-1))
            # upper wall: the upper face has crossed
            if positions[i][a] + half_sides[i] > HI:
                positions[i][a] = HI - half_sides[i]
                velocities[i][a] = -abs(velocities[i][a])
                hits.append((i,a,1))
    return positions, velocities,hits

def can_resize(positions, half_sides, new_lo, new_hi, tolerance=1e-9):
    lowest_face = (positions - half_sides[:, None]).min()
    highest_face = (positions + half_sides[:, None]).max()
    return bool(lowest_face >= new_lo - tolerance and highest_face <= new_hi + tolerance)

