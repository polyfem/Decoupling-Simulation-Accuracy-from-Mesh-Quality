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


def prepare(path, times):
    data = load_data(path)
    data = data.loc[(data['args.use_p_ref']) & (data['discr_order'] == 1) & (data['solver_info.final_res_norm'] < 1e-10) & (data['num_flipped'] == 0) & (data['solver_info.num_iterations'] > 0) & (data['solver_info.num_iterations'] < 1000)]

    data = data[["args.mesh", "time_assembling_stiffness_mat", "time_assigning_rhs", "time_building_basis", "time_solving", "num_vertices"]]
    data["args.mesh"] = data["args.mesh"].str.replace("/scratch/yh1998/polyfem300_mesh/", "")
    data["args.mesh"] = data["args.mesh"].str.replace("/scratch/yh1998/polyfem30k/", "")
    data["args.mesh"] = data["args.mesh"].str.replace("/beegfs/work/panozzo/p_ref/tetmesh_mesh/", "")
    data["args.mesh"] = data["args.mesh"].str.replace("/beegfs/work/panozzo/p_ref/polyfem300_mesh/", "")
    data["args.mesh"] = data["args.mesh"].str.replace("_tetmesh.msh.mesh", "")
    data["args.mesh"] = data["args.mesh"].str.replace("_polyfem300.msh.mesh", "")

    data = pandas.merge(data, times, left_on="args.mesh", right_on="mesh_id")

    return data


def get_time(data):
    return data["time_assembling_stiffness_mat"].values + data["time_building_basis"].values + data["time_solving"].values


if __name__ == "__main__":
    output = "time_bad_vs_good"

    times = pandas.read_csv("../data/meshing_time.csv")
    times["mesh_id"] = times["mesh_id"].astype(str)

    nopt = "../data/results_bad.json"
    opt = "../data/results_good.json"

    data_opt = prepare(opt, times)
    data_nopt = prepare(nopt, times)

    # print(data_opt)

    mm1 = pandas.DataFrame({"name": data_opt["args.mesh"].values})
    mm2 = pandas.DataFrame({"name": data_nopt["args.mesh"].values})
    unique_meshes = pandas.merge(mm1, mm2, on="name")["name"]

    print(unique_meshes.count())

    data_opt = data_opt.loc[data_opt['args.mesh'].isin(unique_meshes)]
    data_nopt = data_nopt.loc[data_nopt['args.mesh'].isin(unique_meshes)]

    # print(data_opt.count())
    # print(data_nopt.count())

    time_opt = get_time(data_opt) + data_opt["opt"].values
    time_nopt = get_time(data_nopt) + data_nopt["nopt"].values

    print("time_opt " + str(numpy.mean(time_opt)))
    print("time_nopt " + str(numpy.mean(time_nopt)))


    time_opt = numpy.sort(time_opt)
    time_nopt = numpy.sort(time_nopt)

    count_opt = numpy.arange(len(time_opt))
    count_nopt = numpy.arange(len(time_nopt))

    trace_opt = go.Scatter(
        x=time_opt,
        y=count_opt,
        name="Optimized",
        mode='lines',
        line=dict(color=("rgb(9, 132, 227)")),
    )

    tace_nopt = go.Scatter(
        x=time_nopt,
        y=count_nopt,
        name="Not Optimized",
        mode='lines',
        line=dict(color=("rgb(0, 184, 148)")),
    )

    layout = go.Layout(
        legend=dict(x=0.81, y=0.1),
        xaxis=dict(
            title="Time (s)",
            # tickformat='.1e',
            # exponentformat='power',
            # showticksuffix='all',
            # showtickprefix='all',
            # showexponent='all',
            # type='log',
            # autotick=True,
            # nticks=5,
            # tickangle=45,
            # ticks='outside',
            tickfont=dict(
                size=16
            ),
            range=[0, 600]
            # autorange='reversed'
        ),
        yaxis=dict(
            title="Number of models",
            # tickformat='.1e',
            # exponentformat='power',
            # ticks='',
            # # showticksuffix='none',
            # # showtickprefix='none',
            # # showexponent='all',
            # tick0=0,
            # dtick=1,
            # # tickangle=-45,
            tickfont=dict(
                size=16
            ),
            # type='log',
            # autorange=True
        ),
        font=dict(
            size=24
        ),
        hovermode='closest'
    )

    fig = go.Figure(data=[tace_nopt, trace_opt], layout=layout)

    if output is not None:
        plotly.plot(fig, image="svg", image_filename=output, image_width=1600, image_height=800)
    else:
        plotly.plot(fig)
