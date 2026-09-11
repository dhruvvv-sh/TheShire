from core import PlantComponent
from streams import WaterStream


class Intake(PlantComponent):
    """
    Intake and coarse screening stage.

    Boundary:
        Raw Ocean Water -> Post-Intake

    The intake introduces a configurable hydraulic pressure loss.
    """

    def __init__(self,name="Intake",intake_pressure_loss=0.5):
        super().__init__(name)

        # Hardcoded model parameter for now.
        # Later this can come from a sensor/model/configuration.
        self.intake_pressure_loss = intake_pressure_loss

    def calculate_pressure_loss(self):
        """
        Calculate pressure loss caused by the intake.

        Currently the loss is represented by a configurable
        model parameter.
        """

        return self.intake_pressure_loss

    def process(self, water_stream):

        if not isinstance(water_stream, WaterStream):
            raise TypeError(
                "Intake expects a WaterStream object"
            )

        pressure_loss = self.calculate_pressure_loss()

        output_pressure = max(0,water_stream.pressure - pressure_loss)

        return water_stream.copy(
            name="Post-Intake",
            pressure=output_pressure
        )


