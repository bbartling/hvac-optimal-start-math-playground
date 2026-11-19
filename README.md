# Optimal start and stop: BAS behavior first, model experiments second

A short [Kaggle tutorial](optimal_start_stop_tutorial.ipynb) backed by a readable Python driver. Both **optimal start and optimal stop** follow the owner-supplied `BOptimizedStartStop.java` behavior reference. PNNL-style predictors and model selection are separate research components.

The notebook replays recorded recoveries, plots errors and selection over time, and can run the actual competition simulator. The standard-library core also works without Jupyter, pandas or NumPy for an IoT/BAS adapter.

The notebook's **Controller without NumPy or pandas** section includes a plain-Python example and explains equivalent scalar arithmetic for a vanilla Java/Niagara adapter. All eight estimators use the standard library; native start/stop needs no matrix math.

## Run

```powershell
python -m pip install -e ".[notebook,test]"
python -m pytest -q
jupyter lab optimal_start_stop_tutorial.ipynb
```

Build an **offline** Kaggle dataset; nothing is uploaded:

```powershell
python -m hvac_optimal bundle --out "$env:TEMP\optimal-start-kaggle"
```

Attach that folder's driver ZIP and data to Kaggle. Run the small notebook with internet off. Attach the official simulator kit separately for simulations; it is not redistributed in the bundle.

## Native BAS state machine and learning

```text
on each scheduled scan:
    reset startDone only under the original disable/midnight conditions
    analyze the PREVIOUS mode before calculating the next command
    if dynamic adjustment, unfinished analysis and valid space-temperature status:
        if correct-direction movement AND (comfort reached OR schedule transitioned):
            observed = elapsed minutes / temperature change
            selected parameter = (old * multiplier + observed) / (multiplier + 1)
            mark this analysis complete
    calculate start or stop for the native schedule/date/enable conditions
    apply original earliest-time, integer-rounding and strict-after-time rules
    emit command value AND null status; save current mode
```

Four independent **minutes/degree** learners cover heating/cooling runtime for start and heating/cooling drift for stop. Defaults are 10; multiplier 2 means two-thirds old plus one-third new. A small positive response at a schedule transition can update before full recovery.

**Do not add AI-invented minimum-change, sample-count, cooldown, rate-cap or outlier gates to this reference.** Preserve its actual conditions and quirks. Active optimized stop is FALSE with non-null status; a null FALSE is no override. See the [source-traceable contract](docs/reference-contract.md) and [agent instructions](AGENTS.md).

The supplied implementation is the owner's established BAS reference. This Python port is new: source/differential tests do not establish decades of field operation or certify Niagara framework equivalence. Framework assumptions are documented rather than hidden.

## Per-AHU inputs and ventilation

Each AHU has independent state and a fixed **30% zone sample**, balanced between exterior/interior zones when metadata permits. Averaging weights default to equal and are configurable. Receipts show selected zones, classifications and any fallback. [Sampling contract](docs/sampling.md).

Verified-unoccupied temperature recovery normally requests full recirculation through the minimum outside-air damper position; occupied ventilation resumes at occupancy. Existing site ventilation/safety interlocks remain external; no learning gate is added. The competition simulator caps recirculation at **70%**, so it cannot validate full-return-air recovery.

## Actual simulator, all buildings

Use the sibling competition environment, which already has simulator dependencies:

```powershell
$simPy = "C:\Users\ben\Documents\neurips-2026-smart-buildings\.venv-sim\Scripts\python.exe"
& $simPy -m hvac_optimal simulate --kit "C:\Users\ben\Documents\neurips-2026-smart-buildings\.kit" --out "$env:TEMP\optimal-start-full" --steps 8640 --workers 2
```

The runner discovers every configured scenario: currently six buildings and 30 scenarios. Each AHU receives its own reference controller and learner bank. Start comparisons hold stop/plant/schedule fixed; stop comparisons hold start fixed. Short runs are integration tests, not competition scores. Resume requires matching source/config identities. [Simulator instructions](docs/simulator.md).

**Executed:** 60 full 30-day jobs passed across all 30 scenarios, with 340 AHU-scenario runs and no failures. Adaptive improved six scenarios and worsened 24; native remains the default. The two policies use different commanded arrival objectives, so this is not an isolated selector comparison. [Results and limits](docs/validation/README.md).

## Source and evidence

- [`reference.py`](hvac_optimal/reference.py): native start/stop and separately named prediction extension.
- [`models.py`](hvac_optimal/models.py), [provenance](docs/model-provenance.md): supplied PNNL code, paper differences and adaptations.
- [`replay.py`](hvac_optimal/replay.py), [datasets](docs/datasets.md): predict-before-update, censoring and inventory.
- [`iot.py`](hvac_optimal/iot.py): timestamped JSONL input and command/status receipts; no field writes.

Old aggregate CSVs and the [archived harness](https://github.com/bbartling/hvac-optimal-start-math-playground/tree/archive/pre-strip-2026-11-17) remain historical material. Their start arms changed stop policies too; they are not corrected winner evidence. PNNL attribution is retained in [`LICENSES/PNNL-BSD.txt`](LICENSES/PNNL-BSD.txt).
