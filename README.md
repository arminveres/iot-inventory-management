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
- Most proposals based on centralized models (client-server) -> use DLT to make it more efficient,
  decentralized

## Structure

### ./thesis

Contains markdown documents for thesis content

### ./dailies

Contains daily notes a la Zettelkasten

### [terminology.md](./terminology.md)

Explanations for different topics

## TODO

- find hyperledger that is able to hold smart contracts and DIDs
- review [Hyperledger Aries](https://www.hyperledger.org/use/aries)
- review [Interledger UMU](https://www.researchgate.net/publication/342255539_An_Interledger_Blockchain_Platform_for_Cross-Border_Management_of_Cybersecurity_Information)
- review [BC4CC UZH]()/[Bifrost UZH](https://gitlab.ifi.uzh.ch/scheid/bifrost)
