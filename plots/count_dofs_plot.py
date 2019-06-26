#!/usr/bin/env python
# -*- coding: utf-8 -*-

# System libs
import json

from pandas.io.json import json_normalize

import plotly.graph_objs as go
import plotly.offline as plotly


colors = {'1': 'rgb(255, 201, 26)', '2': 'rgb(250, 177, 160)', '3': 'rgb(255, 118, 117)', '4': 'rgb(253, 121, 168)', '5': 'rgb(232, 67, 147)'}


def compute_percentage(data, unique_meshes):
    data_tmp = data.loc[data['mesh_path'].isin(unique_meshes) & (data['args.use_p_ref']) & (data['solver_info.final_res_norm'] < 1e-10) & (data['num_flipped'] == 0) & (data['solver_info.num_iterations'] > 0) & (data['solver_info.num_iterations'] < 1000)]

    dofs = data_tmp["num_dofs"].values
    vertices = data_tmp["num_vertices"].values

    val = dofs / vertices

    for i in range(len(val)):
        if val[i] >= 15:
            val[i] = 15

    return val


def iterate(data):
    percs = []

    has_p3 = data.loc[data['discr_order'] == 3]["mesh_path"].count()
    unique_meshes = data.groupby('mesh_path').filter(lambda x: len(x) == (4 if has_p3 else 2))['mesh_path']

    percs = compute_percentage(data, unique_meshes)

    return percs


def load_data(path):
    with open(path, 'r') as f:
        data = json.load(f)

    return json_normalize(data)


def draw_figure(path, output):
    data = load_data(path)

    plot_data = iterate(data)

    layout = go.Layout(
        legend=dict(x=0.81, y=1),
        yaxis=dict(
            tickformat='.1%',
            range=[0, 0.13]
        ),
        xaxis=dict(
            range=[1, 15]
        ),
        font=dict(
            size=24
        )
    )

    trace = go.Histogram(
        x=plot_data,
        xbins=dict(
            start=1,
            end=15,
            size=0.2
        ),
        histnorm='probability',
        marker=dict(color='rgb(85, 239, 196)'),
    )

    fig = go.Figure(data=[trace], layout=layout)

    if output is not None:
        plotly.plot(fig, image="svg", image_filename=output)
    else:
        plotly.plot(fig)


def main():
    draw_figure("../data/results_bad.json", "bad_dofs")
    draw_figure("../data/results_good.json", "good_dofs")


if __name__ == "__main__":
    main()
