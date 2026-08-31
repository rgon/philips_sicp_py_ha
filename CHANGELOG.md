# Changelog

## [0.7.2](https://github.com/rgon/philips_sicp_py_ha/compare/v0.7.1...v0.7.2) (2026-08-31)


### Bug Fixes

* **config_flow:** validate with a 2-command identity fetch instead of a full status poll ([c77c780](https://github.com/rgon/philips_sicp_py_ha/commit/c77c7800b7c6a7aa26ff5c1976c8d1e8c2e57aee))
* fall back to Wake-on-LAN when powering on an unreachable display ([46629f1](https://github.com/rgon/philips_sicp_py_ha/commit/46629f1d46645181921a62207320a50154ae85ac))
* **sicppy:** bound the SICP write with the connection timeout ([80c02db](https://github.com/rgon/philips_sicp_py_ha/commit/80c02db5c7f3b972ce54bb95f5587a0fdbaeb983))
* stop polling a display that reports itself offline ([1a84c28](https://github.com/rgon/philips_sicp_py_ha/commit/1a84c2834807480195fe035f2dd33e0fb9c86579))

## [0.7.1](https://github.com/rgon/philips_sicp_py_ha/compare/v0.7.0...v0.7.1) (2026-08-31)


### Bug Fixes

* stop validating configuration.yaml against the config flow schema ([56da44d](https://github.com/rgon/philips_sicp_py_ha/commit/56da44d951cffb6c5e4a5abf1807d826af3308cb))


### Documentation

* correct stale component paths in the install instructions ([77cffd1](https://github.com/rgon/philips_sicp_py_ha/commit/77cffd156f0d4f4b4079e62130907c29bbe66d3a))

## [0.7.0](https://github.com/rgon/philips_sicp_py_ha/compare/v0.6.0...v0.7.0) (2026-08-31)


### Features

* add reconfigure flow to edit configured displays in place ([8d05010](https://github.com/rgon/philips_sicp_py_ha/commit/8d050106648329cd09437a513ce89881e3d697e6))


### Bug Fixes

* derive the Wake-on-LAN broadcast address from the display subnet ([4a239b3](https://github.com/rgon/philips_sicp_py_ha/commit/4a239b33171a90ff0901c513110dfa461cd0912c))
* point packaging and release workflow at the renamed component directory ([dbce97c](https://github.com/rgon/philips_sicp_py_ha/commit/dbce97c0bbbe90dc2ad46344234dd8d1c47f92c1))
* re-derive Wake-on-LAN broadcast address when reconfiguring a display ([66e355f](https://github.com/rgon/philips_sicp_py_ha/commit/66e355f75f2cfbe095231ea2fd039fce62517dd9))
* route Wake-on-LAN via a configurable broadcast address for cross-subnet displays ([933ca79](https://github.com/rgon/philips_sicp_py_ha/commit/933ca79b6da2c083ef5772ddb25ccefb78fceab8))


### Documentation

* add UniFi cross-subnet Wake-on-LAN setup guide ([a0fda76](https://github.com/rgon/philips_sicp_py_ha/commit/a0fda765bed67f9cdb66b2fb48063c2e583f31bd))
