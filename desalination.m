%% SIMPLE SWRO DESALINATION PLANT MODEL
% A beginner-friendly, steady-state MATLAB model.
% Save as: Simple_SWRO_Plant_Model.m
%
% Model sequence:
% Seawater -> DAF -> DMF -> Cartridge Filter -> UF -> RO -> Product + Brine
%                                                        |
%                                                        -> ERD energy estimate
%
% IMPORTANT:
% This is a simplified engineering prototype, NOT a validated digital twin.
% Assumptions are grouped below so they can be replaced with plant data.
% Pretreatment removes suspended solids, not dissolved salt (TDS).
% RO salt balance is calculated from feed, product and brine streams.

clear;
clc;

%% ============================================================
% 1. USER-EDITABLE INPUTS AND ASSUMPTIONS
% =============================================================

% Raw seawater reference conditions
S.raw.flow_m3h = 4213;          % seawater flow (m^3/h)
S.raw.TDS_mgL = 34458;          % total dissolved solids (mg/L)
S.raw.TSS_mgL = 25;             % ASSUMPTION: suspended solids (mg/L)
S.raw.temperature_C = 25;       % temperature (deg C)
S.raw.pressure_bar = 0.4;       % intake pressure (bar)

% Pretreatment solids removal assumptions (fractions between 0 and 1)
S.DAF.TSS_removal = 0.70;       % ASSUMPTION: 70% TSS removal
S.DAF.water_loss_fraction = 0.002; % ASSUMPTION: 0.2% water loss
S.DMF.TSS_removal = 0.80;       % ASSUMPTION: 80% of remaining TSS removed
S.DMF.water_loss_fraction = 0.002; % ASSUMPTION: 0.2% water loss
S.CF.TSS_removal = 0.50;        % ASSUMPTION: 50% of remaining TSS removed
S.CF.water_loss_fraction = 0.001; % ASSUMPTION: 0.1% water loss

% UF assumptions
S.UF.waterRecovery = 0.95;      % ASSUMPTION: 95% feed becomes UF permeate
S.UF.TSS_removal = 0.99;        % ASSUMPTION: 99% TSS removal
S.UF.pressureDrop_bar = 1.0;    % ASSUMPTION: pressure drop across UF
S.UF.feedPressure_bar = 4.0;    % assumed UF feed pressure

% RO assumptions
S.RO.waterRecovery = 0.48;      % ASSUMPTION: fraction of RO feed becoming permeate
S.RO.saltRejection = 0.9957;    % ASSUMPTION: 99.57% salt rejection
S.RO.feedPressure_bar = 55.1;   % reference-like high-pressure feed
S.RO.permeatePressure_bar = 1.0;

% ERD assumptions
S.ERD.efficiency = 0.95;        % ASSUMPTION: 95% of available hydraulic power recovered
S.ERD.brinePressure_bar = 54.0; % ASSUMPTION: pressure available at brine-side ERD inlet
S.ERD.outletPressure_bar = 2.0; % ASSUMPTION: pressure after energy recovery

% Energy estimate assumptions
S.energy.highPressurePumpEfficiency = 0.85; % ASSUMPTION, fraction
S.energy.feedPumpPressure_bar = S.RO.feedPressure_bar;
S.energy.feedPumpInletPressure_bar = S.raw.pressure_bar;

%% ============================================================
% 2. INITIALIZE RAW WATER STREAM
% =============================================================

stream.raw.flow_m3h = S.raw.flow_m3h;
stream.raw.TDS_mgL = S.raw.TDS_mgL;
stream.raw.TSS_mgL = S.raw.TSS_mgL;
stream.raw.pressure_bar = S.raw.pressure_bar;
stream.raw.temperature_C = S.raw.temperature_C;

%% ============================================================
% 3. DAF - DISSOLVED AIR FLOTATION
% =============================================================

stream.DAF = stream.raw;
stream.DAF.flow_m3h = stream.raw.flow_m3h * ...
    (1 - S.DAF.water_loss_fraction);
stream.DAF.TSS_mgL = stream.raw.TSS_mgL * ...
    (1 - S.DAF.TSS_removal);
% DAF is not assumed to remove dissolved salts.
stream.DAF.TDS_mgL = stream.raw.TDS_mgL;
stream.DAF.pressure_bar = stream.raw.pressure_bar;

%% ============================================================
% 4. DMF - DUAL MEDIA FILTER
% =============================================================

stream.DMF = stream.DAF;
stream.DMF.flow_m3h = stream.DAF.flow_m3h * ...
    (1 - S.DMF.water_loss_fraction);
stream.DMF.TSS_mgL = stream.DAF.TSS_mgL * ...
    (1 - S.DMF.TSS_removal);
stream.DMF.TDS_mgL = stream.DAF.TDS_mgL;

%% ============================================================
% 5. CF - CARTRIDGE FILTER
% =============================================================

