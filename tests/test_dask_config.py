from pathlib import Path
from typing import Any

import pytest
import yaml

from zoo_calrissian_runner import extract_dask_config


def write_package(tmp_path: Path, document: Any) -> str:
    path = tmp_path / "app-package.cwl"
    path.write_text(yaml.safe_dump(document), encoding="utf-8")
    return str(path)


@pytest.mark.parametrize("section", ["requirements", "hints"])
@pytest.mark.parametrize("as_list", [False, True])
@pytest.mark.parametrize(
    "name",
    [
        "calrissian:DaskGatewayRequirement",
        "https://calrissian-cwl.github.io/schema#DaskGatewayRequirement",
        "https://calrissian.example.com/DaskGatewayRequirement",
    ],
)
def test_extract_wrs_coverage_parameters(tmp_path, section, as_list, name):
    expected = {
        "workerCores": 1,
        "workerCoresLimit": 1,
        "workerMemory": "2G",
        "clusterMaxCores": 4,
        "clusterMaxMemory": "10G",
    }
    requirements = [{"class": name, **expected}] if as_list else {name: expected}
    document = {
        "cwlVersion": "v1.2",
        "$graph": [
            {"class": "Workflow", "id": "wrs-coverage"},
            {
                "class": "CommandLineTool",
                "id": "wrs-coverage-tool",
                section: requirements,
            },
        ],
    }

    assert extract_dask_config(write_package(tmp_path, document)) == expected


@pytest.mark.parametrize("steps_as_list", [False, True])
def test_extract_from_inline_run(tmp_path, steps_as_list):
    expected = {"gateway_url": "http://gateway.example", "configmap": "scripts"}
    step = {
        "id": "process",
        "run": {"hints": {"calrissian:DaskGatewayRequirement": expected}},
    }
    document = {"steps": [step] if steps_as_list else {"process": step}}

    assert extract_dask_config(write_package(tmp_path, document)) == expected


def test_extract_from_single_process(tmp_path):
    expected = {"gateway_url": "http://gateway.example", "configmap": "scripts"}
    document = {
        "class": "CommandLineTool",
        "requirements": [
            {"class": "DockerRequirement", "dockerPull": "alpine:3.20"},
            {"class": "calrissian:DaskGatewayRequirement", **expected},
        ],
    }

    assert extract_dask_config(write_package(tmp_path, document)) == expected


def test_empty_requirement_is_distinct_from_absence(tmp_path):
    path = write_package(
        tmp_path, {"requirements": {"calrissian:DaskGatewayRequirement": {}}}
    )
    assert extract_dask_config(path) == {}

    path = write_package(tmp_path, {"class": "Workflow"})
    assert extract_dask_config(path) is None


def test_similarly_named_requirement_is_ignored(tmp_path):
    path = write_package(
        tmp_path, {"requirements": {"calrissian:NotDaskGatewayRequirement": {}}}
    )
    assert extract_dask_config(path) is None


def test_identical_configurations_are_accepted(tmp_path):
    process = {
        "requirements": {"calrissian:DaskGatewayRequirement": {"workerCores": 1}}
    }
    path = write_package(tmp_path, {"$graph": [process, process]})

    assert extract_dask_config(path) == {"workerCores": 1}


def test_conflicting_configurations_are_rejected(tmp_path):
    path = write_package(
        tmp_path,
        {
            "$graph": [
                {
                    "requirements": {
                        "calrissian:DaskGatewayRequirement": {"workerCores": cores}
                    }
                }
                for cores in (1, 2)
            ]
        },
    )

    with pytest.raises(ValueError, match="incompatible Dask configurations"):
        extract_dask_config(path)


@pytest.mark.parametrize(
    ("document", "exception_type", "message"),
    [
        ([], TypeError, "CWL document must be a mapping"),
        ({"requirements": "invalid"}, TypeError, "Invalid requirements section"),
        ({"hints": ["invalid"]}, ValueError, "Section hints is invalid"),
        (
            {"requirements": {"calrissian:DaskGatewayRequirement": None}},
            TypeError,
            "DaskGatewayRequirement must be a mapping",
        ),
    ],
)
def test_invalid_configuration_is_rejected(tmp_path, document, exception_type, message):
    with pytest.raises(exception_type, match=message):
        extract_dask_config(write_package(tmp_path, document))


def test_invalid_yaml_is_rejected(tmp_path):
    path = tmp_path / "app-package.cwl"
    path.write_text("requirements: [", encoding="utf-8")

    with pytest.raises(yaml.YAMLError):
        extract_dask_config(str(path))


def test_missing_package_is_rejected(tmp_path):
    with pytest.raises(FileNotFoundError):
        extract_dask_config(str(tmp_path / "missing.cwl"))


def test_successive_packages_do_not_share_configuration(tmp_path):
    path = write_package(
        tmp_path,
        {"requirements": {"calrissian:DaskGatewayRequirement": {"workerCores": 1}}},
    )
    assert extract_dask_config(path) == {"workerCores": 1}

    path = write_package(tmp_path, {"class": "Workflow"})
    assert extract_dask_config(path) is None
