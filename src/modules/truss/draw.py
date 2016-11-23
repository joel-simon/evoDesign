
def draw_truss(viewer, truss, scale=1):
    nodes = [(j.coordinates+j.deflections)*scale for j in truss.joints]
    edges = [(truss.joint_index(m.joint_a), truss.joint_index(m.joint_b)) \
                                                for m in truss.members]
    colors = [(1 - min(1, m.fos), 0, 0) for m in truss.members]
    widths = [m.r*50 for m in truss.members]

    viewer.start_draw()
    viewer.draw_mesh(nodes, edges, colors,widths)

    for joint, node in zip(truss.joints, nodes):
        if joint.is_static():
            viewer.draw_sphere(node, (0,0,1), r=.1)

        if abs(min(joint.loads)) + max(joint.loads) > 0:
            viewer.draw_arrow(node, joint.loads, c=(1, 0, 0))

    viewer.end_draw()