stream.CF = stream.DMF;
stream.CF.flow_m3h = stream.DMF.flow_m3h * ...
    (1 - S.CF.water_loss_fraction);
stream.CF.TSS_mgL = stream.DMF.TSS_mgL * ...
    (1 - S.CF.TSS_removal);
stream.CF.TDS_mgL = stream.DMF.TDS_mgL;

%% ============================================================
% 6. UF - ULTRAFILTRATION
% ============================================================

stream.UF.permeate.flow_m3h = stream.CF.flow_m3h * S.UF.waterRecovery;
stream.UF.reject.flow_m3h = stream.CF.flow_m3h - stream.UF.permeate.flow_m3h;

stream.UF.permeate.TSS_mgL = stream.CF.TSS_mgL * ...
    (1 - S.UF.TSS_removal);
stream.UF.permeate.TDS_mgL = stream.CF.TDS_mgL; % UF assumed not to remove dissolved salt
stream.UF.permeate.pressure_bar = ...
    max(S.UF.feedPressure_bar - S.UF.pressureDrop_bar, 0);

% Suspended-solids mass balance for UF reject stream
if stream.UF.reject.flow_m3h > 0
    tssMassIn_mgL_m3h = stream.CF.flow_m3h * stream.CF.TSS_mgL;
    tssMassPermeate_mgL_m3h = ...
        stream.UF.permeate.flow_m3h * stream.UF.permeate.TSS_mgL;
    stream.UF.reject.TSS_mgL = ...
        max((tssMassIn_mgL_m3h - tssMassPermeate_mgL_m3h) / ...
        stream.UF.reject.flow_m3h, 0);
else
    stream.UF.reject.TSS_mgL = NaN;
end

%% ============================================================
% 7. RO - REVERSE OSMOSIS
% =============================================================

stream.RO.feed.flow_m3h = stream.UF.permeate.flow_m3h;
stream.RO.feed.TDS_mgL = stream.UF.permeate.TDS_mgL;
stream.RO.feed.pressure_bar = S.RO.feedPressure_bar;

% Flow split
stream.RO.permeate.flow_m3h = ...
    stream.RO.feed.flow_m3h * S.RO.waterRecovery;
stream.RO.brine.flow_m3h = ...
    stream.RO.feed.flow_m3h - stream.RO.permeate.flow_m3h;

% Salt rejection gives permeate concentration from feed concentration.
stream.RO.permeate.TDS_mgL = ...
    stream.RO.feed.TDS_mgL * (1 - S.RO.saltRejection);

% Salt mass balance determines brine TDS:
% Qfeed*Cfeed = Qpermeate*Cpermeate + Qbrine*Cbrine
if stream.RO.brine.flow_m3h > 0
    stream.RO.brine.TDS_mgL = ...
        (stream.RO.feed.flow_m3h * stream.RO.feed.TDS_mgL - ...
        stream.RO.permeate.flow_m3h * stream.RO.permeate.TDS_mgL) / ...
        stream.RO.brine.flow_m3h;
else
    stream.RO.brine.TDS_mgL = NaN;
end

stream.RO.permeate.pressure_bar = S.RO.permeatePressure_bar;
stream.RO.brine.pressure_bar = S.ERD.brinePressure_bar;

%% ============================================================
% 8. ERD - ENERGY RECOVERY DEVICE
% =============================================================

% Hydraulic power (kW) = flow (m^3/h) * pressure difference (bar) / 36
erdPressureDrop_bar = max( ...
    S.ERD.brinePressure_bar - S.ERD.outletPressure_bar, 0);

S.ERD.availableHydraulicPower_kW = ...
    stream.RO.brine.flow_m3h * erdPressureDrop_bar / 36;

S.ERD.recoveredPower_kW = ...
    S.ERD.availableHydraulicPower_kW * S.ERD.efficiency;

%% ============================================================
% 9. ENERGY ESTIMATE
% =============================================================

pumpPressureRise_bar = max( ...
    S.energy.feedPumpPressure_bar - S.energy.feedPumpInletPressure_bar, 0);

S.energy.pumpHydraulicPower_kW = ...
    stream.RO.feed.flow_m3h * pumpPressureRise_bar / 36;

S.energy.pumpElectricalPower_kW = ...
    S.energy.pumpHydraulicPower_kW / S.energy.highPressurePumpEfficiency;

if stream.RO.permeate.flow_m3h > 0
    S.energy.netPower_kW = ...
        S.energy.pumpElectricalPower_kW - S.ERD.recoveredPower_kW;
    S.energy.netSEC_kWh_m3 = ...
        S.energy.netPower_kW / stream.RO.permeate.flow_m3h;
else
    S.energy.netPower_kW = NaN;
    S.energy.netSEC_kWh_m3 = NaN;
end

%% ============================================================
% 10. OVERALL PERFORMANCE AND MASS BALANCES
% =============================================================

