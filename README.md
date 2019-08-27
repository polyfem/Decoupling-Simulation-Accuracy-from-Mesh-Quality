# Decoupling Simulation Accuracy from Mesh Quality

This repository contains the scripts to regenerate the figures in the paper:
> Decoupling Simulation Accuracy from Mesh Quality

```bibtex
@article{Schneider:2018:DSA,
    author = {Teseo Schneider and Yixin Hu and Jérémie Dumas and Xifeng Gao and Daniele Panozzo and Denis Zorin},
    journal = {ACM Transactions on Graphics},
    link = {},
    month = {10},
    number = {6},
    publisher = {Association for Computing Machinery (ACM)},
    title = {Decoupling Simulation Accuracy from Mesh Quality},
    volume = {37},
    year = {2018}
}
```

### Dependencies

##### PolyFEM

A specific version of [PolyFEM](https://github.com/polyfem/polyfem) is included as a submodule. To retrieve and compile it, run the following commands:

```
git submodule update --init --recursive
cd polyfem
mkdir build
cd build
cmake ..
make -j 8
```

Make sure that [PARDISO](https://www.pardiso-project.org/) is found and enabled, otherwise you might not be able to generate certain figures (see below). In PolyFEM, `FindPardiso.cmake` will look for the PARDISO library in `~/.local` or `~/.pardiso`. If you installed PARDISO in a different location, you may need to update this file accordingly.

##### Conda Environment

Install [Miniconda](https://docs.conda.io/en/latest/miniconda.html) for Python 3, and create the environment for this paper from the `conda.yml` file:

```
conda env create -f conda.yml
```

##### PyRenderer (via Singularity/Docker)

[PyRenderer](https://github.com/qnzhou/PyRenderer) is used to render the images in the paper. PyRenderer is a wrapper around [Mitsuba](https://github.com/mitsuba-renderer/mitsuba), and as such is a bit complicated to setup.
There is a [Docker image](https://hub.docker.com/r/qnzhou/pyrender) available on Docker-Hub.
We also provide a pre-built Singularity [Singularity](https://www.sylabs.io) image (>=v3.0.0) of PyRenderer. Singularity is similar to Docker, but does not require root privilege in order to run images. Please read the [documentation](https://sylabs.io/guides/3.3/user-guide/) to install it on your machine.

- <details><summary>Our Singularity image can be downloaded programmatically from our Google Drive using `gdown` (click to expand).</summary><p>
```
pip3 install --user gdown
gdown "https://drive.google.com/uc?id=1zfqiThhSRZkmNDeaXj2nGC1kf00kRIsK"
md5sum pyrenderer.sif
# 557ce7496b29fd11d0808f5ec918a995
```
</p></details>

- For docker users, make sure to:
    1. [Install Docker](https://docs.docker.com/install/linux/docker-ce/ubuntu/) following official instructions.
    2. [Allow](https://docs.docker.com/install/linux/linux-postinstall/) to run docker as a non-root user.

### Solver

As stated in the paper, we use [PARDISO](https://www.pardiso-project.org/) for the following figures:
- Figure 7
- Figure 8
- Figure 11
- Figure 21
- Table 1

And [HYPRE](https://computing.llnl.gov/projects/hypre-scalable-linear-solvers-multigrid-methods) for the following figures:
- Figure 9
- Figure 10
- Figure 16
- Figure 17
- Figure 20


If you try to generate the first figures with an iterative solver, running times may be exceedingly long, so it is not recommended.
