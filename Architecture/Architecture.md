# Architecture

## 1. Overview

The goal of this project is to build a **modular digital twin of a desalination plant**.

The system should represent:

* Physical plant equipment
* Water and process behaviour
* Instrumentation and sensors
* Control systems
* Plant disturbances and faults
* Energy consumption
* Operating costs and revenue
* Eventually, optimization and AI

The architecture should be **modular and extensible**, so individual components can be developed, tested, replaced, and connected without rewriting the entire plant.

The core idea is:

> **Build the desalination plant as a collection of reusable modules connected by process streams.**

---

# 2. High-Level Architecture

```text
                         DESALINATION DIGITAL TWIN
                                  │
              ┌───────────────────┼───────────────────┐
              │                   │                   │
              ▼                   ▼                   ▼
        Physical Layer      Simulation Layer     Data Layer
              │                   │                   │
          CadQuery          Process Models       Plant Data
              │              Instrument Models    Sensor Data
              │              Control Models      Historical Data
              │                   │                   │
              └───────────────────┼───────────────────┘
                                  │
                                  ▼
                         Simulation Engine
                                  │
                     ┌────────────┴────────────┐
                     │                         │
                     ▼                         ▼
                Visualization             Analytics
                     │                         │
                     └────────────┬────────────┘
                                  │
                                  ▼
                           Optimization
                                  │
                                  ▼
                              AI Layer
```

The AI layer is **not part of the initial implementation**.

The first objective is to create a reliable physics-based simulation.

---

# 3. Technology Stack

## Primary Language

**Python**

Python will be used for the majority of the digital twin because it provides strong support for:

* Numerical computation
* Scientific simulation
* Data processing
* Optimization
* Machine learning
* Visualization
* APIs

## Main Libraries

| Requirement           | Technology             |
| --------------------- | ---------------------- |
| Programming           | Python                 |
| Numerical computation | NumPy                  |
| Scientific computing  | SciPy                  |
| Data processing       | Pandas                 |
| Visualization         | Matplotlib / Plotly    |
| Plant topology        | NetworkX               |
| Machine Learning      | PyTorch / Scikit-learn |
| API                   | FastAPI                |
| 3D CAD                | CadQuery               |
| Configuration         | YAML / JSON            |
| Testing               | Pytest                 |

---

# 4. System Layers

The system is divided into several layers.

```text
┌──────────────────────────────────────────────┐
│                  AI / OPTIMIZATION           │
├──────────────────────────────────────────────┤
│                 ECONOMICS                    │
├──────────────────────────────────────────────┤
│             CONTROL SYSTEM                  │
├──────────────────────────────────────────────┤
│             INSTRUMENTATION                 │
├──────────────────────────────────────────────┤
│              PROCESS MODELS                 │
├──────────────────────────────────────────────┤
│             SIMULATION ENGINE               │
├──────────────────────────────────────────────┤
│               CORE ENGINE                   │
├──────────────────────────────────────────────┤
│              PHYSICAL / CAD                 │
└──────────────────────────────────────────────┘
```

Each layer should have a clear responsibility.

---

# 5. Core Engine

The core engine provides the infrastructure required by every other component.

### Responsibilities

* Module management
* Plant topology
* Connections
* Process streams
* Simulation time
* State management
* Parameter management

### Structure

```text
core/
├── module.py
├── stream.py
├── connection.py
├── plant.py
├── simulation.py
└── state.py
```

---

# 6. WaterStream

The most important object connecting process modules is the **WaterStream**.

A WaterStream represents water moving between pieces of equipment.

Example:

```text
Intake
   │
   ▼
WaterStream
   │
   ▼
Pretreatment
   │
   ▼
WaterStream
   │
   ▼
Pump
   │
   ▼
WaterStream
   │
   ▼
RO Membrane
```

A stream should contain properties such as:

```text
Flow rate
Pressure
Temperature
Salinity / TDS
pH
Turbidity
Composition
```

Example conceptual object:

```python
WaterStream(
    flow_rate=1000,
    pressure=5,
    temperature=28,
    salinity=35000,
    ph=7.8
)
```

