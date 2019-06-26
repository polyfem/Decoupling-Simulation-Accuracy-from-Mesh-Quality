import os
import sys

in_dir = sys.argv[1]
out_dir = sys.argv[2]

order = 1
B = 3
configs = [[str(order), 'false', str(B)], [str(order), 'true', str(B)]]

for root, dirs, files in os.walk(in_dir):
    for file in files:
        if not file.endswith('mesh'):
            continue
        for config in configs:
            f = open(in_dir+'/'+file+'_'+config[0]+'_'+config[1]+'_'+config[2]+'_input.json', 'w')
            f.write('{\n')
            f.write('"mesh": "'+in_dir+'/'+file+'",\n')
            f.write('"problem": "Franke",\n')
            f.write('"normalize_mesh": true,\n')
            f.write('"discr_order": '+config[0]+',\n')
            f.write('"use_p_ref": '+config[1]+',\n')
            f.write('"solver_type": "Hypre",\n')
            f.write('"iso_parametric": false,\n')
            f.write('"B": '+config[2]+',\n')
            f.write('"n_boundary_samples": 6,\n')
            f.write('"h1_formula": false,\n')
            f.write('"output": "'+out_dir+'/'+file+'_'+config[0]+'_'+config[1]+'_'+config[2]+'.json"\n')
            f.write('}\n')
            f.close()
    break

# cat intersection_10k_mesh_tmp/tetgen_123044.msh.mesh_1_false_3_input.json
# {
#     "mesh": "/beegfs/work/panozzo/p_ref/intersection_10k_mesh/tetgen_123044.msh.mesh",
#     "problem": "Franke",
#     "normalize_mesh": true,
#     "discr_order": 1,
#     "use_p_ref": false,
#     "solver_type": "Hypre",
#     "iso_parametric": false,
#     "B": 3,
#     "n_boundary_samples": 6,
#     "h1_formula": false,
#     "output": "/beegfs/work/panozzo/p_ref/intersection_10k_mesh_output/tetgen_123044.msh.mesh_1_false_3.json"
# }