#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Converts a triangle/tet mesh in .vtu format into another format.
It also displaces the vertex positions according to the vector field 'solution'.

You may also need to patch 'meshio' to read .vtu properly.
Apply the following patch to `python3.6/site-packages/meshio/vtu_io.py`:

```
--- vtu_io.py 2018-05-29 14:48:47.534258249 -0400
+++ vtu_io.py 2018-05-28 17:28:32.432303877 -0400
@@ -46,7 +46,7 @@
         meshio_type = vtk_to_meshio_type[tpe]
         n = num_nodes_per_cell[meshio_type]
         # The offsets point to the _end_ of the indices
-        indices = numpy.add.outer(offsets[b], numpy.arange(-n, 0))
+        indices = numpy.add.outer(offsets[b], numpy.arange(-n, 0)).astype(offsets.dtype)
         cells[meshio_type] = connectivity[indices]
         cell_data[meshio_type] = \
             {key: value[b] for key, value in cell_data_raw.items()}
```
"""

# System libs
import os
import argparse

# Third party libs
import meshio


def parse_args():
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('input', help="input vtu")
    parser.add_argument('output', nargs='?', default=None, help="output mesh")
    parser.add_argument('-N', '--no_warping', default=False,
                        action='store_true', help="do not warp points")
    parser.add_argument('-s', '--scalar', default=False,
                        action='store_true', help="scalar problem")
    parser.add_argument('-d', '--discr', default=None,
                        type=str, help="export discr mesh")
    return parser.parse_args()


def main():
    args = parse_args()
    if args.output is None:
        args.output = os.path.splitext(args.input)[0] + '.msh'
    mesh = meshio.read(args.input)
    points, cells, point_data, cell_data, field_data = mesh.points, mesh.cells, mesh.point_data, mesh.cell_data, mesh.field_data

    # Export discr mesh as is
    if args.discr is not None:
        meshio.write_points_cells(
            args.discr,
            points,
            cells,
            point_data=point_data,
            cell_data=cell_data,
            field_data=field_data,
            file_format='gmsh2-binary'
        )

    # Warp points
    if args.no_warping is False:
        if args.scalar:
            points[:, 2] = points[:, 2] + point_data['solution'].T
        else:
            points = points + point_data['solution']

    # Export result
    meshio.write_points_cells(args.output,
                              points,
                              cells,
                              point_data=point_data,
                              file_format='gmsh2-binary')


if __name__ == "__main__":
    main()