The exact implementation will evolve as the physical models become more detailed.

---

# 7. Process Layer

The process layer models the actual desalination plant.

```text
process/
├── intake.py
├── pretreatment.py
├── filter.py
├── chemical_dosing.py
├── pump.py
├── pipe.py
├── valve.py
├── ro.py
├── erd.py
├── tank.py
├── brine.py
└── post_treatment.py
```

## Main Process Modules

### Intake

Handles raw seawater entering the plant.

Inputs:

* Source water
* Environmental conditions

Outputs:

* Feed water

---

### Pretreatment

Represents processes used to prepare seawater for RO.

Possible modules:

* Screening
* Coagulation
* Flocculation
* DAF
* Media filtration
* UF/MF
* Cartridge filtration

---

### Pump

Models pressure increase and energy consumption.

Inputs:

* Flow
* Inlet pressure
* Pump parameters

Outputs:

* Increased pressure
* Flow

Possible parameters:

```text
Pump efficiency
Pump curve
Maximum pressure
Motor power
Speed
```

---

### Pipe

Models movement through piping.

Possible effects:

* Pressure drop
* Flow resistance
* Temperature effects

---

### Valve

Controls flow or pressure.

Parameters:

```text
Valve type
Valve opening
Flow coefficient
Pressure relationship
```

---

### RO Membrane

The RO module is one of the most important components.

It should eventually model:

* Feed pressure
* Feed flow
* Feed salinity
* Permeate flow
* Reject flow
* Salt rejection
* Recovery
* Membrane permeability
* Fouling
* Pressure drop

Conceptually:

```text
                 RO MEMBRANE
                      │
          ┌───────────┴───────────┐
          ▼                       ▼
      Permeate                  Reject
      Product                    Brine
```

---

### Energy Recovery Device

The ERD recovers energy from the high-pressure reject stream.

Inputs:

```text
Reject pressure
Reject flow
```

Outputs:

```text
Recovered energy
Adjusted feed pressure
```

---

### Post-Treatment

Processes permeate after RO.

Possible modules:

* Remineralization
* pH adjustment
* Disinfection
* Chlorination
* Final filtration

---

### Storage

Stores produced water or brine.

The tank should eventually model:

* Level
* Inflow
* Outflow
* Pressure
* Volume

---

# 8. Instrumentation Layer

Instrumentation represents the sensors installed on the physical plant.

```text
instrumentation/
├── pressure.py
├── flow.py
├── temperature.py
├── level.py
├── conductivity.py
├── differential_pressure.py
├── ph.py
├── turbidity.py
├── chlorine.py
└── vibration.py
```

Important distinction:

> A process variable is not the same thing as a sensor measurement.

For example:

```text
Actual pressure
      │
      ▼
Pressure Transmitter
      │
      ▼
Measured pressure
```

The actual pressure belongs to the process model.

The measured pressure belongs to the instrumentation model.

---

# 9. Instrument Model

Every instrument should eventually support:

```text
True value
Measured value
Accuracy
Range
Noise
Bias
Response time
Drift
Saturation
Failure state
```

For example:

```text
P_actual = 55 bar

        ↓

Pressure Transmitter

        ↓

P_measured = 54.8 bar
```

The first implementation can be extremely simple:

```text
P_measured = P_actual
```

Later:

```text
P_measured = P_actual + bias + noise
```

Eventually the model can include:

```text
P_measured =
    delayed(
        saturated(
            P_actual
            + bias
            + noise
            + drift
        )
    )
```

---

# 10. Control Layer

The control layer determines how the plant reacts to measurements.

```text
control/
├── pid.py
├── pressure_control.py
├── flow_control.py
├── level_control.py
├── ph_control.py
└── pump_control.py
```

The basic control loop is:

```text
        Setpoint
           │
           ▼
       Controller
           │
           ▼
        Actuator
           │
           ▼
       Plant Process
           │
           ▼
         Sensor
           │
           └──────────────► Controller
```

Example:

