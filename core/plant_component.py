# base class for every physical unit in the desalination plant

class PlantComponent:
    """
    Base class for all desalination plant components.

    A component receives one or more water_streams,
    processes them, and produces one or more WaterStreams.
    """
    def __init__(self, name):
        self.name = name

    def process(self, water_stream):
        """
        Process an incoming WaterStream.

        Each specific plant component should override this method.
        """
        raise NotImplementedError(
            f"{self.name} must implement the process() method"
        )



"""
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