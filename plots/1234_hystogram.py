#!/usr/bin/env python
# -*- coding: utf-8 -*-

# System libs
import json
import numpy

from pandas.io.json import json_normalize

import plotly.graph_objs as go
import plotly.offline as plotly
import plotly.figure_factory as ff


colors = {'pref': 'rgb(85, 239, 196)', '1': 'rgb(255, 201, 26)', '2': 'rgb(250, 177, 160)', '3': 'rgb(255, 118, 117)', '4': 'rgb(253, 121, 168)', '5': 'rgb(232, 67, 147)'}


def get_plot_data(data, field, discr_order, is_p_ref, is_bad):
    name = "Ours" if is_p_ref else ("P" + str(discr_order))
    key = 'pref' if is_p_ref else str(discr_order)

    match = 'polyfem300' if is_bad else 'tetmesh'

    data_tmp = data.loc[(data['mesh_path'].str.contains(match)) & (data['args.use_p_ref'] == is_p_ref) & (data['discr_order'] == discr_order) & (data['solver_info.final_res_norm'] < 1e-10) & (data['num_flipped'] == 0) & (data['solver_info.num_iterations'] > 0) & (data['solver_info.num_iterations'] < 1000)]

    if field == 'time':
        time_solving = data_tmp["time_solving"]
        time_assembling_stiffness_mat = data_tmp["time_assembling_stiffness_mat"]

        if len(time_solving) <= 0:
            return []

        real_data = time_solving.values + time_assembling_stiffness_mat.values
    else:
        plot_data = data_tmp[field]
        average_edge_length = data_tmp["average_edge_length"]

        if len(plot_data) <= 0:
            return []

        if "_l" in field:
            real_data = plot_data.values / average_edge_length.values / average_edge_length.values
        else:
            real_data = plot_data.values / average_edge_length.values

    indices = numpy.random.choice(len(real_data), 300, replace=False)
    real_data = real_data[indices]

    print(len(real_data))

    return [real_data, name, colors[key]]


def iterate(data, field, is_bad):
    plot_data = []

    num_p1 = data.loc[data['discr_order'] == 1]["mesh_path"].count()
    num_p2 = data.loc[data['discr_order'] == 2]["mesh_path"].count()
    num_p3 = data.loc[data['discr_order'] == 3]["mesh_path"].count()
    num_p4 = data.loc[data['discr_order'] == 4]["mesh_path"].count()

    print("p1",num_p1/2)
    print("p2",num_p2)
    print("p3",num_p3)
    print("p4",num_p4)
    assert(num_p1 == num_p2 * 2)
    assert(num_p2 == num_p3)
    assert(num_p2 == num_p4)
    assert(num_p2 == 784)

    plot_data.append(get_plot_data(data, field, 4, False, is_bad))
    plot_data.append(get_plot_data(data, field, 3, False, is_bad))
    plot_data.append(get_plot_data(data, field, 2, False, is_bad))
    plot_data.append(get_plot_data(data, field, 1, False, is_bad))
    plot_data.append(get_plot_data(data, field, 1, True, is_bad))

    return plot_data


def load_data(path):
    with open(path, 'r') as f:
        data = json.load(f)

    return json_normalize(data)


def draw_figure(path, field, yaxis, output, is_bad):
    data = load_data(path)

    plot_data = iterate(data, field, is_bad)

    hist_data = []
    group_labels = []
    cols = []

    for d in plot_data:
        tmp = []
        for v in d[0]:
            tmp.append(min(v, 120 if field == 'time' else 7))

        hist_data.append(tmp)
        group_labels.append(d[1])
        cols.append(d[2])

    fig = ff.create_distplot(hist_data, group_labels, colors=cols, histnorm='probability', bin_size=1 if field == 'time' else .1, show_rug=True, show_curve=False)

    layout = go.Layout(
        # title=title,
        legend=dict(x=0.81, y=1),
        font=dict(
            size=24
        ),
        xaxis=dict(
            range=[0, 120 if field == 'time' else 7]
        ),
        yaxis=dict(
            range=yaxis
        )
    )

    fig['layout'].update(layout)

    if output is not None:
        plotly.plot(fig, image="svg", image_filename=output)
    else:
        plotly.plot(fig)


def main():
    numpy.random.seed(42)

    fields = ["time", "err_l2", "err_h1"]
    yaxiss = [[0, 0.25], [0, 1], [0, 1]]

    for i in range(len(fields)):
        field = fields[i]
        yaxis = yaxiss[i]

        for is_bad in [True, False]:
            output = field + ("_bad" if is_bad else "_good")
            draw_figure("../data/1234_comparison.json", field, yaxis, output, is_bad)


if __name__ == "__main__":
    main()
