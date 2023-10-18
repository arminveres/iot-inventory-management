It holds the scripts to perform various build, and install.

### creating private keys and certificates and using them in configuration
Run from `orion-server` root folder:

Run `./scripts/cryptoGen.sh deployment [args]`,
replace `[args]` with any optional user.


Example:

Create keys and certs for CA, admin, server, user, alice anb bob by: `./scripts/cryptoGen.sh deployment alice bob`

The generated crypto materials are stored inside deployment.
