# TODOs

- [x] (2023-08-11) create architecture for CMDB
- [ ] (2023-08-11) create Orion demo
- [ ] (2023-08-11) investigate Aries agents, who owns what, and where is data stored (indy, indy-vdr etc.)

## Research/Reading

- MUDs:
  - [ ] Securing small-business and home internet of things (IoT) devices: Mitigating network-based
        attacks using manufacturer usage description (mud)
  - [ ] read [mud](https://resources.infosecinstitute.com/topic/how-to-mitigate-iot-attacks-using-manufacturer-usage-description-mud/)
  - [ ] Trusted IoT Device Network-Layer Onboarding and Lifecycle Management
- [ ] read hyperledger fabric doc
- [ ] review [Interledger UMU](https://www.researchgate.net/publication/342255539_An_Interledger_Blockchain_Platform_for_Cross-Border_Management_of_Cybersecurity_Information)
- [ ] review [BC4CC UZH]()/[Bifroest UZH](https://gitlab.ifi.uzh.ch/scheid/bifrost)

### Done

- [x] SRAM-Based PUF Readouts
  - Do I need to develop an algorithm myself?
    - nope, not doing it, simplify with hardcoded credential/key

## Writing and Diagrams

- [ ] Background: DLT
  - (on it)
- [ ] Background: updating
  - (on it)
- [ ] Related Work: VC comparison and highlighting
  - (on it)
- [ ] Related Work: Further in-depth research ETH, IoTeX, Iroha
  - (on it)
- [ ] Search all abbreviations and only define the first one!
- [ ] address CMDB, acc. To proposal should be DLT based

### Done

- [x] create detailed diagram for infrastructure
- [x] Rewrite Introduction from Thesis proposal
- [x] Transcribe use case from markdown

## Implementation

- [ ] run Indy network
  - not working, some compilation error through NodeJS
- [ ] run Fabric network
  - Java, Go, JavaScript Smart Contract Languages
- [ ] run Sawtooth network
- [ ] create local version with [von-network](https://github.com/bcgov/von-network):
      run by `./manage start --logs`, then run demo `./run_demo faber/alice`
- [ ] Aries create standalone example without Faber/Alice demo
- [ ] get hardware details to be able to start implementation
  - (2023-08-10) requested from Eryk

### Done

- [x] run Aries [OpenAPI demo](https://github.com/hyperledger/aries-cloudagent-python/blob/main/demo/AriesOpenAPIDemo.md) (added 2023-07-31)

- Iroha: examples build but cannot submit to network anymore -> version mismatch according to developers

## Meetings

- [x] Prepare slides for Bruno/next supervisor to explain current status (2023-08-09)
