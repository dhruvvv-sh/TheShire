from components import Intake, Pretreatment, ROSystem
from streams import WaterStream

from visualization.registry import default_parameters


def _stream_payload(stream, stream_id, source_unit, target):
    return {
        "id": stream_id,
        "name": stream.name,
        "from": source_unit,
        "to": target,
        "flow": stream.flow,
        "pressure": stream.pressure,
        "temperature": stream.temperature,
        "salinity": stream.salinity,
        "pH": stream.pH,
    }


def simulate(feed, parameters=None):
    """
    Run the live process train with the current operator inputs.

    Chain: seawater → intake → pretreatment → RO (permeate, brine)
    """
    params = default_parameters()
    if parameters:
        for unit_id, unit_params in parameters.items():
            if unit_id in params:
                params[unit_id].update(unit_params)

    source = WaterStream(
        name="Seawater",
        flow=float(feed["flow"]),
        pressure=float(feed["pressure"]),
        temperature=float(feed["temperature"]),
        salinity=float(feed["salinity"]),
        pH=float(feed["pH"]),
    )

    intake = Intake(**params["intake"])
    post_intake = intake.process(source)
    intake_loss = intake.calculate_pressure_loss()

    pretreatment = Pretreatment(**params["pretreatment"])
    pre_ro = pretreatment.process(post_intake)

    filter_resistance = pretreatment.calculate_filter_resistance()
    filtered_pressure = max(0, post_intake.pressure - filter_resistance)
    flow_loss_fraction = pretreatment.calculate_flow_loss_fraction()
    acid_effect = pretreatment.calculate_acid_dosing_effect()
    pump_rise = pretreatment.calculate_pump_pressure_rise()

    ro = ROSystem(**params["ro"])
    ro_out = ro.process(pre_ro)
    permeate = ro_out["permeate"]
    brine = ro_out["brine"]

    overall_recovery = permeate.flow / source.flow if source.flow else 0

    return {
        "streams": [
            _stream_payload(source, "seawater", None, "intake"),
            _stream_payload(post_intake, "post-intake", "intake", "pretreatment"),
            _stream_payload(pre_ro, "pre-ro", "pretreatment", "ro"),
            _stream_payload(permeate, "permeate", "ro", "product"),
            _stream_payload(brine, "brine", "ro", "reject"),
        ],
        "units": {
            "intake": {
                "diagnostics": [
                    {"id": "pressure_loss", "label": "Pressure loss", "value": intake_loss, "unit": "bar"},
                    {"id": "outlet_pressure", "label": "Outlet pressure", "value": post_intake.pressure, "unit": "bar"},
                ],
                "internals": [
                    {
                        "id": "screen",
                        "label": "Coarse screen",
                        "metrics": [
                            {"label": "ΔP", "value": intake_loss, "unit": "bar"},
                        ],
                    }
                ],
            },
            "pretreatment": {
                "diagnostics": [
                    {"id": "filter_resistance", "label": "Filter resistance", "value": filter_resistance, "unit": "bar"},
                    {"id": "filtered_pressure", "label": "Pressure after filter", "value": filtered_pressure, "unit": "bar"},
                    {"id": "flow_loss_fraction", "label": "Flow loss fraction", "value": flow_loss_fraction, "unit": ""},
                    {"id": "acid_effect", "label": "Acid ΔpH", "value": acid_effect, "unit": ""},
                    {"id": "pump_pressure_rise", "label": "HPP rise", "value": pump_rise, "unit": "bar"},
                    {"id": "pre_ro_pressure", "label": "Pre-RO pressure", "value": pre_ro.pressure, "unit": "bar"},
                ],
                "internals": [
                    {
                        "id": "filter",
                        "label": "Media / cartridge filter",
                        "metrics": [
                            {"label": "Resistance", "value": filter_resistance, "unit": "bar"},
                            {"label": "P after filter", "value": filtered_pressure, "unit": "bar"},
                            {"label": "Flow lost", "value": flow_loss_fraction * 100, "unit": "%"},
                        ],
                    },
                    {
                        "id": "dosing",
                        "label": "Chemical dosing",
                        "metrics": [
                            {"label": "ΔpH", "value": acid_effect, "unit": ""},
                            {"label": "Outlet pH", "value": pre_ro.pH, "unit": ""},
                        ],
                    },
                    {
                        "id": "hpp",
                        "label": "High-pressure pump",
                        "metrics": [
                            {"label": "Rise", "value": pump_rise, "unit": "bar"},
                            {"label": "Pre-RO P", "value": pre_ro.pressure, "unit": "bar"},
                        ],
                    },
                ],
            },
            "ro": {
                "diagnostics": [
                    {"id": "recovery", "label": "Recovery", "value": ro.recovery, "unit": ""},
                    {"id": "salt_rejection", "label": "Salt rejection", "value": ro.salt_rejection, "unit": ""},
                    {"id": "permeate_flow", "label": "Permeate flow", "value": permeate.flow, "unit": "m³/h"},
                    {"id": "brine_flow", "label": "Brine flow", "value": brine.flow, "unit": "m³/h"},
                    {"id": "permeate_salinity", "label": "Permeate salinity", "value": permeate.salinity, "unit": "mg/L"},
                    {"id": "brine_salinity", "label": "Brine salinity", "value": brine.salinity, "unit": "mg/L"},
                ],
                "internals": [
                    {
                        "id": "membranes",
                        "label": "RO membranes",
                        "metrics": [
                            {"label": "Recovery", "value": ro.recovery * 100, "unit": "%"},
                            {"label": "Rejection", "value": ro.salt_rejection * 100, "unit": "%"},
                        ],
                    }
                ],
            },
        },
        "kpis": [
            {"id": "overall_recovery", "label": "Plant recovery", "value": overall_recovery * 100, "unit": "%"},
            {"id": "product_flow", "label": "Permeate flow", "value": permeate.flow, "unit": "m³/h"},
            {"id": "product_salinity", "label": "Permeate salinity", "value": permeate.salinity, "unit": "mg/L"},
            {"id": "pre_ro_pressure", "label": "RO feed pressure", "value": pre_ro.pressure, "unit": "bar"},
        ],
    }
