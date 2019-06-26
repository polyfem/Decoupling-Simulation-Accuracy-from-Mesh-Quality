import os
import json
import subprocess
import tempfile

if __name__ == '__main__':
    polyfem_exe = "./PolyFEM_bin"
    out_folder = "cond_num"

    n_refs = [0, 1, 2, 3]
    p_refs = [False, True]

    current_folder = cwd = os.getcwd()

    with open("test.json", 'r') as f:
        json_data = json.load(f)


    for is_bad in [True, False]:
        mesh = "../data/conditioning_44000_bad.mesh" if is_bad else "../data/conditioning_44000_good.mesh"
        out_f = out_folder + ('bad' if is_bad else 'good')

        for ref in n_refs:
            for pref in p_refs:
                json_data["mesh"] = mesh
                json_data["n_refs"] = ref
                json_data["use_p_ref"] = pref

                json_data["output"]                  = os.path.join(os.getcwd(), out_f, "out_" + str(ref) + ("_pref" if pref else "") + ".json")
                json_data["stiffness_mat_save_path"] = os.path.join(os.getcwd(), out_f, "mat_" + str(ref) + ("_pref" if pref else "") + ".json")

                with tempfile.NamedTemporaryFile(suffix=".json") as tmp_json:
                    with open(tmp_json.name, 'w') as f:
                        f.write(json.dumps(json_data, indent=4))

                    args = [polyfem_exe, '-json', tmp_json.name, '-cmd']

                    subprocess.run(args)
