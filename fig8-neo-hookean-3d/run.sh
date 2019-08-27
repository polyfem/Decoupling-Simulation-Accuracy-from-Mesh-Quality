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

${POLYFEM_BIN} --cmd --json job_0.json | tee ../log/job_0.log
${POLYFEM_BIN} --cmd --json job_1.json | tee ../log/job_1.log
${POLYFEM_BIN} --cmd --json job_2.json | tee ../log/job_2.log
${POLYFEM_BIN} --cmd --json job_3.json | tee ../log/job_3.log
${POLYFEM_BIN} --cmd --json job_4.json | tee ../log/job_4.log
${POLYFEM_BIN} --cmd --json job_5.json | tee ../log/job_5.log
${POLYFEM_BIN} --cmd --json job_6.json | tee ../log/job_6.log
${POLYFEM_BIN} --cmd --json job_7.json | tee ../log/job_7.log
${POLYFEM_BIN} --cmd --json job_8.json | tee ../log/job_8.log
${POLYFEM_BIN} --cmd --json job_9.json | tee ../log/job_9.log
${POLYFEM_BIN} --cmd --json job_10.json | tee ../log/job_10.log

popd

# # 3. Process output files
# VTU_TO_MSH=../scripts/vtu_to_msh.py
# find . -name "*.vtu" -exec ${VTU_TO_MSH} {} \;

# # 4. Create render job files
# python render.py

# # # 5. Render selected files
# pushd render
# to_render=(
# 	job_0.json
# 	job_1.json
# 	job_2.json
# 	job_3.json
# 	job_4.json
# 	job_5.json
# 	job_6.json
# 	# job_7.json
# 	job_8.json
# 	# job_9.json
# )
# for f in "${to_render[@]}"; do
#     ${CONTAINER} bash -c ". /usr/local/mitsuba/setpath.sh; pushd `pwd`; render.py --renderer mitsuba -S $f --front-direction=Z --up-direction=Y --head-on;"
# done
# popd

# # 6. Rename files
# mkdir -p fig
# pushd render
# # cp job_0.png ../fig/ours_0.png # Not used in the paper
# cp job_2.png ../fig/ours_1.png
# cp job_4.png ../fig/ours_2.png
# cp job_6.png ../fig/ours_3.png
# cp job_8.png ../fig/ours_4.png
# # cp job_1.png ../fig/p1_0.png # Not used in the paper
# cp job_3.png ../fig/p1_1.png
# cp job_5.png ../fig/p1_2.png
# # cp job_7.png ../fig/p1_3.png
# # cp job_9.png ../fig/p1_4.png
# popd
