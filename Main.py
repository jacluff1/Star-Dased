if __name__ == "__main__":

    import argparse
    parser = argparse.ArgumentParser()

    # arguments-run
    parser.add_argument("--sim", action='store_true', help="run simulation")
    parser.add_argument("--plot3Dpos", action='store_true', help="plot static 3d position plot")
    parser.add_argument("--anim", action='store_true', help="make animation that shows sim progression on the X-Y, Y-Z, and X-Z planes")
    parser.add_argument("--rfc", action='store_true', help="run random forest with classification trees")

    # arguments-sim
    parser.add_argument("--earlyStop", action="store_true", help="stop sim early if either collision or ejection")
    parser.add_argument("--ejectSF", default=1.0, type=float, help="scale factor to increase or decrease ejection critera. EG: --ejectSF 0.5 means scenario will be classified as ejection if speed >= 0.5*escape speed; --ejectSF 2.0 means scenario will be classified as ejection if speed >= 2*escape speed")

    # exploratory data analysis
    parser.add_argument("--eda", action='store_true', help="plot exploratory data analysis figures.")

    # arguments-3D position plot
    parser.add_argument('--sampleRowIdx', default=0, type=int, help="select the scenario you wish to plot 3D positions IOR make animation for (default = 0)")
    parser.add_argument("--timeIdx", help="select either initial time (0), or final time (-1); can be entered either as int or str")

    # arguments-animation

    # arguments-random forest classifier

    # process args
    args = parser.parse_args()
    kwargs = args.__dict__

    # pull out run args
    sim = kwargs.pop('sim')
    eda = kwargs.pop('eda')
    plot3Dpos = kwargs.pop('plot3Dpos')
    anim = kwargs.pop('anim')
    rfc = kwargs.pop('rfc')

    # make a lists for each set of model arguments
    simKwargKeys = ['earlyStop', 'ejectSF']
    edaKeys = []
    posPlotKeys = ['sampleRowIdx', 'timeIdx']
    animKeys = ['sampleRowIdx']
    rfcKwargKeys = []

    # separate dictionaries
    [simKwargs, edaKwargs, posPlotKwargs, animKwargs, rfcKwargs] = map(lambda keys: {x: kwargs[x] for x in keys}, [simKwargKeys, edaKeys, posPlotKeys, animKeys, rfcKwargKeys])

    # run simulation
    if sim:
        from pyFiles.Simulation import Simulation
        simInst = Simulation()
        simInst.run(**simKwargs)

    # exploratory analysis
    if eda:
        import pyFiles.explore_data.py

    # plot static 3d positions
    if plot3Dpos:
        from pyFiles.Plots import staticPositionPlot
        staticPositionPlot(**posPlotKwargs)

    # make animation .mp4 file
    if anim:
        from pyFiles.Plots import scenarioAnimation
        scenarioAnimation(**animKwargs)

    # run random forest classifier
    if rfc:
        from pyFiles.MetaModels.RFclassification import RandomForests
        rfcInst = RandomForests()
        rfcInst.run(**rfcKwargs)
