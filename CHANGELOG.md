# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

> **Note:** This changelog was introduced at version v0.4.0. The full git history prior to this point has not been recovered. Earlier changes can be explored via the [git log](https://github.com/ZOO-Project/zoo-calrissian-runner/commits/main/) or the [upstream EOEPCA repository](https://github.com/EOEPCA/zoo-calrissian-runner). From this point forward, all notable changes will be documented here.

## [Unreleased]

## [v0.4.0] - 2026-01-23

### Added

- Package is now available on PyPI: `pip install zoo-calrissian-runner`
- Initial integration of `zoo-runner-common` for shared base runner functionality
- New dependency on `zoo-template-common` for reusable template utilities
- New dependency on `eoap_cwlwrap` replacing `cwl-wrapper`
- Added `load_a_workflow` method to `ZooCalrissianRunner`
- Added support for array of literal data inputs
- Added file stage-in template to handle pattern-11

### Changed

- Forked from [EOEPCA/zoo-calrissian-runner](https://github.com/EOEPCA/zoo-calrissian-runner) and moved under ZOO-Project organisation
- eoap_cwlwrap replacing cwl-wrapper
- Minimum Python version set to 3.10
- `kubernetes` dependency updated to `>=34.1.0`
- Simplified `get_processing_parameters` method
- Handled `ogc-bbox` input type properly


### Fixed

- Fixed Kubernetes version issue in `build-and-test` action
- Fixed typo in environment variable name


[Unreleased]: https://github.com/ZOO-Project/zoo-calrissian-runner/compare/v0.4.0...HEAD
[v0.4.0]: https://github.com/ZOO-Project/zoo-calrissian-runner/releases/tag/v0.4.0