S.performance.overallRecovery_percent = ...
    stream.RO.permeate.flow_m3h / stream.raw.flow_m3h * 100;

S.performance.RORecovery_percent = ...
    stream.RO.permeate.flow_m3h / stream.RO.feed.flow_m3h * 100;

S.performance.saltRejection_percent = ...
    (1 - stream.RO.permeate.TDS_mgL / stream.RO.feed.TDS_mgL) * 100;

% Water balance at RO
S.balance.RO_waterError_m3h = ...
    stream.RO.feed.flow_m3h - stream.RO.permeate.flow_m3h - stream.RO.brine.flow_m3h;

% Dissolved salt balance at RO, using Q (m^3/h) * TDS (mg/L)
S.balance.RO_saltError = ...
    stream.RO.feed.flow_m3h * stream.RO.feed.TDS_mgL - ...
    stream.RO.permeate.flow_m3h * stream.RO.permeate.TDS_mgL - ...
    stream.RO.brine.flow_m3h * stream.RO.brine.TDS_mgL;

% Total plant water accounting: product + brine + UF reject + pretreatment losses
S.balance.plantWaterError_m3h = ...
    stream.raw.flow_m3h - ...
    stream.RO.permeate.flow_m3h - stream.RO.brine.flow_m3h - ...
    stream.UF.reject.flow_m3h - ...
    (stream.raw.flow_m3h - stream.DAF.flow_m3h) - ...
    (stream.DAF.flow_m3h - stream.DMF.flow_m3h) - ...
    (stream.DMF.flow_m3h - stream.CF.flow_m3h);

%% ============================================================
% 11. DISPLAY RESULTS
% =============================================================

fprintf('\n============================================================\n');
fprintf(' SIMPLE SWRO DESALINATION PLANT MODEL\n');
fprintf(' Steady-state prototype - assumptions are editable\n');
fprintf('============================================================\n');

fprintf('\n--- Water streams ---\n');
fprintf('Raw seawater flow          : %10.2f m3/h\n', stream.raw.flow_m3h);
fprintf('After DAF                  : %10.2f m3/h\n', stream.DAF.flow_m3h);
fprintf('After DMF                  : %10.2f m3/h\n', stream.DMF.flow_m3h);
fprintf('After cartridge filter     : %10.2f m3/h\n', stream.CF.flow_m3h);
fprintf('UF permeate to RO           : %10.2f m3/h\n', stream.UF.permeate.flow_m3h);
fprintf('UF reject                   : %10.2f m3/h\n', stream.UF.reject.flow_m3h);
fprintf('RO permeate / product       : %10.2f m3/h\n', stream.RO.permeate.flow_m3h);
fprintf('RO brine                    : %10.2f m3/h\n', stream.RO.brine.flow_m3h);

fprintf('\n--- Water quality ---\n');
fprintf('Raw seawater TDS            : %10.2f mg/L\n', stream.raw.TDS_mgL);
fprintf('After DAF TSS               : %10.4f mg/L\n', stream.DAF.TSS_mgL);
fprintf('After DMF TSS               : %10.4f mg/L\n', stream.DMF.TSS_mgL);
fprintf('After CF TSS                : %10.4f mg/L\n', stream.CF.TSS_mgL);
fprintf('RO feed TDS                 : %10.2f mg/L\n', stream.RO.feed.TDS_mgL);
fprintf('Product water TDS            : %10.2f mg/L\n', stream.RO.permeate.TDS_mgL);
fprintf('RO brine TDS                : %10.2f mg/L\n', stream.RO.brine.TDS_mgL);

fprintf('\n--- Performance ---\n');
fprintf('Overall plant recovery      : %10.2f %%\n', S.performance.overallRecovery_percent);
fprintf('RO recovery                 : %10.2f %%\n', S.performance.RORecovery_percent);
fprintf('RO salt rejection           : %10.2f %%\n', S.performance.saltRejection_percent);
fprintf('Estimated pump power        : %10.2f kW\n', S.energy.pumpElectricalPower_kW);
fprintf('Estimated ERD recovered     : %10.2f kW\n', S.ERD.recoveredPower_kW);
fprintf('Estimated net SEC            : %10.3f kWh/m3\n', S.energy.netSEC_kWh_m3);

fprintf('\n--- Balance checks (should be close to zero) ---\n');
fprintf('RO water balance error      : % .6f m3/h\n', S.balance.RO_waterError_m3h);
fprintf('RO salt balance error       : % .6f (Q*TDS units)\n', S.balance.RO_saltError);
fprintf('Plant water balance error   : % .6f m3/h\n', S.balance.plantWaterError_m3h);

fprintf('\nNOTE: DAF/DMF/CF/UF removal and recovery values are assumptions.\n');
fprintf('Replace them with measured or sourced values before using results\n');
fprintf('for engineering decisions. This is a steady-state prototype, not\n');
fprintf('yet a time-updating digital twin.\n');
fprintf('============================================================\n');

