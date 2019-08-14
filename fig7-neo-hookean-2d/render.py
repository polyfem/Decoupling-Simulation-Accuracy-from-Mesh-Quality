#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Generates rendering job file + batch script to render them.

find . -name "*.vtu" -exec ~/work/polyfem/python/misc/vtu_to_msh.py \{\} \;

for f in *.json;
    pyrenderer --renderer mitsuba -S $f --front-direction=Z --up-direction=Y --head-on;
end
"""

import os
import glob
import numpy
import meshio

config = """\
{{
    "views": [
        {{
            "type": "composite",
            "views": [
                {{
                    "type": "scalar",
                    "scalar": "scalar_value",
                    "color_map": "viridis",
                    "normalize": false,
                    "bounds": {scalar_range},
                    "view": {{
                        "type": "mesh_only",
                        "bbox": [{min_corner}, {max_corner}],
                        "mesh": "{msh_path}",
                        "wire_frame": false
                    }}
                }},
                {{
                    "type": "wire_network",
                    "wire_network": "{wire_path}",
                    "bbox": [{min_corner}, {max_corner}],
                    "color": "black",
                    "radius": 0.002
                }}
            ],
            "width": 1600,
            "height": 1600,
            "transparent_bg": true,
            "background": "n",
            "name": "{output_path}"
        }}
    ]
}}
"""


def write_job(msh_path, render_dir, bbox, minmax):
    basename = os.path.splitext(msh_path)[0]
    msh_path = os.path.relpath(msh_path, render_dir)
    wire_path = os.path.relpath(basename + '.obj', render_dir)
    basename = os.path.basename(basename)
    output_path = basename + '.png'
    json_path = os.path.join(render_dir, basename + '.json')
    with open(json_path, 'w') as f:
        f.write(config.format(
            msh_path=msh_path,
            wire_path=wire_path,
            output_path=output_path,
            min_corner='[{}]'.format(','.join(map(str, bbox[0]))),
            max_corner='[{}]'.format(','.join(map(str, bbox[1]))),
            scalar_range='[{}]'.format(','.join(map(str, minmax))),
        ))


def get_bbox(all_msh):
    bbox = [None, None]
    for msh_path in all_msh:
        mesh = meshio.read(msh_path)
        mesh_bbox = [
            numpy.amin(mesh.points, axis=0),
            numpy.amax(mesh.points, axis=0)
        ]
        for i in range(2):
            if bbox[i] is None:
                bbox[i] = mesh_bbox[i]
        bbox[0] = numpy.minimum(bbox[0], mesh_bbox[0])
        bbox[1] = numpy.maximum(bbox[1], mesh_bbox[1])
    return bbox


def get_scalar_range(all_msh):
    minmax = [None, None]
    for msh_path in all_msh:
        mesh = meshio.read(msh_path)
        val = mesh.point_data['scalar_value']
        a = numpy.min(val)
        b = numpy.max(val)
        if (minmax[0] is None) or (minmax[0] > a):
            minmax[0] = a
        if (minmax[1] is None) or (minmax[1] < b):
            minmax[1] = b
        break
    return minmax


def main():
    render_dir = "render"
    for folder in [render_dir]:
        if not os.path.exists(folder):
            os.makedirs(folder)
    all_msh = sorted(glob.glob("./output/*.msh"))
    bbox = get_bbox(all_msh)
    minmax = get_scalar_range(all_msh)
    for msh_path in all_msh:
        write_job(msh_path, render_dir, bbox, minmax)


if __name__ == "__main__":
    main()
