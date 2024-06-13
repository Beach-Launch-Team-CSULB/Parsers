
sensorList = [

# Node 2
["ChamberPT2",          [52, 2], [0.0196, -102.94]],
["ChamberPT1",          [50, 2], [0.0195, -128.88]],
["FuelInletPropSidePT", [58, 2], [0.0185, -125.74]],
["FuelInjectorPT",      [54, 2], [0.0196, -123.27]],
["LoxInletPropSidePT",  [60, 2], [0.0196, -128.58]],
["MVPneumaticsPT",      [56, 2], [0.0193, -125.56]],
# Node 3
["DomeRegFuelPT",   [74, 3], [0.0196, -127.95]],
["DomeRegLoxPT",    [76, 3], [0.0194, -134.95]],
["FuelTankPT1",     [62, 3], [0.0192, -125.04]],
["FuelTankPT2",     [64, 3], [0.0194, -125.08]],
["LoxTankPT1",      [66, 3], [0.0192, -122.78]],
["LoxTankPT2",      [68, 3], [0.0191, -126.90]],
["HiPressFuelPT",   [70, 3], [0.0967, -623.11]],
["HiPressLoxPT",    [72, 3], [0.0981, -630.47]],

#FAKESHIT
["FakeChamberPT1",   [150, 2], [1, 0]],
["FakeFuelLinePT",   [158, 2], [1, 0]],
["FakeLoxLinePT",    [160, 2], [1, 0]],
["FakeFuelTankPT",   [162, 3], [1, 0]],
["FakeLoxTankPT",    [166, 3], [1, 0]],
["FakeHiPressPT",    [170, 3], [1, 0]],

#LC Sensors
["ThrustMountLoadCell1", [32, 4], [1, 0]],
["ThrustMountLoadCell2", [38, 4], [1, 0]],
["ThrustMountLoadCell3", [44, 4], [1, 0]],

# Temp Sensors
["coldJunctionRenegade",   [ 99, 4], [1, 0]],
["EngineChamberWallTC",    [100, 4], [1, 0]],
["EngineThroatWallTC",     [102, 4], [1, 0]],
["EngineNozzleExitWallTC", [104, 4], [1, 0]],
["LoxTankLowerTC",         [106, 4], [1, 0]],
["LoxTankMidTC",           [108, 4], [1, 0]],
["LoxTankUpperTC",         [110, 4], [1, 0]],

# HP Channel Sensors
# Node 2
["RenegadeEngineHP1",   [121, 2], [0.0006,1.7800]],
["RenegadeEngineHP2",   [122, 2], [0.0006,1.7800]],
["RenegadeEngineHP3",   [123, 2], [0.0006,1.7800]],
["RenegadeEngineHP4",   [124, 2], [0.0006,1.7800]],
["RenegadeEngineHP5",   [125, 2], [0.0006,1.7800]],
["RenegadeEngineHP6",   [126, 2], [0.0006,1.7800]],
["RenegadeEngineHP7",   [127, 2], [0.0006,1.7800]],
["RenegadeEngineHP8",   [128, 2], [0.0006,1.7800]],
["RenegadeEngineHP9",   [129, 2], [0.0006,1.7800]],
["RenegadeEngineHP10",  [130, 2], [0.0006,1.7800]],
# Node 3
["RenegadePropHP1",     [131, 3], [0.0006,1.7800]],
["RenegadePropHP2",     [132, 3], [0.0006,1.7800]],
["RenegadePropHP3",     [133, 3], [0.0006,1.7800]],
["RenegadePropHP4",     [134, 3], [0.0006,1.7800]],
["RenegadePropHP5",     [135, 3], [0.0006,1.7800]],
["RenegadePropHP6",     [136, 3], [0.0006,1.7800]],
["RenegadePropHP7",     [137, 3], [0.0006,1.7800]],
["RenegadePropHP8",     [138, 3], [0.0006,1.7800]],
["RenegadePropHP9",     [139, 3], [0.0006,1.7800]],
["RenegadePropHP10",    [140, 3], [0.0006,1.7800]],

]

sensor_id_from_name = {s[0]:s[1][1] for s in sensorList}
sensor_name_from_id = {s[1][0]:s[0] for s in sensorList}

sensor_index_from_name = {s[0]:i    for i,s in enumerate(sensorList)}
sensor_index_from_id =   {s[1][0]:i for i,s in enumerate(sensorList)}
