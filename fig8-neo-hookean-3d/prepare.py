#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Generates jobs to run with polyfem.

Usage:

1. Run
   `python prepare.py`

2. Go into the job folder
   `cd jobs/`

3. Either run each job individually
   `PolyFEM_bin -cmd job_0.json`

4. Or batch it with slurm
   `sbatch batch.sh`
"""

import os
import glob
import json
import itertools

config = {
    "mesh": sorted(list(glob.glob("./meshes/*.mesh"))),
    "problem": "GenericTensor",
    "normalize_mesh": True,
    "discr_order": 1,
    "use_p_ref": [True, False],
    "tensor_formulation": "NeoHookean",

    "output": "",
    "export": {},

    "params": {
        "lambda": 0.5769230769230769,
        "mu": 0.3846153846153846
    },

    # "solver_type": "Eigen::CholmodSupernodalLLT",
    "problem_params": {
        "dirichlet_boundary": [{
            "id": 5,
            "value": [0.0, 0.0, 0.0]
        }],
        "neumann_boundary": [{
            "id": 6,
            "value": [0.1, 0.0, 0.0]
        }]
    }
}

config_ref = {
    "mesh": sorted(list(glob.glob("./meshes/*.mesh")))[0],
    "problem": "GenericTensor",
    "normalize_mesh": True,
    "discr_order": 3,
    "use_p_ref": False,
    "tensor_formulation": "NeoHookean",

    "output": "",
    "export": {},

    "params": {
        "lambda": 0.5769230769230769,
        "mu": 0.3846153846153846
    },

    "problem_params": {
        "dirichlet_boundary": [{
            "id": 5,
            "value": [0.0, 0.0, 0.0]
        }],
        "neumann_boundary": [{
            "id": 6,
            "value": [0.1, 0.0, 0.0]
        }]
    }
}

template_sbatch = """\
#!/bin/bash
#
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=8
#SBATCH --time=30:00:00
#SBATCH --mem=64GB
#SBATCH --array=%s
#SBATCH --output=../log/slurm_%%A_%%a.out
#SBATCH --error=../log/slurm_%%A_%%a.err
##SBATCH --reservation=panozzo
#SBATCH --partition=c18_25

# Load modules
module purge

module load mercurial/intel/4.0.1
module load gcc/6.3.0
module load cmake/intel/3.7.1
module load eigen/3.3.1
module load mesa/intel/17.0.2
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

POLYFEM_BIN=${HOME}/work/polyfem/cpp/build/Release/PolyFEM_bin

# Run job
cd "${SLURM_SUBMIT_DIR}"
${POLYFEM_BIN} -cmd -json "job_${SLURM_ARRAY_TASK_ID}.json"
"""


def generate_jobs(entry):
    """
    Generate a list of job configurations by varying the parameters in the given entry.
    In practice, computes the cartesian product of all the lists at the toplevel of
    the input dictionary, and generates one job for each resulting instance.

    Args:
        entry (dict): Input job configurations

    Returns:
        list: List of jobs with list parameters replaced by actual values
    """
    keys = [k for k, v in entry.items() if isinstance(v, list)]
    all_vals = itertools.product(
        *[v for __, v in entry.items() if isinstance(v, list)])
    all_jobs = []
    for vals in all_vals:
        job = entry.copy()
        for k, v in zip(keys, vals):
            job[k] = v
        all_jobs.append(job)
    return all_jobs


def write_job(entry, job_id, output_dir, job_dir):
    """
    Writes a job file corresponding the given entry. Also sets the output paths
    for the given job (json, vis_mesh, wire_mesh, etc.). The resulting job
    file is written in `job_dir`, and all paths are transformed to be relative
    to the `job_dir` the file is written to.

    Args:
        entry (dict): Job file to write to disk
        job_id (int): Unique id of the job to write
        output_dir (str): Path to the directory for output data
        job_dir (str): Path to the directory where to write the job file
    """
    job_name = "job_{}".format(job_id)
    job_path = os.path.join(job_dir, job_name + '.json')
    baseout = os.path.realpath(os.path.join(output_dir, job_name))
    entry["mesh"] = os.path.relpath(entry["mesh"], job_dir)
    entry["output"] = os.path.relpath(baseout + '.json', job_dir)
    entry["export"]["vis_mesh"] = os.path.relpath(baseout + '.vtu', job_dir)
    entry["export"]["wire_mesh"] = os.path.relpath(baseout + '.obj', job_dir)
    entry["stiffness_mat_save_path"] = os.path.relpath(baseout + '.mat', job_dir)
    with open(job_path, 'w') as f:
        f.write(json.dumps(entry, indent=4))


def write_sbatch(job_dir, num_jobs):
    content = template_sbatch % ('-'.join(['0', str(num_jobs - 1)]))
    with open(os.path.join(job_dir, 'all.sh'), 'w') as f:
        f.write(content)


def main():
    output_dir = "output"
    job_dir = "jobs"
    log_dir = "log"
    for folder in [output_dir, job_dir, log_dir]:
        if not os.path.exists(folder):
            os.makedirs(folder)
    all_jobs = generate_jobs(config)
    for i, job in enumerate(all_jobs):
        write_job(job, i, output_dir, job_dir)
    write_job(config_ref, i + 1, output_dir, job_dir)
    write_sbatch(job_dir, len(all_jobs) + 1)


if __name__ == "__main__":
    main()
