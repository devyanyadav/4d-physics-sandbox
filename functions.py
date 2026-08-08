import numpy as np



def project(vertices, w_dist=2.0, z_dist=3.0):#w_dist and z_dist are distance from camera
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

            
def rotate_xw(vertices,theta): 
    R = np.array([[np.cos(theta),0,0,-np.sin(theta)],
                                [0,1,0,0],
                                [0,0,1,0],
                                [np.sin(theta),0,0,np.cos(theta)]])

    rotating_vertices = vertices @ R.T
    return rotating_vertices