from stream import WaterStream


class PlantComponent:
    """
    Base class for every physical unit in the desalination plant.
    """

    def __init__(self, name: str):
        self.name = name

    def process(self, water_stream: WaterStream):
        """
        Transform the incoming WaterStream.

        Subclasses must implement this method.
        """
        raise NotImplementedError(
            f"{self.name} must implement the process() method"
        )

# example of a specific plant component, Pretreatment, which inherits from PlantComponent
"""
class Pretreatment(PlantComponent):

    def process(self, water_stream: WaterStream):
        return water_stream.with_changes(
            temperature=5
        )

- # output : WaterStream(flow=1000, pressure=3, temperature=5, salinity=35000, pH=7.8)

point of this ->

                 WaterStream
                      │
                      ▼
              PlantComponent
                      │
          ┌───────────┼───────────┐
          ▼           ▼           ▼
    Pretreatment    ROUnit    PostTreatment
          │           │
          │       ┌───┴───┐
          │       ▼       ▼
          │   Permeate  Brine
          │
          ▼
    WaterStream
"""