# Bachelor Thesis: Inventorying and Secure life-cycles of IoT Devices

## This thesis will

- Develop a **service to support security information** sharing between stakeholders

- Consider Distributed Ledger Technology for sharing cybersecurity information

- Throughout security monitoring activities vulnerabilities may be detected, that will be shared
  with manufacturer, prompting mitigation and resolutions.

- Devices deploying this methodology will be able to be reconfigured throughout whole life-cycle

- Develop bootstrapping mechanism to **provide light-weight bootstrapping protocol**, supporting
  different authentication methods, depending on the devices characteristics/key-management.

- Device inventorying, keeping track of each (embedded) IoT device

- Secure updating/patching, as close as possible to end device

- Analysis of Bifröst/Interledger approaches to interconnect different blockchain implementations

- Consider mitigation using Manufacturer Usage Description

## Challenges

- Using same pre-shared credential for every device is the easiest way, but not identifiable for
  each device
  - Clonability of DID credentials
- Most proposals based on centralized models (client-server) -> use DLT to make it more efficient,
  decentralized

## Setup

The full repo including submodules needs to be cloned:

`git clone --recursive https://github.com/bachelor-thesis-23`

In order to run the demo network `docker` is needed. (add other requirements)

For local development, we offer to solutions for python environments.
Either use `conda` and setup an environment using the `acapy-env.yml` and subsequently installing missing packages
through pip with the `requirements.dev.txt` file or using Python virtual environment solely with
`requirements.dev.noconda.txt`.

## Repository Structure

### [Archive](./.archive)

Holds some experimentation with other frameworks than Aries/ACA-py

### [Cyrpto](./crypto)

Holds cryptographic information for connection to the Hyperledger Orion Database

### [Dependencies](./dependencies)

Holds git submodules, that we depend on for running our framework.

### [Docker](./docker/)

Holds `Dockerfiles` for every type of agent we have.

### [Graphs](./graphs)

Holds some of the visualizations and the corresponding scripts used in evaluating the performance.

### [Scripts](./scripts)

Holds relevant scripts, that are either used in the `manage` or `run` scripts, or they are
completely standalone, such as the `./scripts/setup-many-nodes.sh` and `./scripts/stop-nodes.sh`.

### [Source](./src)

Holds all the python source files used to implement our framework.

### [Agent Cache](./.agent_cache) and [Logs](./logs)

Both are used to hold temporary information while running the framework.
