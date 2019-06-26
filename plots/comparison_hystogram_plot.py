#!/usr/bin/env python
# -*- coding: utf-8 -*-

# System libs
import json
import argparse
# import scipy.stats

from pandas.io.json import json_normalize

import plotly.graph_objs as go
import plotly.offline as plotly
import plotly.figure_factory as ff


colors = {'pref': 'rgb(85, 239, 196)', '1': 'rgb(255, 201, 26)', '2': 'rgb(250, 177, 160)', '3': 'rgb(255, 118, 117)', '4': 'rgb(253, 121, 168)', '5': 'rgb(232, 67, 147)'}


def get_plot_data(data, unique_meshes, field, discr_order, is_p_ref):
    name = "Ours" if is_p_ref else ("P" + str(discr_order))
    key = 'pref' if is_p_ref else str(discr_order)

    data_tmp = data.loc[data['mesh_path'].isin(unique_meshes) & (data['args.use_p_ref'] == is_p_ref) & (data['discr_order'] == discr_order) & (data['solver_info.final_res_norm'] < 1e-8) & (data['num_flipped'] == 0) & (data['solver_info.num_iterations'] > 0) & (data['solver_info.num_iterations'] < 1000)]
    badd = data.loc[(data['mesh_path'].isin(unique_meshes) & (data['args.use_p_ref'] == is_p_ref) & (data['discr_order'] == discr_order)) & ((data['solver_info.final_res_norm'] > 1e-8) | (data['solver_info.num_iterations'] <= 0) | (data['solver_info.num_iterations'] >= 1000))]

    print(badd['mesh_path'].values)

    if field == 'time':
        time_solving = data_tmp["time_solving"].values
        time_building_basis = data_tmp["time_building_basis"].values
        time_assembling_stiffness_mat = data_tmp["time_assembling_stiffness_mat"].values

        real_data = time_solving + time_assembling_stiffness_mat + time_building_basis

        if len(real_data) <= 0:
            return []
    else:
        plot_data = data_tmp[field]
        average_edge_length = data_tmp["average_edge_length"]
        # average_edge_length = data_tmp["mesh_size"]

        # 159695 screw intersection
        # 236922 totem
        # 839723 screw
        # 931901 apple 2 pieces
        # 1368061 rock/cave
        # 815484 sphere
        # 815486 apple
        screw_data = data_tmp.loc[data['mesh_path'].str.contains("159695") | data['mesh_path'].str.contains("236922") | data['mesh_path'].str.contains("839723") | data['mesh_path'].str.contains("931901") | data['mesh_path'].str.contains("1368061") | data['mesh_path'].str.contains("815484") | data['mesh_path'].str.contains("815486")]

        print(screw_data['mesh_path'].values)

        screw_val = screw_data[field]
        screw_average_edge_length = screw_data["average_edge_length"]


        if len(plot_data) <= 0:
            return []

        if "_l" in field:
            real_data = plot_data.values / average_edge_length.values / average_edge_length.values
            screw_data = screw_val.values / screw_average_edge_length.values / screw_average_edge_length.values
        else:
            real_data = plot_data.values / average_edge_length.values
            screw_data = screw_val.values / screw_average_edge_length.values

        print(("Ours" if is_p_ref else "P1"), screw_data)


    print("n data " + str(len(real_data)))
    # print(real_data)

    # if is_p_ref:
    #     print(data_tmp.loc[data_tmp["num_p4"] > 0]['mesh_path'].values)

    # if is_p_ref:
    #     for index in range(len(real_data)):
    #         if real_data[index] > 7:
    #             print(real_data[index], plot_data.values[index], average_edge_length.values[index])
    #         index = index + 1

    return [real_data, name, colors[key]]


def iterate(data, field):
    plot_data = []
    has_p3 = data.loc[data['discr_order'] == 3]["mesh_path"].count()
    unique_meshes = data.groupby('mesh_path').filter(lambda x: len(x) == (4 if has_p3 else 2))['mesh_path']
    print(len(unique_meshes))
    print(len(data))
    # unique_meshes = pandas.Series(list(set(qualities).intersection(set(unique_meshes))))

    plot_data.append(get_plot_data(data, unique_meshes, field, 1, True))
    plot_data.append(get_plot_data(data, unique_meshes, field, 1, False))
    
    return plot_data


def load_data(path):
    with open(path, 'r') as f:
        data = json.load(f)

    return json_normalize(data)


def draw_figure(path, field, yrange, output):
    data = load_data(path)

    plot_data = iterate(data, field)

    hist_data = []
    group_labels = []
    cols = []

    for d in plot_data:
        tmp = []
        for v in d[0]:
            tmp.append(min(v, 80 if field == 'time' else 7))

        hist_data.append(tmp)
        group_labels.append(d[1])
        cols.append(d[2])

    fig = ff.create_distplot(hist_data, group_labels, colors=cols, histnorm='probability', bin_size=0.6 if field == 'time' else .05, show_rug=True)

    layout = go.Layout(
        # title=title,
        legend=dict(x=0.81, y=1),
        # title='Styled Scatter',
        xaxis=dict(
            range=[0, 80 if field == 'time' else 7]
        ),
        yaxis=dict(
            range=yrange
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

    fig['layout'].update(layout)
    # fig['layout']['yaxis']['tickformat'] = ('%')

    # fig = go.Figure(data=plot_data, layout=layout)
    if output is not None:
        plotly.plot(fig, image="svg", image_filename=output)
    else:
        plotly.plot(fig)


def parse_args():
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("-o", "--output", type=str, default=None, help="output file name")
    return parser.parse_args()


def main():
    fields = ["err_l2", "err_h1", "time"]
    yranges = [[0, 0.52], [0, 0.15], [0, 0.15]]


    for i in range(len(fields)):
        field = fields[i]
        yrange = yranges[i]

        name = "3d_" + ("time_solving" if field == "time" else field)

        draw_figure("../data/results_good.json", field, yrange, name)
        draw_figure("../data/results_bad.json", field, yrange, name + "_bad")



    datasets = ["cgal_no_features", "cgal_implicit", "cgal", "tetgen", "tetwild"]
    fields = ["err_l2", "time"]
    yranges = [[0, 0.5], [0, 0.15]]

    for dataset in datasets:
        for i in range(len(fields)):
            field = fields[i]
            yrange = yranges[i]

            draw_figure("../data/data_" + dataset + ".json", field, yrange, field + "_" + dataset)


if __name__ == "__main__":
    main()