```text
Desired pressure = 60 bar

        ↓

Pressure Controller

        ↓

Pump speed

        ↓

RO pressure

        ↓

Pressure Transmitter

        ↓

Measured pressure

        └──────────────► Controller
```

---

# 11. Actuators

Actuators are different from sensors.

### Sensors

Measure the plant.

Examples:

```text
PT
FT
TT
LT
pH sensor
Conductivity sensor
```

### Actuators

Change the plant.

Examples:

```text
Pump speed
Valve opening
Chemical dosing rate
```

This distinction is important for the digital twin.

---

# 12. Simulation Engine

The simulation engine coordinates all modules.

```text
simulation/
├── engine.py
├── scheduler.py
├── solver.py
└── timestep.py
```

The simulation runs in discrete time steps.

For example:

```text
t = 0 s
t = 1 s
t = 2 s
t = 3 s
...
```

At each timestep:

```text
1. Read plant state
2. Calculate process behaviour
3. Update process variables
4. Generate sensor measurements
5. Run controllers
6. Apply actuator changes
7. Update plant state
8. Store results
```

Conceptually:

```text
             ┌───────────────┐
             │ Plant State   │
             └───────┬───────┘
                     ▼
             ┌───────────────┐
             │ Process Model │
             └───────┬───────┘
                     ▼
             ┌───────────────┐
             │   Sensors     │
             └───────┬───────┘
                     ▼
             ┌───────────────┐
             │ Controllers   │
             └───────┬───────┘
                     ▼
             ┌───────────────┐
             │   Actuators   │
             └───────┬───────┘
                     │
                     └──────────► Next timestep
```

---

# 13. Plant Topology

The plant should be represented as a graph.

Example:

```text
[INTAKE]
    │
    ▼
[PRETREATMENT]
    │
    ▼
[FILTER]
    │
    ▼
[PUMP]
    │
    ▼
[RO]
   / \
  /   \
 ▼     ▼
[PRODUCT] [BRINE]
```

Each node represents a module.

Each connection represents a WaterStream.

This allows different plant configurations to be created without changing the underlying modules.

---

# 14. Configuration-Driven Plant

The plant topology should eventually be defined through configuration rather than hard-coded Python.

Example:

```yaml
plant:
  type: SWRO

modules:

  - id: intake
    type: Intake

  - id: pretreatment
    type: Pretreatment

  - id: feed_pump
    type: Pump

  - id: ro_train
    type: RO

  - id: product_tank
    type: Tank

connections:

  - from: intake
    to: pretreatment

  - from: pretreatment
    to: feed_pump

  - from: feed_pump
    to: ro_train

  - from: ro_train
    to: product_tank
```

This means the same software can represent different desalination plants.

---

# 15. Physical / CAD Layer

The existing CadQuery work should be treated as the **physical representation** of the plant.

```text
cad/
├── intake.py
├── pretreatment.py
├── pump.py
├── ro.py
├── tank.py
└── plant.py
```

CadQuery answers:

> What does the plant physically look like?

The simulation answers:

> How does the plant behave?

These should remain separate but connected.

```text
             Plant Definition
                    │
          ┌─────────┴─────────┐
          ▼                   ▼
     CAD Model          Simulation Model
          │                   │
       CadQuery             Python
          │                   │
          └─────────┬─────────┘
                    ▼
             Digital Twin
```

---

# 16. Fault Layer

Faults should be modeled independently from the normal process models.

```text
faults/
├── sensor_fault.py
├── pump_fault.py
├── valve_fault.py
├── membrane_fouling.py
└── pipe_fault.py
```

Possible faults:

### Sensor

```text
Bias
Drift
Noise
Stuck value
Signal loss
```

### Pump

```text
Efficiency degradation
Reduced speed
Mechanical failure
```

### RO membrane

```text
Fouling
Scaling
Reduced permeability
Reduced salt rejection
```

### Valve

```text
Stuck valve
Partial opening
Actuator failure
```

This will eventually allow the digital twin to simulate abnormal plant behaviour.

---

# 17. Economics Layer

The economics layer translates plant behaviour into financial consequences.

```text
economics/
├── electricity.py
├── chemicals.py
├── maintenance.py
├── water_revenue.py
└── profit.py
```

