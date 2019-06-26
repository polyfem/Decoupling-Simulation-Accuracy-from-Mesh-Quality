### Generate Figures

To reproduce the figures in the teaser:

1. If you didn't build PolyFEM as instructed in the base README, you will need to edit `run.sh` with the path to your `PolyFEM_bin` executable;
2. You may also need to edit the part that activate the necessary conda environment;
3. Run the main script from this folder:
   ```
   ./run.sh
   ```
4. The images for the teaser will appear in the `teaser/` folder.

### Cleanup

To cleanup the generated files, run this from the current folder:

```
git clean -ffdx .
```


##### Note 1

The colors on the ground plane look slightly different in the paper. This is because the discrete colormap for element types was hardcoded into PyRenderer. More specifically, the [following lines](https://github.com/qnzhou/PyRenderer/blob/0eadbb4e94d05fcdb57287a5fb36c6b138f668c6/pyrender/color/PredefinedColorMaps.py#L1316) were replaced by

```python
    "discrete_4": {
        0.000: hex2rgb("#FFEAA7"),
        0.333: hex2rgb("#FAB1A0"),
        0.666: hex2rgb("#FF7675"),
        1.000: hex2rgb("#FD79A8"),
    },
```

##### Note 2

The lighting for the reference solution is slightly different than in the paper, since rendering a soft-shadow with a white background required a bit of hacking around PyRenderer. The solution is the same though, but with a slightly different rendering.
