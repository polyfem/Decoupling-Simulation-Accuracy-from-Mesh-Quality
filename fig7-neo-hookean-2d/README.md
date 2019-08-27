### Generate Figures

To reproduce the images in Figure 7:

1. If you didn't build PolyFEM as instructed in the base README, you will need to edit `run.sh` with the path to your `PolyFEM_bin` executable;
2. You may also need to edit the part that activate the necessary conda environment;
3. Run the main script from this folder:
   ```
   ./run.sh
   ```
4. The images for the teaser will appear in the `fig/` folder.

### Cleanup

To cleanup the generated files, run this from the current folder:

```
git clean -ffdx .
```

##### Note

The last two jobs using only P1 elements take a very long time to run (several hours). Thus running them is disabled by default, and the result of PolyFEM is provided in this repository. Simply uncomment the lines in the script `./run.sh` to reproduce them.
