if __name__ == "__main__":

    import argparse
    parser = argparse.ArgumentParser()
    # arguments-run
    parser.add_argument("--sim", action='store_true', help="run simulation")
    parser.add_argument("--rfc", action='store_true', help="run random forest with classification trees")
    # arguments-sim
    parser.add_argument("--earlyStop", action="store_true", help="stop sim early if either collision or ejection")
    parser.add_argument("--ejectSF", default=1.0, type=float, help="scale factor to increase or decrease ejection critera. EG: --ejectSF 0.5 means scenario will be classified as ejection if speed >= 0.5*escape speed; --ejectSF 2.0 means scenario will be classified as ejection if speed >= 2*escape speed")
    # arguments-random forest classifier
    # process args
    args = parser.parse_args()
    kwargs = args.__dict__

    # pull out run args
    sim = kwargs.pop('sim')
    rfc = kwargs.pop('rfc')

    # make a lists for each set of model arguments
    simKwargKeys = ['earlyStop', 'ejectSF']
    rfcKwargKeys = []

    # separate dictionaries
    [simKwargs, rfcKwargs] = map(lambda keys: {x: kwargs[x] for x in keys}, [simKwargKeys, rfcKwargKeys])

    # run simulation
    if sim:
        from pyFiles.Simulation import Simulation
        simInst = Simulation()
        simInst.run(**simKwargs)

    # run random forest classifier
    if rfc:
        from pyFiles.MetaModels.RFclassification import RandomForests
        rfcInst = RandomForests()
        rfcInst.run(**rfcKwargs)
