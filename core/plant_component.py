class PlantComponent:
    """
    Base class for all physical desalination plant components.
    """

    def __init__(self, name):
        self.name = name

    def process(self, water_stream):
        """
        Process an incoming WaterStream.

        Each physical component must implement this.
        """
        raise NotImplementedError(
            f"{self.__class__.__name__} must implement process()"
        )

    def __repr__(self):
        return f"{self.__class__.__name__}(name='{self.name}')"