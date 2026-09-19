import numpy as np



def project(vertices, w_dist, z_dist):#w_dist and z_dist are distance from camera
    w = vertices[:, 3]
    xyz = vertices[:, :3] / (w_dist - w)[:, None] # projection math for w

    z = xyz[:, 2]
    xy = xyz[:, :2] / (z_dist - z)[:, None] # projection math for z

    return xy


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