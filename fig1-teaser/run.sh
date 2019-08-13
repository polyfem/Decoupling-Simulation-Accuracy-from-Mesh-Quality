#! /bin/bash

SCRIPT_PATH="$( cd "$(dirname "$0")" ; pwd -P )"

POLYFEM_BIN=${SCRIPT_PATH}/../polyfem/build/PolyFEM_bin
# CONTAINER="singularity exec ${SCRIPT_PATH}/../pyrenderer.sif"
CONTAINER="docker run -it --rm -v `pwd`:`pwd` qnzhou/pyrender"

# Enable conda
if [ -f /opt/miniconda3/etc/profile.d/conda.sh ]; then
	source /opt/miniconda3/etc/profile.d/conda.sh
elif [ -f ${HOME}/miniconda3/etc/profile.d/conda.sh ]; then
	source ${HOME}/miniconda3/etc/profile.d/conda.sh
fi

conda activate decoupling-paper

# 1. Prepare job scripts
python3 prepare.py

# 2. Execute job scripts
pushd jobs

# ${POLYFEM_BIN} --cmd --json job_0.json
# ${POLYFEM_BIN} --cmd --json job_10.json
# ${POLYFEM_BIN} --cmd --json job_11.json
# ${POLYFEM_BIN} --cmd --json job_12.json
# ${POLYFEM_BIN} --cmd --json job_13.json
# ${POLYFEM_BIN} --cmd --json job_14.json
# ${POLYFEM_BIN} --cmd --json job_15.json
# ${POLYFEM_BIN} --cmd --json job_16.json
# ${POLYFEM_BIN} --cmd --json job_17.json
# ${POLYFEM_BIN} --cmd --json job_18.json
# ${POLYFEM_BIN} --cmd --json job_1.json
# ${POLYFEM_BIN} --cmd --json job_2.json
# ${POLYFEM_BIN} --cmd --json job_3.json
# ${POLYFEM_BIN} --cmd --json job_4.json
${POLYFEM_BIN} --cmd --json job_5.json
# ${POLYFEM_BIN} --cmd --json job_6.json
# ${POLYFEM_BIN} --cmd --json job_7.json
# ${POLYFEM_BIN} --cmd --json job_8.json
# ${POLYFEM_BIN} --cmd --json job_9.json

popd

# 3. Process output files
VTU_TO_MSH=../scripts/vtu_to_msh.py
# find . -name "*.vtu" -exec ${VTU_TO_MSH} {} -s -d {}_discr.msh \;

# 4. Create render job files
python render.py

# 5. Render selected files
pushd render
to_render=(
	job_4.json
	job_5.json
	job_8.json
	job_9.json
	job_12.json
	job_13.json
	job_16.json
	job_17.json
	job_18.json
)
for f in "${to_render[@]}"; do
    ${CONTAINER} bash -c ". /usr/local/mitsuba/setpath.sh; render.py --renderer mitsuba -S `pwd`/$f --front-direction=X --up-direction=Z;"
done
popd

# 6. Rename files which are in the teaser
mkdir -p teaser
pushd render
cp job_4.png  ../teaser/bridge_2p.png
cp job_5.png  ../teaser/bridge_2.png
cp job_8.png  ../teaser/bridge_4p.png
cp job_9.png  ../teaser/bridge_4.png
cp job_12.png ../teaser/bridge_6p.png
cp job_13.png ../teaser/bridge_6.png
cp job_16.png ../teaser/bridge_8p.png
cp job_17.png ../teaser/bridge_8.png
cp job_18.png ../teaser/bridge_ref.png
popd
