import copy

import pytest
from jsonschema import Draft202012Validator
from pydantic import ValidationError

from ai_harness_compiler.models import HarnessSpec, ProjectInput
from ai_harness_compiler.pipeline import plan


def test_baseline_preserves_intent_and_evaluation_coverage(project):
    spec = plan(project)
    assert spec.project_dna.project == project
    assert spec.project_dna.domain.status == "declared"
    assert spec.project_dna.domain.confidence is None
    assert spec.capability_graph.execution_order() == ["material-library", "lesson-draft"]
    assert len(spec.evals) == 4
    assert all(case.status == "not-run" for case in spec.evals)
    assert spec.runtime_status == "not-implemented"
    assert HarnessSpec.model_validate_json(spec.model_dump_json()) == spec
    schema = HarnessSpec.model_json_schema()
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(spec.model_dump())


def test_missing_domain_is_explicit_uncertainty(project):
    project.domain = None
    spec = plan(project)
    assert spec.project_dna.domain.status == "DOMAIN_UNCERTAIN"
    assert spec.project_dna.domain.primary is None
    assert any("DOMAIN_UNCERTAIN" in item for item in spec.project_dna.unknowns)


@pytest.mark.parametrize("kind", ["cycle", "missing", "self", "duplicate-dependency"])
def test_invalid_graph_is_rejected(project, kind):
    if kind == "cycle":
        project.backlog[0].depends_on = ["lesson-draft"]
    elif kind == "missing":
        project.backlog[0].depends_on = ["missing"]
    elif kind == "self":
        project.backlog[0].depends_on = ["material-library"]
    else:
        project.backlog[1].depends_on = ["material-library", "material-library"]
    with pytest.raises(ValidationError):
        plan(project)


@pytest.mark.parametrize("field,value", [("name", "  "), ("id", "../escape"), ("extra", True)])
def test_invalid_input_is_rejected(project, field, value):
    payload = project.model_dump()
    payload[field] = value
    with pytest.raises(ValidationError):
        ProjectInput.model_validate(payload)


def test_duplicate_backlog_ids_are_rejected(project):
    payload = project.model_dump()
    payload["backlog"].append(copy.deepcopy(payload["backlog"][0]))
    with pytest.raises(ValidationError, match="unique"):
        ProjectInput.model_validate(payload)


@pytest.mark.parametrize(
    "kind",
    ["project", "evidence", "eval-coverage", "eval-capability", "criterion", "source", "policy"],
)
def test_ir_rejects_broken_references_and_policy_changes(project, kind):
    payload = plan(project).model_dump()
    if kind == "project":
        payload["capability_graph"]["project_id"] = "another-project"
    elif kind == "evidence":
        payload["decisions"][0]["evidence_ids"] = ["missing"]
    elif kind == "eval-coverage":
        payload["evals"].pop()
    elif kind == "eval-capability":
        payload["evals"][0]["capability_id"] = "missing"
    elif kind == "criterion":
        payload["evals"][0]["criterion"] = "Unrelated criterion"
    elif kind == "source":
        payload["capability_graph"]["capabilities"][0]["title"] = "Changed meaning"
    else:
        payload["permissions"]["execute_generated_code"] = True
    with pytest.raises(ValidationError):
        HarnessSpec.model_validate(payload)
