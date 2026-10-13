<!-- Glossary: hover any abbreviation to see its definition -->

<!-- GNSS fundamentals — see Navipedia (navipedia.net) for detailed articles -->
*[GNSS]: Global Navigation Satellite System — umbrella term for GPS, Galileo, GLONASS, BeiDou, etc. (Navipedia: GNSS)
*[GPS]: Global Positioning System — US satellite navigation constellation, 31 SVs in 6 orbital planes (Navipedia: GPS)

<!-- Satellite identifiers -->
*[SV]: Space Vehicle — a single GNSS satellite, identified by system prefix + PRN number

<!-- Observation data -->
*[RINEX]: Receiver Independent Exchange Format — standard ASCII format for GNSS observations, defined by IGS (Navipedia: RINEX)
*[SBF]: Septentrio Binary Format — proprietary binary telemetry from Septentrio receivers; embeds satellite geometry

<!-- VOD and transmissometry -->
*[VOD]: Vegetation Optical Depth — dimensionless measure of microwave attenuation through vegetation canopy (τ = −ln(T)·cos θ)
*[GNSS-T]: GNSS Transmissometry — method using differential SNR between canopy and reference receivers to estimate vegetation properties

<!-- Ephemerides and orbits -->
*[SP3]: Standard Product 3 — precise satellite orbit (position ± ~2 cm) file format, produced by IGS analysis centres (Navipedia: SP3)
*[CLK]: Clock — precise satellite and station clock correction file (30 s intervals), companion to SP3 orbits

<!-- Infrastructure -->
*[Icechunk]: Version-controlled cloud-native tensor storage engine — git-like snapshots over Zarr v3 chunks
*[pydantic]: The fastest and most widely used data validation library for Python - written in Rust
*[DAG]: Directed Acyclic Graph — task dependency structure used by workflow schedulers (Airflow, Prefect)

<!-- Signal bands -->
*[L1]: GPS/Galileo L1 band — centre frequency 1575.42 MHz (Navipedia: GPS Signal Plan)
*[L2]: GPS L2 band — centre frequency 1227.60 MHz (Navipedia: GPS Signal Plan)

<!-- Software tools -->
*[uv]: Fast Python package manager written in Rust — replaces pip, pip-tools, virtualenv
*[ruff]: Fast Python linter and formatter written in Rust — replaces flake8, black, isort
*[PyPI]: Python Package Index — public Python package repository
