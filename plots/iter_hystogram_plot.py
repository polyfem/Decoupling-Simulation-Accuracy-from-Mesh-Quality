#!/usr/bin/env python
# -*- coding: utf-8 -*-

# System libs
import json

from pandas.io.json import json_normalize

import plotly.graph_objs as go
import plotly.offline as plotly
import plotly.figure_factory as ff


colors = {'pref': 'rgb(85, 239, 196)', '1': 'rgb(255, 201, 26)', '2': 'rgb(250, 177, 160)', '3': 'rgb(255, 118, 117)', '4': 'rgb(253, 121, 168)', '5': 'rgb(232, 67, 147)'}


def get_plot_data(data, unique_meshes, field, discr_order, is_p_ref):
    name = "Ours" if is_p_ref else ("P" + str(discr_order))
    key = 'pref' if is_p_ref else str(discr_order)

    data_tmp = data.loc[data['mesh_path'].isin(unique_meshes) & (data['args.use_p_ref'] == is_p_ref) & (data['discr_order'] == discr_order) & (data['solver_info.final_res_norm'] < 1e-10) & (data['num_flipped'] == 0) & (data['solver_info.num_iterations'] > 0) & (data['solver_info.num_iterations'] < 1000)]
    real_data = data_tmp[field]

    return [real_data, name, colors[key]]


def iterate(data, field):
    plot_data = []

    has_p3 = data.loc[data['discr_order'] == 3]["mesh_path"].count()
    unique_meshes = data.groupby('mesh_path').filter(lambda x: len(x) == (4 if has_p3 else 2))['mesh_path']

    plot_data.append(get_plot_data(data, unique_meshes, field, 1, True))
    plot_data.append(get_plot_data(data, unique_meshes, field, 1, False))

    return plot_data


def load_data(path):
    with open(path, 'r') as f:
        data = json.load(f)

    return json_normalize(data)


def draw_figure(path, field, output):
    data = load_data(path)

    plot_data = iterate(data, field)

    hist_data = []
    group_labels = []
    cols = []

    for d in plot_data:
        tmp = []
        for v in d[0]:
            tmp.append(v)

        hist_data.append(tmp)
        group_labels.append(d[1])
        cols.append(d[2])

    fig = ff.create_distplot(hist_data, group_labels, colors=cols, histnorm='probability', bin_size=1, show_rug=False, show_curve=False)

    layout = go.Layout(
        # title=title,
        legend=dict(x=0.81, y=1),
        font=dict(
            size=24
        ),
        xaxis=dict(range=[0, 130]),
        yaxis=dict(range=[0, 0.25])
    )

    fig['layout'].update(layout)

    if output is not None:
        plotly.plot(fig, image="svg", image_filename=output)
    else:
        plotly.plot(fig)


def main():
    field = "solver_info.num_iterations"

    draw_figure("../data/results_good.json", field, "good_iters")
    draw_figure("../data/results_bad.json", field, "bad_iters")


if __name__ == "__main__":
    main()
