# TODO

## Research/Reading

- [ ] read hyperledger fabric doc
- [ ] think about conceptual blockchain stuff
- MUDs:
  - [ ] Securing small-business and home internet of things (IoT) devices: Mitigating network-based
        attacks using manufacturer usage description (mud)
  - [ ] read [mud](https://resources.infosecinstitute.com/topic/how-to-mitigate-iot-attacks-using-manufacturer-usage-description-mud/)
  - [ ] Trusted IoT Device Network-Layer Onboarding and Lifecycle Management
- [x] SRAM-Based PUF Readouts
  - Do I need to develop an algorithm myself?
    - nope, not doing it, simplify with hardcoded credential/key

### on hold

- [ ] review [Interledger UMU](https://www.researchgate.net/publication/342255539_An_Interledger_Blockchain_Platform_for_Cross-Border_Management_of_Cybersecurity_Information)
- [ ] review [BC4CC UZH]()/[Bifroest UZH](https://gitlab.ifi.uzh.ch/scheid/bifrost)

## Writing

- [x] Rewrite Introduction from Thesis proposal
- [x] Transcribe use case from markdown
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

## Implementation

- [ ] get hardware details to be able to start implementation
- [ ] run Indy network
  - not working, some compilation error through NodeJS
- [ ] run Fabric network
  - Java, Go, JavaScript Smart Contract Languages
- [ ] run Sawtooth network

### Aries

- [x] run Aries [OpenAPI demo](https://github.com/hyperledger/aries-cloudagent-python/blob/main/demo/AriesOpenAPIDemo.md) (added 2023-07-31)
- [ ] find out where credentials are stored
- [ ] made local version with [von-network](https://github.com/bcgov/von-network)
      run by `./manage start --logs`, then run demo `./run_demo faber/alice`
- [ ] create standalone example without Faber/Alice demo

### Iroha

- examples build but cannot submit to network anymore -> version mismatch according to developers

## Meetings

- [ ] Prepare slides for Bruno/next supervisor to explain current status
