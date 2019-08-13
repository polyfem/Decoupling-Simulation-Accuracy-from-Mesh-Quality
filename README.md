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

##### Conda Environment

Install [Miniconda](https://docs.conda.io/en/latest/miniconda.html) for Python 3, and create the environment for this paper from the `conda.yml` file:

```
conda env create -f conda.yml
```

##### PyRenderer (via Singularity)

[PyRenderer](https://github.com/qnzhou/PyRenderer) is used to render the images in the paper. PyRenderer is a wrapper around [Mitsuba](https://github.com/mitsuba-renderer/mitsuba), and as such is a bit complicated to setup.
There is a [Docker image](https://hub.docker.com/r/qnzhou/pyrender) available on Docker-Hub. However, this image is built against the master of the upstream github repository.
To ensure reproducibility of the renders over time, we instead provide a pre-built [Singularity](https://www.sylabs.io) image (>=v3.0.0) of PyRenderer. Singularity is similar to Docker, but does not require root privilege in order to run images. Please read the [documentation](https://sylabs.io/guides/3.3/user-guide/) to install it on your machine.

Our Singularity image can be downloaded programmatically from our Google Drive using `gdown`:

```
pip3 install --user gdown
gdown "https://drive.google.com/uc?id=1zfqiThhSRZkmNDeaXj2nGC1kf00kRIsK"
md5sum pyrenderer.sif
# 557ce7496b29fd11d0808f5ec918a995
```

We also summarize the steps required to install Singularity (>=v3.0.0) on Ubuntu:
1. Install build dependencies:
```
sudo apt update; sudo apt install -y \
    build-essential \
    libgpgme11-dev \
    libseccomp-dev \
    libssl-dev \
    pkg-config \
    uuid-dev \
    git \
    wget
```
2. Clone repository
```
export VERSION=3.3.0 && # adjust this as necessary \
    wget https://github.com/sylabs/singularity/releases/download/v${VERSION}/singularity-${VERSION}.tar.gz && \
    tar -xzf singularity-${VERSION}.tar.gz && \
    cd singularity

```
