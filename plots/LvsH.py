#!/usr/bin/env python
# -*- coding: utf-8 -*-

# System libs
import json
import numpy

from pandas.io.json import json_normalize


import plotly.graph_objs as go
import plotly.offline as plotly

colors = {'pref': 'rgb(85, 239, 196)', '1': 'rgb(255, 201, 26)', '2': 'rgb(250, 177, 160)', '3': 'rgb(255, 118, 117)', '4': 'rgb(253, 121, 168)', '5': 'rgb(232, 67, 147)'}


def get_plot_data(data, discr_order, is_p_ref, is_h1):
    marker_shape = 'circle'
    marker_size = 6

    data_tmp = data.loc[data['args.use_p_ref'] == is_p_ref]
    xx = data_tmp["sigma_avg"].values

    if is_h1:
        yy = data_tmp["err_h1"].values
    else:
        yy = data_tmp["err_l2"].values

    to_sort = []
    meshes = data_tmp["args.mesh"]
    for s in meshes:
        s = s.replace("../meshes/large_angle_strip_", "").replace("/Users/teseo/Desktop/sigasia/teaser/meshes/large_angle_strip_", "").replace(".obj", "")
        to_sort.append(int(s))

    # _, xx = zip(*sorted(zip(to_sort, xx))[:])
    # to_sort, yy = zip(*sorted(zip(to_sort, yy))[:])
    xx, yy = zip(*sorted(zip(xx, yy))[3:-2])

    w = numpy.polyfit(numpy.log(xx[:]), numpy.log(yy[:]), 1)
    p = numpy.poly1d(w)
    z = numpy.exp(p(numpy.log(xx)))


    # xx = numpy.square(xx)
    # yy = numpy.log10(yy)
    print(xx)
    print(yy)

    print("slope",w[0])

    trace = go.Scatter(
        x=xx,
        y=yy,
        mode='lines+markers',
        name="Error: {:.4f}  ".format(abs(w[0])),
        line=dict(color='rgb(255, 201, 26)'),
        marker=dict(symbol=marker_shape, size=marker_size)
    )

    fitted = go.Scatter(
        x=xx,
        y=z,
        showlegend=False,
        mode='lines',
        line=dict(dash='dash', color=('rgb(255, 201, 26)'))
    )

    return [trace, fitted]


def load_data(path):
    with open(path, 'r') as f:
        data = json.load(f)

    return json_normalize(data)


def draw_figure(is_p_ref, is_h1, output):
    path = "../data/LvsH.json"
    data = load_data(path)

    plot_data = get_plot_data(data, 1, is_p_ref, is_h1)

    layout = go.Layout(
        legend=dict(x=0.81, y=0.91),
        xaxis=dict(
            title="sigma",
            # tickformat='.1e',
            exponentformat='power',
            showticksuffix='all',
            showtickprefix='all',
            showexponent='all',
            type='log',
            # autotick=True,
            nticks=5,
            # tickangle=45,
            # ticks='outside',
            tickfont=dict(
                size=16
            ),
            # autorange='reversed'
        ),
        yaxis=dict(
            title="H1" if is_h1 else "L2",
            exponentformat='power',
            showticksuffix='all',
            showtickprefix='all',
            showexponent='all',
            type='log',
            # autotick=True,
            nticks=5,
            # tickangle=45,
            # ticks='outside',
            tickfont=dict(
                size=16
            ),
            # range=[0.0, 0.3]
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
    draw_figure(False, False, "bound_l2")
    draw_figure(False, True, "bound_h1")


if __name__ == "__main__":
    main()