Example:

```text
Electricity consumption
        +
Chemical consumption
        +
Maintenance
        +
Other operating costs
        │
        ▼
   Operating Cost
        │
        ▼
      Revenue
        │
        ▼
      Profit
```

The objective is eventually to answer questions such as:

> What happens to profit if RO pressure is increased by 2 bar?

---

# 18. Optimization Layer

Optimization comes after the simulation is reliable.

```text
optimization/
├── optimizer.py
├── objectives.py
├── constraints.py
└── search.py
```

Possible objectives:

```text
Maximize water production
Minimize energy consumption
Minimize operating cost
Maximize profit
Maximize recovery
Maintain water quality
Minimize membrane degradation
```

The optimizer should not directly replace the physics model.

Instead:

```text
             Candidate Configuration
                       │
                       ▼
                Physics Simulator
                       │
                       ▼
                 Plant Results
                       │
                       ▼
                   Objective
                       │
                       ▼
                   Optimizer
                       │
                       └──────► New Configuration
```

---

# 19. AI Layer

AI should be introduced only after the underlying digital twin has been validated.

Potential future applications:

### Prediction

Predict:

```text
Membrane fouling
Energy consumption
Maintenance requirements
Water production
Equipment failure
```

### Optimization

AI could search for:

```text
Pump pressure
Pump speed
Valve settings
Chemical dosage
Recovery ratio
Operating conditions
```

### Natural Language Interface

Eventually a user could ask:

> "Why did the plant's energy consumption increase?"

The system could inspect the digital twin and explain:

```text
Energy consumption increased because:

1. Feed pressure increased by 4.2 bar
2. Pump efficiency decreased by 3%
3. RO recovery decreased by 1.8%
```

The LLM should primarily act as an **interface and reasoning/explanation layer**, while numerical optimization and physics calculations remain deterministic wherever possible.

---

# 20. Complete Architecture

```text
                         USER
                          │
                          ▼
                  Visualization / API
                          │
                          ▼
                ┌────────────────────┐
                │ Digital Twin Core  │
                └─────────┬──────────┘
                          │
       ┌──────────────────┼──────────────────┐
       │                  │                  │
       ▼                  ▼                  ▼
   Process Models     Instrumentation      Control
       │                  │                  │
       └──────────────────┼──────────────────┘
                          │
                          ▼
                   Simulation Engine
                          │
             ┌────────────┼────────────┐
             │            │            │
             ▼            ▼            ▼
          Faults      Economics     Plant State
             │            │            │
             └────────────┼────────────┘
                          │
                          ▼
                    Plant Results
                          │
                          ▼
                    Optimization
                          │
                          ▼
                         AI
```

---

# 21. Proposed Repository Structure

```text
desalination-digital-twin/
│
├── README.md
├── architecture.md
├── requirements.txt
│
├── core/
│   ├── module.py
│   ├── stream.py
│   ├── connection.py
│   ├── plant.py
│   ├── state.py
│   └── simulation.py
│
├── process/
│   ├── intake.py
│   ├── pretreatment.py
│   ├── filter.py
│   ├── chemical_dosing.py
│   ├── pump.py
│   ├── pipe.py
│   ├── valve.py
│   ├── ro.py
│   ├── erd.py
│   ├── brine.py
│   ├── tank.py
│   └── post_treatment.py
│
├── instrumentation/
│   ├── base_sensor.py
│   ├── pressure.py
│   ├── flow.py
│   ├── temperature.py
│   ├── level.py
│   ├── conductivity.py
│   ├── differential_pressure.py
│   ├── ph.py
│   ├── turbidity.py
│   └── chlorine.py
│
├── control/
│   ├── controller.py
│   ├── pid.py
│   ├── pressure_control.py
│   ├── flow_control.py
│   └── level_control.py
│
├── faults/
│   ├── sensor_fault.py
│   ├── pump_fault.py
│   ├── valve_fault.py
│   └── membrane_fouling.py
│
├── economics/
│   ├── electricity.py
│   ├── chemicals.py
│   ├── maintenance.py
│   ├── revenue.py
│   └── profit.py
│
├── optimization/
│   ├── optimizer.py
│   ├── objectives.py
│   └── constraints.py
│
├── cad/
│   └── ...
│
├── visualization/
│   └── ...
│
├── tests/
│   ├── test_stream.py
│   ├── test_pump.py
│   ├── test_pressure_transmitter.py
│   └── test_ro.py
│
└── examples/
    └── simple_ro_plant.py
```

