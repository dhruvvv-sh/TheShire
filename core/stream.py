from dataclasses import dataclass, replace

@dataclass(frozen=True)
class WaterStream:
    """
    Represents the state of a water stream flowing through the plant.

    All values use the plant's standard units:
        flow        -> m³/h
        pressure    -> bar
        temperature -> °C
        salinity    -> mg/L
        pH          -> dimensionless
    """

    flow: float
    pressure: float
    temperature: float
    salinity: float
    pH: float
    # for future expansion, you can add more properties like turbidity, dissolved oxygen, etc.
    
    def __post_init__(self): #for validation of the properties
        if self.flow < 0:
            raise ValueError("Flow cannot be negative")

        if self.pressure < 0:
            raise ValueError("Pressure cannot be negative")

        if self.pH < 0 or self.pH > 14:
            raise ValueError("pH must be between 0 and 14")

        if self.salinity < 0:
            raise ValueError("Salinity cannot be negative")

    def with_changes(self, **changes):
        """
        Create a new WaterStream with selected properties changed.
        The original stream remains unchanged.
        """
        return replace(self, **changes)
feed_water = WaterStream(
    flow=1000,
    pressure=3,
    temperature=28,
    salinity=35000,
    pH=7.8
)
# for testing purposes, you can create a sample water stream and modify it
"""
class Pump:
    def __init__(self, name):
        self.name = name

    def process(self, stream: WaterStream):
        # Example: pump increases pressure
        return stream.with_changes(
            pressure=10
        )

feed_water = WaterStream(
    flow=1000,
    pressure=3,
    temperature=28,
    salinity=35000,
    pH=7.8
)

pump = Pump("Feed Pump")

pressurized_water = pump.process(feed_water)

print(feed_water.pressure)          # 3
print(pressurized_water.pressure)   # 10
"""