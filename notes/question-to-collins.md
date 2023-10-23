- What hardware capabilities are foreseen?

  - Wait for equipment list from COLLINS

- What is the general status of remote connection, is an in-flight real-time connection foreseen? Or
  mainly only connected at gateway with data offloading etc.

- What is the exact scenario difference between a regular replacement and a LRU replacement

---

## 2023-07-07, Stefano Sebastio, Eryk Schiller, Julia Kostadinova

How the network at the airplane may receive information to the network.
Left entities: owners, carriers Lufthansa, need remote maintenance, system integration
then product owner, multiple entities provide devices

All entities interact with plane from different life-cycle
knowledge should/could be leveraged for the whole fleet.

Classic connectivity on ground, but also on ground. not same kind of changes on ground vs.
in-flight. Could be anything, satcom, wifi, 5g etc.
Aircraft gateway is entry point! Collect and manage different kind of connectivity, storage of
information pushed from plane to ground, but also from ground/external infrastructure to plane.
Considering the passenger side, not the critical system, such as GPS and co.

IoT nodes, buttons and sensors, lightweight RISC-V MCUs devices, otherwise ARM M+ devices

- ask Eryk about what device he received, probably an M4 though
- [TOCKos](https://tockos.org/), lightweight OS for embedded device, compatible with ARM and RISC-V
  function collector: not much intelligence, some computational power for aggregation and data
  analysis
  central controller: multi-core ARM Cortex A based devices, it should be fine to replace with a Pi
- OS not decided yet

Current implementation in between the cabin devices is wired, although industry moving to wireless,
obvious challenges to security

Two configurations:

- A: pre-certified configurations, safety and security involved, managing simple task, could be
  expensive coffee machine, but not much data analysis/processing involved
- B: for more data related tasks

Roaming, can the airport verify identity of device and authenticate it to use airport services.
Depending on the trust between entities, e.g., trusting airport and their security policies and then
use their facilities

We should be able to see through the DLT that a credential was revoked. Associate firmware
versions with features and whatnot, that could be vulnerable.
