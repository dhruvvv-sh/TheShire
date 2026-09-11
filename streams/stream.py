class WaterStream:
    """
    Represents a water stream flowing through the desalination plant.

    Units:
        flow        -> m3/h
        pressure    -> bar
        temperature -> °C
        salinity    -> mg/L
        pH          -> dimensionless
    """

    def __init__(
        self,
        name,
        flow,
        pressure,
        temperature,
        salinity,
        pH
    ):
        self.name = name
        self.flow = flow
        self.pressure = pressure
        self.temperature = temperature
        self.salinity = salinity
        self.pH = pH

    def copy(self, name=None, **changes):
        """
        Create a new WaterStream using the current stream
        as the base and applying calculated changes.
        """

        return WaterStream(
            name=name if name is not None else self.name,
            flow=changes.get("flow", self.flow),
            pressure=changes.get("pressure", self.pressure),
            temperature=changes.get("temperature", self.temperature),
            salinity=changes.get("salinity", self.salinity),
            pH=changes.get("pH", self.pH)
        )

    def __repr__(self):
        return (
            f"WaterStream("
            f"name='{self.name}', "
            f"flow={self.flow:.2f} m3/h, "
            f"pressure={self.pressure:.2f} bar, "
            f"temperature={self.temperature:.2f} °C, "
            f"salinity={self.salinity:.2f} mg/L, "
            f"pH={self.pH:.2f}"
            f")"
        )