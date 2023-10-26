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

## Structure

### [Thesis](./thesis/)

Contains markdown documents for thesis content

### [Implementation](./impl/)

Contains the implementation and its dependencies

### [Notes](./notes/)

Contains personal notes, irrelevant for final submission.

### [Presentation Slides](https://docs.google.com/presentation/d/1dhrsWy_iDS3d3HnWNr0E9MciqOHN4IZfDC7f3xYNjKo/edit?usp=sharing)
