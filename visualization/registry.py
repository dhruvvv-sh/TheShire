"""
Plant topology and parameter schemas for the operator UI.

To add a process module later:
  1. Implement it under components/
  2. Register its parameters and node here
  3. Wire it into visualization/simulate.py
The UI reads this registry and does not hard-code unit lists.
"""

STREAM_PROPERTIES = [
    {"id": "flow", "label": "Flow", "unit": "m³/h", "digits": 2},
    {"id": "pressure", "label": "Pressure", "unit": "bar", "digits": 2},
    {"id": "temperature", "label": "Temperature", "unit": "°C", "digits": 1},
    {"id": "salinity", "label": "Salinity", "unit": "mg/L", "digits": 1},
    {"id": "pH", "label": "pH", "unit": "", "digits": 2},
]

FEED_DEFAULTS = {
    "flow": 1000.0,
    "pressure": 3.0,
    "temperature": 28.0,
    "salinity": 35000.0,
    "pH": 7.8,
}

FEED_PARAMETERS = [
    {"id": "flow", "label": "Flow", "unit": "m³/h", "min": 100, "max": 5000, "step": 10, "default": 1000.0},
    {"id": "pressure", "label": "Pressure", "unit": "bar", "min": 0.5, "max": 10, "step": 0.1, "default": 3.0},
    {"id": "temperature", "label": "Temperature", "unit": "°C", "min": 5, "max": 40, "step": 0.5, "default": 28.0},
    {"id": "salinity", "label": "Salinity", "unit": "mg/L", "min": 5000, "max": 50000, "step": 100, "default": 35000.0},
    {"id": "pH", "label": "pH", "unit": "", "min": 6.0, "max": 8.5, "step": 0.05, "default": 7.8},
]

UNITS = [
    {
        "id": "intake",
        "label": "Intake",
        "short": "INT",
        "status": "live",
        "summary": "Coarse screening and hydraulic loss from the ocean intake.",
        "class_name": "Intake",
        "parameters": [
            {
                "id": "intake_pressure_loss",
                "label": "Intake pressure loss",
                "unit": "bar",
                "min": 0,
                "max": 3,
                "step": 0.05,
                "default": 0.5,
            },
        ],
        "internals": [
            {"id": "screen", "label": "Coarse screen", "detail": "Removes debris before the process train."},
        ],
    },
    {
        "id": "pretreatment",
        "label": "Pretreatment",
        "short": "PT",
        "status": "live",
        "summary": "Filtration, acid dosing, and high-pressure pumping ahead of RO.",
        "class_name": "Pretreatment",
        "parameters": [
            {"id": "filter_age", "label": "Filter age", "unit": "days", "min": 0, "max": 365, "step": 1, "default": 30},
            {
                "id": "base_filter_resistance",
                "label": "Base filter resistance",
                "unit": "bar",
                "min": 0,
                "max": 2,
                "step": 0.05,
                "default": 0.5,
            },
            {
                "id": "resistance_age_factor",
                "label": "Resistance age factor",
                "unit": "bar/day",
                "min": 0,
                "max": 0.1,
                "step": 0.005,
                "default": 0.02,
            },
            {
                "id": "base_flow_loss",
                "label": "Base flow loss",
                "unit": "fraction",
                "min": 0,
                "max": 0.08,
                "step": 0.005,
                "default": 0.01,
            },
            {
                "id": "flow_loss_age_factor",
                "label": "Flow-loss age factor",
                "unit": "1/day",
                "min": 0,
                "max": 0.001,
                "step": 0.00005,
                "default": 0.0002,
            },
            {
                "id": "acid_dosing_factor",
                "label": "Acid dosing factor",
                "unit": "ΔpH / rate",
                "min": 0,
                "max": 2,
                "step": 0.05,
                "default": 0.5,
            },
            {
                "id": "dosing_rate",
                "label": "Dosing rate",
                "unit": "",
                "min": 0,
                "max": 2,
                "step": 0.05,
                "default": 1.0,
            },
            {
                "id": "pump_pressure_rise",
                "label": "HPP pressure rise",
                "unit": "bar",
                "min": 0,
                "max": 80,
                "step": 0.5,
                "default": 58.0,
            },
        ],
        "internals": [
            {
                "id": "filter",
                "label": "Media / cartridge filter",
                "detail": "Pressure drop grows with filter age; a small flow fraction is lost to backwash.",
            },
            {
                "id": "dosing",
                "label": "Chemical dosing",
                "detail": "Acid dose lowers pH before the membranes.",
            },
            {
                "id": "hpp",
                "label": "High-pressure pump",
                "detail": "Raises filtered water to RO feed pressure.",
            },
        ],
    },
    {
        "id": "ro",
        "label": "RO system",
        "short": "RO",
        "status": "live",
        "summary": "Splits pre-RO feed into permeate and brine with salt rejection.",
        "class_name": "ROSystem",
        "parameters": [
            {"id": "recovery", "label": "Recovery", "unit": "fraction", "min": 0.15, "max": 0.6, "step": 0.01, "default": 0.43},
            {
                "id": "salt_rejection",
                "label": "Salt rejection",
                "unit": "fraction",
                "min": 0.90,
                "max": 0.999,
                "step": 0.001,
                "default": 0.992,
            },
            {
                "id": "permeate_pressure",
                "label": "Permeate pressure",
                "unit": "bar",
                "min": 0.5,
                "max": 5,
                "step": 0.1,
                "default": 1.5,
            },
            {
                "id": "membrane_pressure_loss",
                "label": "Membrane pressure loss",
                "unit": "bar",
                "min": 0,
                "max": 15,
                "step": 0.5,
                "default": 5.0,
            },
            {
                "id": "permeate_pH_drop",
                "label": "Permeate pH drop",
                "unit": "",
                "min": 0,
                "max": 2,
                "step": 0.05,
                "default": 0.8,
            },
            {
                "id": "brine_pH_change",
                "label": "Brine pH change",
                "unit": "",
                "min": -1,
                "max": 1,
                "step": 0.05,
                "default": -0.1,
            },
        ],
        "internals": [
            {"id": "membranes", "label": "RO membranes", "detail": "Water flux through the membrane; salt is mostly rejected."},
        ],
    },
]


def default_parameters():
    return {
        unit["id"]: {param["id"]: param["default"] for param in unit["parameters"]}
        for unit in UNITS
    }


def plant_descriptor():
    return {
        "id": "swro-prototype",
        "name": "SWRO prototype",
        "description": "Ocean intake, pretreatment, and reverse osmosis. Additional units register here as they are built.",
        "stream_properties": STREAM_PROPERTIES,
        "feed": {
            "label": "Seawater feed",
            "parameters": FEED_PARAMETERS,
            "defaults": FEED_DEFAULTS,
        },
        "units": UNITS,
        "default_parameters": default_parameters(),
    }
