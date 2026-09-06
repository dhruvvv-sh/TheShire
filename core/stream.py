class WaterStream:
    # we will be recieving the following parameters from the sensor present
    def __init__(self,flow,pressure,temperature,salinity,pH):
        self.flow = flow
        self.pressure = pressure
        self.temperature = temperature
        self.salinity = salinity
        self.pH = pH
    
# example usage of the WaterStream class
feed_water = WaterStream(
    flow=1000,
    pressure=3,
    temperature=28,
    salinity=35000,
    pH=7.8
)
print(feed_water.flow)
print(feed_water.pressure)
print(feed_water.salinity)
'''
flow       = 1000 m³/h
pressure   = 3 bar
temperature = 28 °C
salinity   = 35000 mg/L
pH         = 7.8
'''