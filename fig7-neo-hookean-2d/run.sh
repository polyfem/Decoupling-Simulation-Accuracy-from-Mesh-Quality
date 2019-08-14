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

${POLYFEM_BIN} --cmd --json job_0.json
${POLYFEM_BIN} --cmd --json job_1.json
${POLYFEM_BIN} --cmd --json job_2.json
${POLYFEM_BIN} --cmd --json job_3.json
${POLYFEM_BIN} --cmd --json job_4.json
${POLYFEM_BIN} --cmd --json job_5.json
# ${POLYFEM_BIN} --cmd --json job_6.json
# ${POLYFEM_BIN} --cmd --json job_7.json
# ${POLYFEM_BIN} --cmd --json job_8.json
# ${POLYFEM_BIN} --cmd --json job_9.json

popd

# 3. Process output files
VTU_TO_MSH=../scripts/vtu_to_msh.py
find . -name "*.vtu" -exec ${VTU_TO_MSH} {} \;

# 4. Create render job files
python render.py

# # 5. Render selected files
pushd render
to_render=(
	job_0.json
	job_1.json
	job_2.json
	job_3.json
	job_4.json
	job_5.json
	# job_6.json
	# job_7.json
	# job_8.json
	# job_9.json
)
for f in "${to_render[@]}"; do
    ${CONTAINER} bash -c ". /usr/local/mitsuba/setpath.sh; pushd `pwd`; render.py --renderer mitsuba -S $f --front-direction=Z --up-direction=Y --head-on;"
done
popd

# 6. Rename files
# mkdir -p teaser
# pushd render
# popd
