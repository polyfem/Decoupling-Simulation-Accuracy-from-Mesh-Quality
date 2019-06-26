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

<!-- ##### Git LFS

This repository contains some large files that are tracked via [Git LFS](https://git-lfs.github.com/). After installing Git LFS on your machine, activate it for this repository, and fetch the tacked objects by running:

```
git lfs install
git lfs fetch
``` -->

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

##### PyRenderer (via Singularity)

[PyRenderer](https://github.com/qnzhou/PyRenderer) is used to render the images in the paper. PyRenderer is a wrapper around [Mitsuba](https://github.com/mitsuba-renderer/mitsuba), and as such is a bit complicated to setup. To ensure reproducibility of the results, a [Singularity](https://www.sylabs.io) image of PyRenderer is provided. Singularity is similar to Docker, but does not require root privilege in order to run images. Please read the [documentation](https://www.sylabs.io/guides/3.2/user-guide/index.html) to install it on your machine.

##### Conda Environment

Install [Miniconda](https://docs.conda.io/en/latest/miniconda.html) for Python 3, and create the environment for this paper from the `conda.yml` file:

```
conda create env -f conda.yml
```