---

# 22. Development Order

The system should **not** be built all at once.

### Phase 1 — Core

Build:

```text
WaterStream
Module
Connection
Plant
Simulation Engine
```

### Phase 2 — Basic Process

Build:

```text
Pipe
Pump
Valve
Tank
RO
```

### Phase 3 — Instrumentation

Start with:

```text
Pressure Transmitter
        ↓
Flow Transmitter
        ↓
Temperature
        ↓
Differential Pressure
        ↓
Level
        ↓
Conductivity
```

Then add:

```text
pH
Turbidity
Chlorine
Vibration
```

### Phase 4 — Control

Implement:

```text
PID
Pressure control
Flow control
Level control
Pump control
```

### Phase 5 — Dynamic Simulation

Introduce:

```text
Time-dependent behaviour
Sensor delays
Process dynamics
Transient behaviour
```

### Phase 6 — Faults

Implement:

```text
Sensor faults
Pump degradation
Valve faults
Membrane fouling
```

### Phase 7 — Economics

Implement:

```text
Energy
Chemicals
Maintenance
Revenue
Profit
```

### Phase 8 — Validation

Compare simulation results against:

```text
Published models
Experimental data
Plant data
RoSIM / other established simulators
```

The model should be validated before optimization or AI is added.

### Phase 9 — Optimization

Add numerical optimization.

### Phase 10 — AI

Only after the previous layers are reliable.

---

# 23. First Prototype

The first working prototype should be intentionally small.

```text
             PUMP
               │
               │
               ▼
        Pressure Transmitter
               │
               ▼
          Measurement
```

Then expand to:

```text
             PUMP
               │
        ┌──────┴──────┐
        ▼             ▼
       PT             FT
        │             │
        └──────┬──────┘
               ▼
              RO
             /  \
            /    \
           ▼      ▼
      Permeate   Brine
```

The objective of this first prototype is **not** to simulate an entire desalination plant.

It is to prove that the architecture works.

---

# 24. Design Principles

The project should follow these principles:

### 1. Modularity

Every major physical component should be an independent module.

### 2. Separation of Concerns

Process physics, sensors, controls, economics, and AI should not be mixed together.

### 3. Reusability

A Pump module should work in multiple plant configurations.

### 4. Configuration Over Hard-Coding

Plant topology should eventually be defined through configuration.

### 5. Physics First

The physics-based simulation is the source of truth.

### 6. Validation Before Intelligence

Do not add AI to compensate for an incorrect physical model.

### 7. Expandability

The architecture should support additional desalination technologies in the future, such as:

```text
SWRO
BWRO
MED
MSF
ED/EDR
```

without requiring a complete rewrite.

---

# 25. Final Architecture Philosophy

The long-term goal is to create something closer to a **platform for building desalination plant digital twins**, rather than a single hard-coded model of one plant.

The fundamental abstraction is:

```text
              MODULE
                 │
       ┌─────────┼─────────┐
       │         │         │
     Input     State     Output
       │         │         │
       └─────────┼─────────┘
                 │
          Mathematical Model
                 │
       ┌─────────┼─────────┐
       │         │         │
   Sensors   Controllers  Faults
```

Multiple modules are connected together:

```text
Module → Stream → Module → Stream → Module
```

forming the complete plant.

The resulting system becomes:

```text
       Physical Plant
             ↕
        Digital Twin
             │
      ┌──────┼──────┐
      │      │      │
   Monitor Control Optimize
                    │
                    ▼
                   AI
```

The immediate objective is therefore:

> **Build the smallest correct module, validate it, and progressively compose modules into a complete desalination plant digital twin.**
