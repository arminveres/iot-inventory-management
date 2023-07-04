# Hyperledger

<!--toc:start-->
- [Hyperledger](#hyperledger)
  - [Distributed Ledgers in Consideration](#distributed-ledgers-in-consideration)
    - [[Interledger](https://ieeexplore.ieee.org/document/9119756?denied=), UMU](#interledgerhttpsieeexploreieeeorgdocument9119756denied-umu)
      - [Possible Application](#possible-application)
    - [Bifröst/BC4CC, UMU](#bifröstbc4cc-umu)
      - [Possible Application](#possible-application)
    - [[Hyperledger Aries](https://wiki.hyperledger.org/display/ARIES/Hyperledger+Aries)](#hyperledger-arieshttpswikihyperledgerorgdisplayarieshyperledgeraries)
      - [Possible Application](#possible-application)
    - [[Hyperledger Besu](https://wiki.hyperledger.org/display/BESU/Hyperledger+Besu)](#hyperledger-besuhttpswikihyperledgerorgdisplaybesuhyperledgerbesu)
      - [Possible Application](#possible-application)
    - [[Hyperledger Fabric](https://wiki.hyperledger.org/display/fabric/Hyperledger+Fabric)](#hyperledger-fabrichttpswikihyperledgerorgdisplayfabrichyperledgerfabric)
      - [Possible Application](#possible-application)
    - [[Hyperledger Indy](https://wiki.hyperledger.org/display/indy/Hyperledger+Indy)](#hyperledger-indyhttpswikihyperledgerorgdisplayindyhyperledgerindy)
      - [Possible Application](#possible-application)
    - [[Hyperledger Iroha](https://wiki.hyperledger.org/display/iroha/Hyperledger+Iroha)](#hyperledger-irohahttpswikihyperledgerorgdisplayirohahyperledgeriroha)
      - [Possible Application](#possible-application)
    - [[Hyperledger Sawtooth](https://wiki.hyperledger.org/display/sawtooth/Hyperledger+Sawtooth)](#hyperledger-sawtoothhttpswikihyperledgerorgdisplaysawtoothhyperledgersawtooth)
<!--toc:end-->

CERTIFY is targeting [Hyperledger Aries](https://www.hyperledger.org/use/aries) as a DLT and also the identity management.

## Distributed Ledgers in Consideration

We will probably use permissioned blockchains, as we don't want permissionless access, therefore
Ethereum and Bitcoin are out of the picture.

### [Interledger](https://ieeexplore.ieee.org/document/9119756?denied=), UMU

#### Possible Application

### Bifröst/BC4CC, UMU

#### Possible Application

### [Hyperledger Aries](https://wiki.hyperledger.org/display/ARIES/Hyperledger+Aries)

- focus on creating, transmitting and storing VCs
- blockchain rooted, peer-to-peer interactions
- cryptographic support by [Hyperledger Ursa](https://www.hyperledger.org/use/ursa) (deprecated)

#### Possible Application

- Identity Management, IdM, of edge nodes
- let the manufacturer issue VCs through Aries

### [Hyperledger Besu](https://wiki.hyperledger.org/display/BESU/Hyperledger+Besu)

- Ethereum client, private and public network use cases
- Can be run on test networks such as [Sepolia and Goerli](https://www.alchemy.com/overviews/goerli-vs-sepolia)
- Multiple consensus algorithms
  - proof of stake
  - proof of work
  - proof of authority

#### Possible Application

### [Hyperledger Fabric](https://wiki.hyperledger.org/display/fabric/Hyperledger+Fabric)

- Architectural 'glue', allows modular architecture, combining consensus and membership services
- [docs](https://hyperledger-fabric.readthedocs.io/en/latest/blockchain.html)

#### Possible Application

- According to [this](https://www.hyperledger.org/blog/2021/02/25/solution-brief-decentralized-id-and-access-management-diam-for-iot-networks)
  whitepaper, there are already some architectural solutions to managing this kind of IoT
  infrastructure
- Application therefore possible to our infrastructure

### [Hyperledger Indy](https://wiki.hyperledger.org/display/indy/Hyperledger+Indy)

- tools/libraries/components for providing digital identities

#### Possible Application

- use to generate DIDs for IoT devices.

### [Hyperledger Iroha](https://wiki.hyperledger.org/display/iroha/Hyperledger+Iroha)

- for IoT projects requiring DLT
- supports crash fault tolerant consensus algorithm, YAC.

#### Possible Application

- could be directly employed on the edge nodes and take advantage of DLT services
- has python API

### [Hyperledger Sawtooth](https://wiki.hyperledger.org/display/sawtooth/Hyperledger+Sawtooth)

- various consensus algorithms, Practical Byzantine Fault Tolerance, PBFT, Proof of Elapsed Time,
  PoET
