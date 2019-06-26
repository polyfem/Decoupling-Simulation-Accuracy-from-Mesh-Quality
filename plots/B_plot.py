#!/usr/bin/env python
# -*- coding: utf-8 -*-

# System libs
import json
import colorsys
import numpy

from pandas.io.json import json_normalize


import plotly.graph_objs as go
import plotly.offline as plotly

colors = {'pref': 'rgb(85, 239, 196)', '1': 'rgb(255, 234, 167)', '2': 'rgb(250, 177, 160)', '3': 'rgb(255, 118, 117)', '4': 'rgb(253, 121, 168)', '5': 'rgb(232, 67, 147)'}


def get_plot_data(pattern, data, quality, xlabel, ylabel, discr_order, is_p_ref, B):
    marker_shape = 'circle'
    marker_size = 6

    name = ("Ours B=" + str(B)) if is_p_ref else ("P" + str(discr_order))
    key = 'pref' if is_p_ref else str(discr_order)

    if is_p_ref:
        xx = data.loc[data['args.use_p_ref'] & data['args.mesh'].str.contains(pattern)][xlabel]

        if ylabel == 'time_solving':
            time_solving = data.loc[data['args.use_p_ref'] & data['args.mesh'].str.contains(pattern)]["time_solving"].values
            time_building_basis = data.loc[data['args.use_p_ref'] & data['args.mesh'].str.contains(pattern)]["time_building_basis"].values
            time_assembling_stiffness_mat = data.loc[data['args.use_p_ref'] & data['args.mesh'].str.contains(pattern)]["time_assembling_stiffness_mat"].values

            yy = time_solving + time_building_basis + time_assembling_stiffness_mat
        else:
            yy = data.loc[data['args.use_p_ref'] & data['args.mesh'].str.contains(pattern)][ylabel].values

    else:
        xx = data.loc[(numpy.logical_not(data['args.use_p_ref'])) & (data['discr_order'] == discr_order) & data['args.mesh'].str.contains(pattern)][xlabel]

        if ylabel == 'time_solving':
            time_solving = data.loc[(numpy.logical_not(data['args.use_p_ref'])) & data['args.mesh'].str.contains(pattern)]["time_solving"].values
            time_building_basis = data.loc[(numpy.logical_not(data['args.use_p_ref'])) & data['args.mesh'].str.contains(pattern)]["time_building_basis"].values
            time_assembling_stiffness_mat = data.loc[(numpy.logical_not(data['args.use_p_ref'])) & data['args.mesh'].str.contains(pattern)]["time_assembling_stiffness_mat"].values

            yy = time_solving + time_building_basis + time_assembling_stiffness_mat
        else:
            yy = data.loc[(numpy.logical_not(data['args.use_p_ref'])) & data['args.mesh'].str.contains(pattern)][ylabel].values

    if len(xx) <= 0:
        return []

    if is_p_ref:
        cc = colorsys.rgb_to_hls(85 / 255, 239 / 255, 196 / 255)
        cc1 = (B - 1.5) / 2.5 / 2 + 0.1
        cc = colorsys.hls_to_rgb(cc[0], cc1, cc[2])
        col = 'rgb(' + str(cc[0] * 255) + ',' + str(cc[1] * 255) + ',' + str(cc[2] * 255) + ')'
    else:
        col = colors[key]

    tmp = xx
    xx = []
    for s in tmp:
        s = s.replace("/beegfs/work/panozzo/p_ref/bunny_screw_sequence/", "").replace("/Users/teseo/Desktop/download/meshes/B/meshes/", "").replace("mesh", "msh")
        val = quality[s]
        print(s, val['avg'])
        xx.append(val['avg'])

    xx, yy = zip(*sorted(zip(xx, yy))[1:])


    trace = go.Scatter(
        x=xx,
        y=yy,
        mode='lines+markers',
        name=name,
        line=dict(color=(col)),
        marker=dict(symbol=marker_shape, size=marker_size)
    )

    return [trace]


def iterate(pattern, data, xx, xlabel, ylabel, B):
    plot_data = []

    plot_data.extend(get_plot_data(pattern, data, xx, xlabel, ylabel, 1, True, B))

    return plot_data


def load_data(path):
    with open(path, 'r') as f:
        data = json.load(f)

    return json_normalize(data)


def draw_figure(pattern, quality_file, ylabel, output):
    xlabel = "args.mesh"
    plot_data = []

    with open(quality_file, 'r') as f:
        quality = json.load(f)

    Bs = reversed([1.5, 2, 2.5, 3, 3.5, 4])

    for B in Bs:
        path = "../data/B_data_all_" + str(B) + ".json"
        data = load_data(path)
        plot_data.extend(iterate(pattern, data, quality, xlabel, ylabel, B))

    B = 3
    path = "../data/B_data_all_" + str(B) + ".json"
    data = load_data(path)
    plot_data.extend(get_plot_data(pattern, data, quality, xlabel, ylabel, 1, False, B))

    layout = go.Layout(
        legend=dict(x=0.01, y=0.91),
        xaxis=dict(
            title="Mesh quality",
            # tickformat='.1e',
            exponentformat='power',
            showticksuffix='all',
            showtickprefix='all',
            showexponent='all',
            # type='log',
            # autotick=True,
            nticks=5,
            # tickangle=45,
            # ticks='outside',
            tickfont=dict(
                size=16
            ),
            autorange='reversed'
        ),
        yaxis=dict(
            title=ylabel.replace("_", " ").title(),
            # tickformat='.1e',
            exponentformat='power',
            ticks='',
            # showticksuffix='none',
            # showtickprefix='none',
            # showexponent='all',
            tick0=0,
            dtick=1,
            # tickangle=-45,
            tickfont=dict(
                size=16
            ),
            type='log',
            anchor='y2',
            autorange=True
        ),
        font=dict(
            size=24
        ),
        hovermode='closest'
    )

    fig = go.Figure(data=plot_data, layout=layout)
    if output is not None:
        plotly.plot(fig, image="svg", image_filename=output)
    else:
        plotly.plot(fig)


def main():
    patterns = ["/Users/teseo/Desktop/download/meshes/B/meshes/bunny.msh", "/Users/teseo/Desktop/download/meshes/B/meshes/371103_polyfem.msh"]
    quality_files = ["../data/B_bunny_quality.json", "../data/B_screw_quality.json"]
    names = ["bunny", "screw"]

    for i in range(len(patterns)):
        pattern = patterns[i]
        quality_file = quality_files[i]
        name = names[i]

        for y_label in ["time_solving", "err_l2"]:
            draw_figure(pattern, quality_file, y_label, y_label + "_" + name)


if __name__ == "__main__":
    main()
