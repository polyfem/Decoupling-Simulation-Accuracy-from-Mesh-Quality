#!/usr/bin/env python
# -*- coding: utf-8 -*-

# System libs
import numpy
import pandas as pd


import plotly.graph_objs as go
import plotly.offline as plotly

colors = {'pref': 'rgb(85, 239, 196)', '1': 'rgb(255, 234, 167)', '2': 'rgb(250, 177, 160)', '3': 'rgb(255, 118, 117)', '4': 'rgb(253, 121, 168)', '5': 'rgb(232, 67, 147)'}


def get_plot_data(data, discr_order, is_p_ref):
    marker_shape = 'circle'
    marker_size = 6

    name = "Ours" if is_p_ref else ("P" + str(discr_order))
    key = 'pref' if is_p_ref else str(discr_order)

    xx = numpy.arange(1, len(data) + 1)
    yy = data

    if len(xx) <= 0:
        return []

    col = colors[key]

    xx, yy = zip(*sorted(zip(xx, yy))[:])

    # xx = numpy.log(xx)

    w = numpy.polyfit(xx[:], numpy.log(yy[:]), 1)
    p = numpy.poly1d(w)
    z = numpy.exp(p(xx))

    trace = go.Scatter(
        x=xx,
        y=yy,
        mode='lines+markers',
        name="{}: {:.4f}  ".format(name, w[0]),
        line=dict(color=(col)),
        marker=dict(symbol=marker_shape, size=marker_size)
    )

    fitted = go.Scatter(
        x=xx,
        y=z,
        showlegend=False,
        mode='lines',
        line=dict(dash='dash', color=(col))
    )

    return [fitted, trace]


def draw_figure(plot_data, output):
    layout = go.Layout(
        legend=dict(x=0.01, y=0.91),
        xaxis=dict(
            title="Refinements",
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
            # autorange='reversed'
        ),
        yaxis=dict(
            # title='Condition number',
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
    for prefix in ['good_', 'bad_']:
        nprefs = pd.read_csv('../data/conditioning_' + prefix + 'nprefs.csv')
        prefs = pd.read_csv('../data/conditioning_' + prefix + 'prefs.csv')

        output = prefix + "cond"

        plot_data = []
        plot_data.extend(get_plot_data(nprefs['cond'].values, 1, False))
        plot_data.extend(get_plot_data(prefs['cond'].values, 1, True))

        draw_figure(plot_data, output)


if __name__ == "__main__":
    main()
