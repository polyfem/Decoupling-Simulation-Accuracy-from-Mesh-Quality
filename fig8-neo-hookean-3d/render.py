#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Generates rendering job file + batch script to render them.

find . -name "*.vtu" -exec ~/work/polyfem/python/misc/vtu_to_msh.py \{\} \;

for f in *.json;
    pyrenderer --renderer mitsuba -S $f --up-direction=Z --front-direction=-X;
end
"""

import re
import os
import glob
import numpy
import pymesh


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
                        "mesh": "{msh_path}",
                        "bbox": [{min_corner}, {max_corner}],
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
            "background": "l",
            "name": "{output_path}"
        }}
    ],
    "cameras": [
        {{
            "location": [3.5, 1.0, 1.0]
        }}
    ]
}}
"""

# "transform": [0.69389467, -0.07258616, -0.71640871, -0.71222942, -0.21566388, -0.66799576, -0.10601623, 0.97376606, -0.20134601, 0.55648425, 0.13218482, 1.30217892]

config_ref = """\
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
                        "mesh": "{msh_path}",
                        "bbox": [{min_corner}, {max_corner}],
                        "wire_frame": false
                    }}
                }}
            ],
            "width": 1600,
            "height": 1600,
            "transparent_bg": true,
            "background": "n",
            "name": "{output_path}"
        }}
    ],
    "cameras": [
        {{
            "location": [3.5, 1.0, 1.0]
        }}
    ]
}}
"""

template_sbatch = """\
#!/bin/bash
#
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=8
#SBATCH --time=1:00:00
#SBATCH --mem=32GB
#SBATCH --array=%s
#SBATCH --output=../log/slurm_%%A_%%a.out
#SBATCH --error=../log/slurm_%%A_%%a.err
##SBATCH --reservation=panozzo
##SBATCH --partition=c18_25

# Load modules
module purge

module load mercurial/intel/4.0.1
module load gcc/6.3.0
module load cmake/intel/3.7.1
module load eigen/3.3.1
module load mesa/intel/17.0.2
module load boost/intel/1.62.0
module swap python/intel python3/intel/3.6.3

module load mpfr/gnu/3.1.5
module load zlib/intel/1.2.8
module load suitesparse/intel/4.5.4
module load lapack/gnu/3.7.0
module load gmp/gnu/6.1.2
module load mpc/gnu/1.0.3
module load cuda/8.0.44
module load tbb/intel/2017u3
module load blast+/2.7.1

export CC=${GCC_ROOT}/bin/gcc
export CXX=${GCC_ROOT}/bin/g++

export PARDISO_LIC_PATH="${HOME}/.pardiso"
export PARDISO_INSTALL_PREFIX="${HOME}/.local"
export OMP_NUM_THREADS=8

# Mitsuba
module load xerces-c/intel/3.1.4
module load openexr/intel/2.2.0
module load fftw/intel/3.3.6-pl2
module load ilmbase/intel/2.2.0
module load glew/intel/1.13.0

PYRENDERER=${HOME}/external/git/PyRendererV2/render.py

export MITSUBA_DIR=/scratch/jd3934/mitsuba/mitsuba
export PYTHONPATH="$MITSUBA_DIR/dist/python:$MITSUBA_DIR/dist/python/3.6:$PYTHONPATH"
export LD_LIBRARY_PATH="$MITSUBA_DIR/dist:$LD_LIBRARY_PATH"
export PATH="$MITSUBA_DIR/dist:$PATH"

# Run job
cd "${SLURM_SUBMIT_DIR}"
${PYRENDERER} --renderer mitsuba -S "job_${SLURM_ARRAY_TASK_ID}.json" --up-direction=Z --front-direction=-X;
"""


def atoi(text):
    return int(text) if text.isdigit() else text


def natural_keys(text):
    '''
    alist.sort(key=natural_keys) sorts in human order
    http://nedbatchelder.com/blog/200712/human_sorting.html
    (See Toothy's implementation in the comments)
    '''
    return [atoi(c) for c in re.split('(\d+)', text)]


def write_job(config_str, msh_path, render_dir, bbox, minmax):
    basename = os.path.splitext(msh_path)[0]
    msh_path = os.path.relpath(msh_path, render_dir)
    wire_path = os.path.relpath(basename + '.obj', render_dir)
    basename = os.path.basename(basename)
    output_path = basename + '.png'
    json_path = os.path.join(render_dir, basename + '.json')
    with open(json_path, 'w') as f:
        f.write(config_str.format(
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
        mesh = pymesh.load_mesh(msh_path)
        for i in range(2):
            if bbox[i] is None:
                bbox[i] = mesh.bbox[i]
        bbox[0] = numpy.minimum(bbox[0], mesh.bbox[0])
        bbox[1] = numpy.maximum(bbox[1], mesh.bbox[1])
    return bbox


def get_scalar_range(all_msh):
    minmax = [None, None]
    for msh_path in all_msh:
        mesh = pymesh.load_mesh(msh_path)
        val = mesh.get_vertex_attribute('scalar_value')
        a = numpy.min(val)
        b = numpy.max(val)
        if (minmax[0] is None) or (minmax[0] > a):
            minmax[0] = a
        if (minmax[1] is None) or (minmax[1] < b):
            minmax[1] = b
        break
    return minmax


def write_sbatch(render_dir, num_jobs):
    content = template_sbatch % ('-'.join(['0', str(num_jobs - 1)]))
    with open(os.path.join(render_dir, 'all.sh'), 'w') as f:
        f.write(content)


def main():
    render_dir = "render"
    for folder in [render_dir]:
        if not os.path.exists(folder):
            os.makedirs(folder)
    all_msh = sorted(list(glob.glob("./output/*_n20.msh")), key=natural_keys)
    bbox = get_bbox(all_msh)
    minmax = get_scalar_range(all_msh)
    for msh_path in all_msh:
        write_job(config, msh_path, render_dir, bbox, minmax)
    write_job(config_ref, all_msh[-1], render_dir, bbox, minmax)
    write_sbatch(render_dir, len(all_msh) + 1)


if __name__ == "__main__":
    main()
