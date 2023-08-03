# Hyperledger

CERTIFY is targeting [Hyperledger Aries](https://www.hyperledger.org/use/aries) as a DLT and also the identity management.

## Distributed Ledgers in Consideration

We will probably use permissioned blockchains, as we don't want permissionless access, therefore
Ethereum and Bitcoin are out of the picture.

### [Interledger](https://ieeexplore.ieee.org/document/9119756?denied=), UMU

#### Possible Application

### Bifröst/BC4CC, UMU

- I don't see a good reason to use such a blockchain while there exist others like Hyperledger.

#### Possible Application

### [Hyperledger Aries](https://wiki.hyperledger.org/display/ARIES/Hyperledger+Aries)

- focus on creating, transmitting and storing VCs
- blockchain rooted, peer-to-peer interactions
- cryptographic support by [Hyperledger Ursa](https://www.hyperledger.org/use/ursa) (deprecated)

#### Possible Application

- Identity Management, IdM, of edge nodes
- let the manufacturer issue VCs through Aries
- using Aries in combination with Indy, we wouldn't be able to use Smart Contracts, but we could
  simply retain the logic for REST APIs and then check on conditions, maybe not the fastest way.

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
- Java, Go or JavaScript as applicable language

### [Hyperledger Indy](https://wiki.hyperledger.org/display/indy/Hyperledger+Indy)

- tools/libraries/components for providing digital identities

#### Possible Application

- use to generate DIDs for IoT devices.
- as it is a DLT its working in the background for other stuff like Aries!

### [Hyperledger Iroha](https://wiki.hyperledger.org/display/iroha/Hyperledger+Iroha)

- for IoT projects requiring DLT
- supports crash fault tolerant consensus algorithm, YAC.

#### Possible Application

- could be directly employed on the edge nodes and take advantage of DLT services
- has python API

### [Hyperledger Sawtooth](https://wiki.hyperledger.org/display/sawtooth/Hyperledger+Sawtooth)

- various consensus algorithms, Practical Byzantine Fault Tolerance, PBFT, Proof of Elapsed Time,
  PoET
- Can use Smart Contracts on Chain with `Sawtooth Sabre` and on Ethereum through `Sawtooth Seth`
