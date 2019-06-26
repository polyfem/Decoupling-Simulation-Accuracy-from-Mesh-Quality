#!/usr/bin/env python
# -*- coding: utf-8 -*-

# System libs
import json
import numpy

from pandas.io.json import json_normalize

import plotly.graph_objs as go
import plotly.offline as plotly


colors = {'1': 'rgb(255, 201, 26)', '2': 'rgb(250, 177, 160)', '3': 'rgb(255, 118, 117)', '4': 'rgb(253, 121, 168)', '5': 'rgb(232, 67, 147)'}


def get_plot_data(data, unique_meshes):
    data_tmp = data.loc[data['mesh_path'].isin(unique_meshes) & (data['args.use_p_ref']) & (data['solver_info.final_res_norm'] < 1e-10) & (data['num_flipped'] == 0) & (data['solver_info.num_iterations'] > 0) & (data['solver_info.num_iterations'] < 1000)]

    num_p1 = data_tmp["num_p1"].values
    num_p2 = data_tmp["num_p2"].values
    num_p3 = data_tmp["num_p3"].values
    num_p4 = data_tmp["num_p4"].values
    num_p5 = data_tmp["num_p5"].values

    total = num_p1 + num_p2 + num_p3 + num_p4 + num_p5
    print(len(num_p1))

    return [num_p1 / total, num_p2 / total, num_p3 / total, num_p4 / total, num_p5 / total]


def iterate(data):
    plot_data = []

    has_p3 = data.loc[data['discr_order'] == 3]["mesh_path"].count()
    unique_meshes = data.groupby('mesh_path').filter(lambda x: len(x) == (4 if has_p3 else 2))['mesh_path']

    plot_data = get_plot_data(data, unique_meshes)

    return plot_data


def load_data(path):
    with open(path, 'r') as f:
        data = json.load(f)

    return json_normalize(data)


def draw_figure(path, output):
    data = load_data(path)

    plot_data = iterate(data)

    hist_data = []
    group_labels = []
    cols = []

    layout = go.Layout(
        # title=title,
        legend=dict(x=0.81, y=1),
        # title='Styled Scatter',
        # xaxis=dict(
        #     title=field.replace("_", " ").title(),
        #     # range=[0, 64]
        # ),
        yaxis=dict(
            tickformat='%',
            range=[0, 1]
        ),
        # xaxis=dict(
        #     ticktext=lambda x: str(pow(x, 10)),
        # ),
        font=dict(
            size=24
        ),
        # barmode='overlay',
        # bargroupgap=0.1,
        # bargap=0.1
    )

    for k in range(4):
        hist_data.append(numpy.mean(plot_data[k]))
        group_labels.append("P" + str(k + 1))
        cols.append(colors[str(k + 1)])

    trace = go.Bar(
        x=group_labels,
        y=hist_data,
        textposition='outside',
        text=['{:.2%}'.format(i) for i in hist_data],
        marker=dict(color=cols),
    )

    fig = go.Figure(data=[trace], layout=layout)

    if output is not None:
        plotly.plot(fig, image="svg", image_filename=output)
    else:
        plotly.plot(fig)


def main():
    for is_bad in [True, False]:
        postfix = "bad" if is_bad else "good"
        draw_figure("../data/results_" + postfix + ".json", postfix)


if __name__ == "__main__":
    main()
