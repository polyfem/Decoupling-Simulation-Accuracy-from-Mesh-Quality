#!/usr/bin/env python
# -*- coding: utf-8 -*-

# System libs
import json

from pandas.io.json import json_normalize

import plotly.graph_objs as go
import plotly.offline as plotly
import plotly.figure_factory as ff

colors = {'low quality': 'rgb(116, 185, 255)', 'high quality': 'rgb(162, 155, 254)'}


def get_plot_data(data, unique_meshes, field, discr_order, is_p_ref, name):
    data_tmp = data.loc[data['mesh_path'].isin(unique_meshes) & (data['args.use_p_ref'] == is_p_ref) & (data['discr_order'] == discr_order) & (data['solver_info.final_res_norm'] < 1e-10) & (data['num_flipped'] == 0) & (data['solver_info.num_iterations'] > 0) & (data['solver_info.num_iterations'] < 1000)]
    real_data = data_tmp[field]

    return [real_data, name, colors[name]]


def iterate(data, field, name):
    plot_data = []

    has_p3 = data.loc[data['discr_order'] == 3]["mesh_path"].count()
    unique_meshes = data.groupby('mesh_path').filter(lambda x: len(x) == (4 if has_p3 else 2))['mesh_path']

    plot_data.append(get_plot_data(data, unique_meshes, field, 1, True, name))

    return plot_data


def load_data(path):
    with open(path, 'r') as f:
        data = json.load(f)

    return json_normalize(data)


def draw_figure(plot_data, output):
    hist_data = []
    group_labels = []
    cols = []

    for d in plot_data:
        tmp = []
        for v in d[0]:
            tmp.append(min(v, 200000))

        hist_data.append(tmp)
        group_labels.append(d[1].title())
        cols.append(d[2])

    fig = ff.create_distplot(hist_data, group_labels, colors=cols, histnorm='probability', bin_size=3000, show_rug=True)

    layout = go.Layout(
        # title=title,
        legend=dict(x=0.81, y=1),
        font=dict(
            size=24
        ),
        yaxis=dict(range=[0, 0.6])
    )

    fig['layout'].update(layout)

    if output is not None:
        plotly.plot(fig, image="svg", image_filename=output)
    else:
        plotly.plot(fig)


def main():
    field = "num_vertices"

    plot_data = []

    data = load_data("../data/results_bad.json")
    plot_data.extend(iterate(data, field, 'low quality'))
    draw_figure(plot_data, 'num_vertices_bad')

    data = load_data("../data/results_good.json")
    plot_data.extend(iterate(data, field, 'high quality'))
    draw_figure(plot_data, 'num_vertices_good')


if __name__ == "__main__":
    main()
