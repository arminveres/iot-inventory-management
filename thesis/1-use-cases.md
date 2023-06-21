# Use Case

Our use-case will highlight the advantages in a 'Connected Cabin system'

In addition to the use-cases defined in the CERTIFY documentation, we will also explore the
possibilities of enabling roaming on these devices

## Definitions

- PHM: Prognostics and Health Management
- HMI: Human Machine Interface
- Line-Replaceable Unit: modular component of airplane, designed to be replaced quickly

## Domain

**TODO: Explain why it makes sense to employ in this domain**

## Actors

- **Airline**
  - Owns the aircraft and oversees interactions and system operations.
- **Airplane maintainer** (e.g., Airplane manufacturer)
  - Oversees maintenance of the aircraft, including the integration of systems designed by different
    manufacturers and their configuration.
- **Product Owner**
  - Oversees design and maintenance of systems deployed in the aircraft on assignment of the
    airplane maintainer
- **Maintenance operator**
  - Works for airplane maintainer
  - E.g., replacement of device or on-site software upgrade (e.g., portable data loader)
- **Passenger, Attendant, Pilot**
  - Interact with aircraft through Human Machine Interfaces, HMI

## System under analysis/Functionalities

**TODO: identify components of system**

- Are we also using the central/function control scenario?

## Scenarios

### 1. Installation of Connected Cabin Systems

#### Goal

- Bootstrapping and customization for specific deployment
- Updating
- Decommissioning of previous systems, guaranteeing a reset to a _known and fresh (wiped data)_
  state.

### 2. System operation and monitoring

#### Goal

- periodic collection of data from airplane
- data offload/upload to ground stations for performance monitoring, optimization and PHM operations
- interaction through HMI

#### Actors involved

- Airline
- Airplane Maintainer
- Product Owner
- Maintenance Operator

#### New installation

#### Replacement

### 3. LRU - replacement and re-purposing

#### Goals

- to minimize downtime in case no LRU is available, compatible spare LRU is retrieved from
  manufacturer and re-purposed for specific target system

#### Actors involved

### 4. Roaming?

#### Goals

- Devices checking in at airport gateway should be able to checkout and check in at arriving
  destination. Needs rechecking and or re-certifying DID.

#### Actors involved

## Security Requirements

### Technologies
