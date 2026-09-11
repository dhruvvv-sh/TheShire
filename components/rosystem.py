from core import PlantComponent
from streams import WaterStream


class ROSystem(PlantComponent):
    """
    Reverse Osmosis system.

    Boundary:
        Pre-RO -> Permeate + Brine

    The RO model performs:
        - Flow split
        - Salt rejection
        - Salt mass balance
        - Pressure loss
    """

    def __init__(
        self,
        name="RO System",

        # RO operating parameters
        recovery=0.43,
        salt_rejection=0.992,

        # Hydraulic parameters
        permeate_pressure=1.5,
        membrane_pressure_loss=5.0,

        # Initial pH model parameters
        permeate_pH_drop=0.8,
        brine_pH_change=-0.1
    ):

        super().__init__(name)

        self.recovery = recovery
        self.salt_rejection = salt_rejection

        self.permeate_pressure = permeate_pressure
        self.membrane_pressure_loss = membrane_pressure_loss

        self.permeate_pH_drop = permeate_pH_drop
        self.brine_pH_change = brine_pH_change

    # ==================================================
    # FLOW MODEL
    # ==================================================

    def calculate_permeate_flow(self, feed_flow):
        """
        Qp = Qf × Recovery
        """

        return feed_flow * self.recovery

    def calculate_brine_flow(
        self,
        feed_flow,
        permeate_flow
    ):
        """
        Qb = Qf - Qp
        """

        return feed_flow - permeate_flow

    # ==================================================
    # PERMEATE SALINITY
    # ==================================================

    def calculate_permeate_salinity(self, feed_salinity):
        """
        Simplified salt passage model:

            Salt Passage = 1 - Rejection

            Cp = Cf × Salt Passage
        """

        salt_passage = 1 - self.salt_rejection

        return feed_salinity * salt_passage

    # ==================================================
    # BRINE SALINITY
    # ==================================================

    def calculate_brine_salinity(
        self,
        feed_flow,
        feed_salinity,
        permeate_flow,
        permeate_salinity,
        brine_flow
    ):
        """
        Calculate brine salinity using a salt mass balance.

            Salt in = Salt in permeate + Salt in brine
        """

        salt_in = feed_flow * feed_salinity

        salt_in_permeate = (
            permeate_flow
            * permeate_salinity
        )

        salt_in_brine = (
            salt_in
            - salt_in_permeate
        )

        if brine_flow <= 0:
            return 0

        return salt_in_brine / brine_flow

    # ==================================================
    # PRESSURE MODEL
    # ==================================================

    def calculate_brine_pressure(self, feed_pressure):
        """
        Brine pressure is the feed pressure minus
        the hydraulic pressure loss across the membrane.
        """

        return max(
            0,
            feed_pressure - self.membrane_pressure_loss
        )

    # ==================================================
    # PH MODEL
    # ==================================================

    def calculate_permeate_pH(self, feed_pH):
        """
        Initial simplified model:

            pH_permeate = pH_feed - pH_drop
        """

        return max(
            0,
            min(
                14,
                feed_pH - self.permeate_pH_drop
            )
        )

    def calculate_brine_pH(self, feed_pH):
        """
        Calculate brine pH using the configured
        concentration effect.
        """

        return max(
            0,
            min(
                14,
                feed_pH + self.brine_pH_change
            )
        )

    # ==================================================
    # MAIN PROCESS
    # ==================================================

    def process(self, water_stream):

        if not isinstance(water_stream, WaterStream):
            raise TypeError(
                "ROSystem expects a WaterStream object"
            )

        if not 0 < self.recovery < 1:
            raise ValueError(
                "RO recovery must be between 0 and 1"
            )

        if not 0 <= self.salt_rejection < 1:
            raise ValueError(
                "Salt rejection must be between 0 and 1"
            )

        # ----------------------------------------------
        # 1. FLOW SPLIT
        # ----------------------------------------------

        feed_flow = water_stream.flow

        permeate_flow = (
            self.calculate_permeate_flow(feed_flow)
        )

        brine_flow = (
            self.calculate_brine_flow(
                feed_flow,
                permeate_flow
            )
        )

        # ----------------------------------------------
        # 2. PERMEATE SALINITY
        # ----------------------------------------------

        permeate_salinity = (
            self.calculate_permeate_salinity(
                water_stream.salinity
            )
        )

        # ----------------------------------------------
        # 3. BRINE SALINITY
        # ----------------------------------------------

        brine_salinity = (
            self.calculate_brine_salinity(
                feed_flow,
                water_stream.salinity,
                permeate_flow,
                permeate_salinity,
                brine_flow
            )
        )

        # ----------------------------------------------
        # 4. PRESSURE
        # ----------------------------------------------

        permeate_pressure = (
            self.permeate_pressure
        )

        brine_pressure = (
            self.calculate_brine_pressure(
                water_stream.pressure
            )
        )

        # ----------------------------------------------
        # 5. pH
        # ----------------------------------------------

        permeate_pH = (
            self.calculate_permeate_pH(
                water_stream.pH
            )
        )

        brine_pH = (
            self.calculate_brine_pH(
                water_stream.pH
            )
        )

        # ----------------------------------------------
        # 6. CREATE PERMEATE
        # ----------------------------------------------

        permeate = water_stream.copy(
            name="Permeate",
            flow=permeate_flow,
            pressure=permeate_pressure,
            temperature=water_stream.temperature,
            salinity=permeate_salinity,
            pH=permeate_pH
        )

        # ----------------------------------------------
        # 7. CREATE BRINE
        # ----------------------------------------------

        brine = water_stream.copy(
            name="Brine",
            flow=brine_flow,
            pressure=brine_pressure,
            temperature=water_stream.temperature,
            salinity=brine_salinity,
            pH=brine_pH
        )

        return {
            "permeate": permeate,
            "brine": brine
        }