Aries Cloud Agent Python runs two processes, one for the agent, one for the controller.

In the demo, the agents start a sub-process that runs the controller.

RFC: Request for comments
AIP: Aries Interoperability Profiles

- created for interoperability and inherent problem with newer modules and evolution.

- And as this is written (January 2023), there are rumblings of an AIP 3.0 that will include a new version of DIDComm (V2), and the protocol updates necessary to use DIDComm V2. Given the progress being made in Aries since AIP 2.0 was declared, AIP 3.0 will likely include a number of powerful new capabilities.

## Aries Cloud Agent Python

Aries Cloud Agent Python (ACA-Py) is a mature, purely cloud-based agent, suitable for deployment as an enterprise issuer/verifier or an organizational holder (or all three at once!). It supports robust, scalable enterprise deployments with features like:

- Full AIP 1.0 and near complete (as of this writing, January 2023) support for AIP 2.0.
- Support for multiple verifiable credential formats including AnonCreds and JSON-LD using LD-Signatures and BBS+ Signatures.
- Scalable cloud native support, for use on container environments like Kubernetes.
- Multi-tenant support, allowing many identity owners to use a single scaled instance.
- Enterprise database support using Postgres or Clustered Postgres.
- Integration with persistent queue and shared caching, such as Redis.
- Issuer support for AnonCreds Revocation, including automated handling of multiple registries.

While developed in Python, ACA-Py exposes an HTTP API for controllers to use, so applications can be developed in any language/stack.
**ACA-Py has even been deployed on Raspberry Pi’s and so can be used in IoT scenarios.**
-> applies to me and my RPI controller nodes
The Hyperledger Aries project includes services such as an Aries Mediator and an Aries Endorser that are pre-configured, purpose-built instances of ACA-Py suitable for immediate deployment.

## Aries Agent Test Harness

- ACME is an issuer
- Bob is a holder/prover
- Faber is a verifier
- Mallory is holder/prover that is sometime malicious
