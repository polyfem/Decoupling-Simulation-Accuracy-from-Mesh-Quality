#!/usr/bin/env python
# -*- coding: utf-8 -*-

# System libs
import json
import numpy
import pandas

from pandas.io.json import json_normalize

import plotly.graph_objs as go
import plotly.offline as plotly


def load_data(path):
    with open(path, 'r') as f:
        data = json.load(f)

    return json_normalize(data)


def prepare(path, times, is_pref):
    data = load_data(path)
    data = data.loc[(data['args.use_p_ref'] == is_pref) & (data['discr_order'] == 1) & (data['solver_info.final_res_norm'] < 1e-10) & (data['num_flipped'] == 0) & (data['solver_info.num_iterations'] > 0) & (data['solver_info.num_iterations'] < 1000)]

    data = data[["args.mesh", "time_assembling_stiffness_mat", "time_assigning_rhs", "time_building_basis", "time_solving", "num_vertices"]]
    data["args.mesh"] = data["args.mesh"].str.replace("/scratch/yh1998/polyfem300_mesh/", "")
    data["args.mesh"] = data["args.mesh"].str.replace("/scratch/yh1998/polyfem30k/", "")
    data["args.mesh"] = data["args.mesh"].str.replace("/beegfs/work/panozzo/p_ref/tetmesh_mesh/", "")
    data["args.mesh"] = data["args.mesh"].str.replace("/beegfs/work/panozzo/p_ref/polyfem300_mesh/", "")
    data["args.mesh"] = data["args.mesh"].str.replace("_tetmesh.msh.mesh", "")
    data["args.mesh"] = data["args.mesh"].str.replace("_polyfem300.msh.mesh", "")

    data = pandas.merge(data, times, left_on="args.mesh", right_on="mesh_id")

    return data




def create_one(key, is_pref):
    numpy.random.seed(42)
    output = "time_separate_" + key + "_" + ("pref" if is_pref else "p1")
    # output = None

    times = pandas.read_csv("../data/meshing_time.csv")
    times["mesh_id"] = times["mesh_id"].astype(str)

    nopt = "../data/results_bad.json"
    opt = "../data/results_good.json"

    data_opt = prepare(opt, times, is_pref)
    data_nopt = prepare(nopt, times, is_pref)

    mm1 = pandas.DataFrame({"name": data_opt["args.mesh"].values})
    mm2 = pandas.DataFrame({"name": data_nopt["args.mesh"].values})
    unique_meshes = pandas.merge(mm1, mm2, on="name")["name"]

    print(unique_meshes.count())

    data_opt = data_opt.loc[data_opt['args.mesh'].isin(unique_meshes)]
    data_nopt = data_nopt.loc[data_nopt['args.mesh'].isin(unique_meshes)]


    if key == 'opt':
        data = data_opt
    else:
        data = data_nopt

    data = data.sort_values(by=["args.mesh"])
    count = numpy.arange(len(data[key].values))
    # count_nopt = numpy.arange(len(data_nopt["nopt"].values))
    # mask = numpy.random.choice([False, True], size=len(count), p=[0.987, 0.013])
    indices = numpy.random.choice(len(count), 100, replace=False)

    count = numpy.arange(len(data["time_building_basis"].values[indices]))
    print(len(count))




    meshing_data  = data[key].values[indices]
    basis_data    = data["time_building_basis"].values[indices]
    assembly_data = data["time_assembling_stiffness_mat"].values[indices]
    solving_data  = data["time_solving"].values[indices]

    asd  = data["args.mesh"].values[indices]
    print(asd)

    # meshing = go.Bar(
    #     x=count,
    #     y=meshing_data,
    #     name="Meshing",
    #     # marker=dict(color=("rgb(0, 184, 148)")),
    # )

    basis = go.Bar(
        x=count,
        y=basis_data,
        name="Build bases",
        marker=dict(color=("#095d46" if is_pref else "#ce9e17")),
    )

    assembly = go.Bar(
        x=count,
        y=assembly_data,
        name="Assembly",
        marker=dict(color=("#12ba8b" if is_pref else "#ffc91a")),
    )

    solving = go.Bar(
        x=count,
        y=solving_data,
        name="Solving",
        marker=dict(color=("#45edbe" if is_pref else "#ffde8d")),
    )

    layout = go.Layout(
        legend=dict(x=0.81, y=0.9),
        # title=key + ' ' + ('ours' if is_pref else 'P1'),
        barmode='stack',
        xaxis=dict(
            tickfont=dict(
                size=16
            )
        ),
        yaxis=dict(
            # title="Time (s)",
            tickfont=dict(
                size=16
            ),
            range=[0, 60]
        ),
        font=dict(
            size=24
        ),
        hovermode='closest'
    )

    fig = go.Figure(data=[basis, assembly, solving], layout=layout)

    if output is not None:
        plotly.plot(fig, image="svg", image_filename=output)
    else:
        plotly.plot(fig)


if __name__ == "__main__":
    # key = 'opt'
    key = 'nopt'
    is_pref = False

    create_one("opt", True)
    create_one("nopt", True)

    create_one("opt", False)
    create_one("nopt", False)
