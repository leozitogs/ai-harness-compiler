"""Synthetic injected responses only: no provider, reserved corpus or real PO approval."""

import json

import pytest
from jsonschema import Draft202012Validator
from test_semantic_assessment import declaration, rubric
from test_semantic_contract_v4 import add_rejection, development

from ai_harness_compiler.models.evidence import canonical_project_digest
from ai_harness_compiler.models.semantic_analysis_v4 import SemanticAnalysisV4
from ai_harness_compiler.models.semantic_assessment_v4 import (
    SemanticAssessmentV4,
    SemanticHumanReviewV4,
    assess_v4,
)
from ai_harness_compiler.models.semantic_case_v3 import AssessmentCaseV3
from ai_harness_compiler.models.semantic_eval import CRITERIA
from ai_harness_compiler.models.semantic_flow_v4 import (
    SemanticFlowAuthorizationV4,
    SemanticFlowRequestV4,
    SemanticFlowResultV4,
)
from ai_harness_compiler.models.semantic_inventory_v4 import component_inventory_v4
from ai_harness_compiler.models.semantic_verification_v5 import (
    SemanticVerifierReportV5,
    audit_v5_program_digest,
)
from ai_harness_compiler.offline_schema_registry import OFFLINE_MODELS
from ai_harness_compiler.semantic_flow_runner_v4 import (
    run_semantic_flow_v4,
    save_semantic_review_v4,
    validate_semantic_flow_v4,
)
from ai_harness_compiler.semantic_generation_v4 import (
    analyze_v4,
    audit_schema_v5,
    audit_v5,
    generation_program_v4,
    generation_schema_v4,
)


def fixtures():
    _, _, case, analysis = development()
    case = AssessmentCaseV3.model_validate(
        case.model_dump() | {"expectations_approval": declaration().model_dump()}
    )
    return case, rubric(), analysis


def audit_proposal(analysis):
    return dict(
        analysis_sha256=analysis.snapshot_sha256,
        findings=[
            dict(
                finding_id=f.id,
                finding_sha256=f.sha256,
                source_atom_ids=f.source_atom_ids,
                support="supports",
                materiality="appropriate" if f.kind == "question" else "not-applicable",
                note="Synthetic evidence judgment",
            )
            for f in analysis.findings
        ],
        components=[
            c.identity.model_dump() | dict(support="supports", note="Synthetic component judgment")
            for c in component_inventory_v4(analysis)
        ],
        omissions=[],
        source_coverage=[
            dict(
                atom_id=s.atom_id,
                quote_sha256=s.quote_sha256,
                disposition="represented"
                if any(s.atom_id in f.source_atom_ids for f in analysis.findings)
                else "not-applicable",
                finding_ids=[f.id for f in analysis.findings if s.atom_id in f.source_atom_ids],
                omission_ids=[],
            )
            for s in analysis.sources
        ],
    )


def human_review(case, rubric_, analysis):
    proposal = audit_proposal(analysis)
    return SemanticHumanReviewV4(
        **declaration().model_dump(),
        case_sha256=case.snapshot_sha256,
        rubric_sha256=canonical_project_digest(rubric_.model_dump()),
        analysis_sha256=analysis.snapshot_sha256,
        checks=[
            dict(criterion=c, outcome="pass", note="Synthetic human judgment") for c in CRITERIA
        ],
        coverage=[dict(obligation_id="intent", finding_id="intent-requirement")],
        finding_support=[
            {k: v for k, v in f.items() if k != "support"} | dict(outcome="pass")
            for f in proposal["findings"]
        ],
        component_support=[
            {k: v for k, v in c.items() if k != "support"} | dict(outcome="pass")
            for c in proposal["components"]
        ],
    )


class FakeGenerator:
    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = []

    def generate_json(self, prompt, schema):
        self.calls.append((prompt, schema))
        response = self.responses.pop(0)
        if isinstance(response, Exception):
            raise response
        return json.dumps(response)


def request_pair(case, rubric_, analysis):
    request = SemanticFlowRequestV4(
        run_id="synthetic-run",
        case=case,
        rubric=rubric_,
        requested_model="synthetic.model-v1:fixture",
        generation_program_sha256=generation_program_v4(analysis.extraction),
        audit_program_sha256=audit_v5_program_digest(),
    )
    auth = SemanticFlowAuthorizationV4(
        **declaration().model_dump(), request_sha256=request.sha256, authorized=True
    )
    return request, auth


def report(analysis, proposal):
    return SemanticVerifierReportV5(
        analysis=analysis,
        proposal=proposal,
        requested_model="synthetic-model",
        program_sha256=audit_v5_program_digest(),
    )


def test_generator_and_auditor_dynamic_schemas_and_no_expectations():
    case, rubric_, analysis = fixtures()
    generator = FakeGenerator([analysis.proposal.model_dump(), audit_proposal(analysis)])
    generated = analyze_v4(analysis.extraction, generator)
    audited = audit_v5(generated, generator, "synthetic-model")
    assert generated == analysis
    assert audited.authority == "model-advisory"
    assert audited.semantic_status == "not-established"
    for (_, schema), response in zip(
        generator.calls, [analysis.proposal.model_dump(), audit_proposal(analysis)], strict=True
    ):
        Draft202012Validator.check_schema(schema)
        Draft202012Validator(schema).validate(response)
    for prompt, _ in generator.calls:
        assert "expectations_approval" not in prompt
        assert "required_content_rejection_pointers" not in prompt
        assert case.snapshot_sha256 not in prompt
        assert canonical_project_digest(rubric_.model_dump()) not in prompt
        assert "synthetic-fixture-human" not in prompt


@pytest.mark.parametrize(
    "mutation",
    [
        "analysis",
        "finding-hash",
        "component-hash",
        "source",
        "duplicate",
        "missing",
        "materiality",
        "hidden-link",
        "hidden-source",
        "aggregate",
    ],
)
def test_audit_rejects_structural_contradictions(mutation):
    _, _, analysis = fixtures()
    proposal = audit_proposal(analysis)
    if mutation == "analysis":
        proposal["analysis_sha256"] = "0" * 64
    elif mutation == "finding-hash":
        proposal["findings"][0]["finding_sha256"] = "0" * 64
    elif mutation == "component-hash":
        proposal["components"][0]["component_sha256"] = "0" * 64
    elif mutation == "source":
        proposal["components"][0]["source_atom_ids"] = ["unknown"]
    elif mutation == "duplicate":
        proposal["components"].append(proposal["components"][0])
    elif mutation == "missing":
        proposal["components"].pop()
    elif mutation == "materiality":
        proposal["findings"][0]["materiality"] = "appropriate"
    elif mutation == "hidden-link":
        next(r for r in proposal["source_coverage"] if r["finding_ids"])["finding_ids"] = []
    elif mutation == "hidden-source":
        proposal["source_coverage"].pop()
    else:
        proposal["components"][0]["support"] = "insufficient-evidence"
    with pytest.raises(ValueError):
        report(analysis, proposal)


def test_audit_omissions_preserve_all_citations_and_require_exact_ledger():
    _, _, analysis = fixtures()
    analysis = add_rejection(analysis)
    proposal = audit_proposal(analysis)
    atom = analysis.proposal.requirements[0].content.source_atom_ids[0]
    proposal["omissions"] = [
        dict(id="missing", kind="requirement", source_atom_ids=[atom], note="Synthetic omission")
    ]
    row = next(s for s in proposal["source_coverage"] if s["atom_id"] == atom)
    row.update(disposition="missing", omission_ids=["missing"])
    valid = report(analysis, proposal)
    assert "ignored-instruction" in row["finding_ids"]
    assert valid.analysis.disposition == "ready"
    row["omission_ids"] = []
    with pytest.raises(ValueError):
        report(analysis, proposal)


def test_components_distinguish_force_applicability_and_rejection():
    _, _, analysis = fixtures()
    data = add_rejection(analysis).model_dump()
    atom = next(a for a in analysis.extraction.atoms if a.kind == "acceptance-criterion")
    data["proposal"]["requirements"][0]["applicability"] = dict(
        text="Synthetic applicability", source_atom_ids=[atom.id]
    )
    changed = SemanticAnalysisV4.model_validate(data)
    components = component_inventory_v4(changed)
    assert {"content", "normative-force", "applicability", "rejection-reason"}.issubset(
        {c.name for c in components}
    )
    requirement = [c for c in components if c.finding_id == "intent-requirement"]
    assert len({c.identity.component_sha256 for c in requirement}) == 3
    assert next(c for c in requirement if c.name == "applicability").source_atom_ids == [atom.id]
    Draft202012Validator(audit_schema_v5(changed)).validate(audit_proposal(changed))


def test_independent_human_review_is_required_and_bound_to_all_components():
    case, rubric_, analysis = fixtures()
    assert assess_v4(case, rubric_, analysis).status == "not-run"
    review = human_review(case, rubric_, analysis)
    assessment = assess_v4(case, rubric_, analysis, review)
    assert assessment.status == "pass"
    assert assessment.compilation_eligibility == "not-authorized"
    assert assessment.model_qualification == "not-established"
    assert SemanticAssessmentV4.model_validate_json(assessment.model_dump_json()) == assessment
    for field in ["finding_support", "component_support", "coverage"]:
        data = review.model_dump()
        data[field].pop()
        with pytest.raises(ValueError):
            assess_v4(case, rubric_, analysis, SemanticHumanReviewV4.model_validate(data))
    with pytest.raises(ValueError):
        SemanticHumanReviewV4.model_validate(
            report(analysis, audit_proposal(analysis)).model_dump()
        )


@pytest.mark.parametrize(
    "mutation",
    [
        "case",
        "analysis",
        "rubric",
        "component-source",
        "component-hash",
        "finding-hash",
        "duplicate",
    ],
)
def test_human_review_cannot_transfer_approval(mutation):
    case, rubric_, analysis = fixtures()
    data = human_review(case, rubric_, analysis).model_dump()
    if mutation in {"case", "analysis", "rubric"}:
        data[f"{mutation}_sha256"] = "0" * 64
    elif mutation == "component-source":
        data["component_support"][0]["source_atom_ids"] = ["unknown"]
    elif mutation == "component-hash":
        data["component_support"][0]["component_sha256"] = "0" * 64
    elif mutation == "finding-hash":
        data["finding_support"][0]["finding_sha256"] = "0" * 64
    else:
        data["component_support"].append(data["component_support"][0])
    with pytest.raises(ValueError):
        assess_v4(case, rubric_, analysis, SemanticHumanReviewV4.model_validate(data))


def test_negative_component_cannot_be_overridden_by_human_positive_aggregate():
    case, rubric_, analysis = fixtures()
    data = human_review(case, rubric_, analysis).model_dump()
    data["component_support"][0]["outcome"] = "fail"
    next(c for c in data["checks"] if c["criterion"] == "citation-support")["outcome"] = "fail"
    with pytest.raises(ValueError):
        assess_v4(case, rubric_, analysis, SemanticHumanReviewV4.model_validate(data))
    finding_id = data["component_support"][0]["finding_id"]
    next(f for f in data["finding_support"] if f["finding_id"] == finding_id)["outcome"] = "fail"
    result = assess_v4(case, rubric_, analysis, SemanticHumanReviewV4.model_validate(data))
    assert {"finding-support-fail", "component-support-fail"}.issubset(
        {f.code for f in result.failures}
    )


def test_applicability_source_cannot_cover_normative_content():
    case, rubric_, analysis = fixtures()
    data = analysis.model_dump()
    atom = next(a for a in analysis.extraction.atoms if a.kind == "constraint")
    data["proposal"]["requirements"][0]["applicability"] = dict(
        text=atom.quote, source_atom_ids=[atom.id]
    )
    analysis = SemanticAnalysisV4.model_validate(data)
    case_data = case.model_dump()
    case_data["obligations"][0].update(source_pointer=atom.pointer, quote=atom.quote)
    case = AssessmentCaseV3.model_validate(case_data)
    assert "obligation-missing" in {f.code for f in assess_v4(case, rubric_, analysis).failures}
    with pytest.raises(ValueError):
        assess_v4(case, rubric_, analysis, human_review(case, rubric_, analysis))


def test_missing_rejection_and_disposition_failures_are_both_retained():
    case, rubric_, analysis = fixtures()
    case_data = case.model_dump()
    case_data.update(
        expected_behavior="blocked", required_content_rejection_pointers=["/conception"]
    )
    case_data["obligations"][0]["disposition"] = "required-question"
    case = AssessmentCaseV3.model_validate(case_data)
    result = assess_v4(case, rubric_, analysis)
    assert {"disposition-mismatch", "content-rejection-missing"}.issubset(
        {f.code for f in result.failures}
    )


def test_single_use_flow_replay_and_persistent_human_review(tmp_path):
    case, rubric_, analysis = fixtures()
    request, authorization = request_pair(case, rubric_, analysis)
    generator = FakeGenerator([analysis.proposal.model_dump(), audit_proposal(analysis)])
    result = run_semantic_flow_v4(tmp_path, request, authorization, lambda: generator)
    assert result.status == "completed"
    assert result.assessment.status == "not-run"
    assert len(generator.calls) == len(result.calls) == 2
    assert validate_semantic_flow_v4(tmp_path, request.run_id) == result
    assessment = save_semantic_review_v4(
        tmp_path, request.run_id, human_review(case, rubric_, analysis)
    )
    assert assessment.status == "pass"
    assert validate_semantic_flow_v4(tmp_path, request.run_id).assessment.status == "not-run"
    with pytest.raises(FileExistsError):
        run_semantic_flow_v4(tmp_path, request, authorization, lambda: pytest.fail("No replay"))
    with pytest.raises(FileExistsError):
        save_semantic_review_v4(tmp_path, request.run_id, human_review(case, rubric_, analysis))
    directory = tmp_path / ".factory" / "semantic-v4-runs" / request.run_id
    assert not list(directory.glob("*prompt*"))
    assert list(directory.glob("human-assessment-*.json"))


@pytest.mark.parametrize("stage", ["factory", "analysis", "audit"])
def test_first_failure_stops_and_preserves_charged_calls(tmp_path, stage):
    case, rubric_, analysis = fixtures()
    request, authorization = request_pair(case, rubric_, analysis)
    secret = RuntimeError("private-provider-error-do-not-save")
    generator = FakeGenerator(
        [secret] if stage == "analysis" else [analysis.proposal.model_dump(), secret]
    )

    def factory():
        if stage == "factory":
            raise secret
        return generator

    result = run_semantic_flow_v4(tmp_path, request, authorization, factory)
    assert result.failure_code == f"{stage}-failed"
    assert len(result.calls) == {"factory": 0, "analysis": 1, "audit": 2}[stage]
    assert (result.analysis is not None) == (stage == "audit")
    assert validate_semantic_flow_v4(tmp_path, request.run_id) == result
    assert all(
        "private-provider-error-do-not-save" not in p.read_text() for p in tmp_path.rglob("*.json")
    )
    with pytest.raises(FileExistsError):
        run_semantic_flow_v4(tmp_path, request, authorization, factory)


@pytest.mark.parametrize("gate", ["authorization", "case-approval", "rubric-approval", "program"])
def test_gates_run_before_constructing_generator(tmp_path, gate):
    case, rubric_, analysis = fixtures()
    if gate == "case-approval":
        case = AssessmentCaseV3.model_validate(case.model_dump() | {"expectations_approval": None})
    if gate == "rubric-approval":
        rubric_ = rubric(False)
    request, authorization = request_pair(case, rubric_, analysis)
    if gate == "authorization":
        authorization.request_sha256 = "0" * 64
    if gate == "program":
        # model_construct simulates mutated/unvalidated caller data.
        request = request.model_copy(update={"generation_program_sha256": "0" * 64})
    with pytest.raises(ValueError):
        run_semantic_flow_v4(tmp_path, request, authorization, lambda: pytest.fail("Gate bypass"))
    assert not (tmp_path / ".factory").exists()


@pytest.mark.parametrize("mutation", ["response", "analysis", "call", "claim", "path"])
def test_offline_replay_detects_tampering(tmp_path, mutation):
    case, rubric_, analysis = fixtures()
    request, authorization = request_pair(case, rubric_, analysis)
    generator = FakeGenerator([analysis.proposal.model_dump(), audit_proposal(analysis)])
    result = run_semantic_flow_v4(tmp_path, request, authorization, lambda: generator)
    directory = tmp_path / ".factory" / "semantic-v4-runs" / request.run_id
    if mutation == "path":
        with pytest.raises(ValueError):
            validate_semantic_flow_v4(tmp_path, "../escape")
        return
    path = {
        "response": directory / "analysis-response.json",
        "analysis": directory / "analysis.json",
        "call": directory / "analysis-call.json",
        "claim": tmp_path / ".factory" / "semantic-v4-claims" / f"{request.sha256}.json",
    }[mutation]
    path.write_text("{}")
    with pytest.raises(ValueError):
        validate_semantic_flow_v4(tmp_path, request.run_id)
    if mutation == "call":
        data = result.model_dump()
        data["calls"][0]["prompt_sha256"] = "0" * 64
        (directory / "result.json").write_text(json.dumps(data))
        path.write_text(json.dumps(data["calls"][0]))
        with pytest.raises(ValueError, match="exact input prompt"):
            validate_semantic_flow_v4(tmp_path, request.run_id)


def test_result_cannot_claim_completed_or_semantically_approved_without_artifacts(tmp_path):
    case, rubric_, analysis = fixtures()
    request, authorization = request_pair(case, rubric_, analysis)
    result = run_semantic_flow_v4(
        tmp_path, request, authorization, lambda: FakeGenerator([RuntimeError()])
    )
    data = result.model_dump()
    data.update(status="completed", failure_code=None)
    with pytest.raises(ValueError):
        SemanticFlowResultV4.model_validate(data)
    Draft202012Validator.check_schema(generation_schema_v4(analysis.extraction))


def test_supported_but_inappropriate_question_fails_uncertainty_only():
    case, rubric_, analysis = fixtures()
    data = analysis.model_dump()
    data["proposal"]["project_analysis"]["issues"] = [
        dict(
            kind="question",
            text="Synthetic extra question?",
            context_indices=[0],
            rationale="Synthetic",
            impact="rule",
        )
    ]
    analysis = SemanticAnalysisV4.model_validate(data)
    review_data = human_review(case, rubric_, analysis).model_dump()
    question = next(f for f in analysis.findings if f.kind == "question")
    next(f for f in review_data["finding_support"] if f["finding_id"] == question.id)[
        "materiality"
    ] = "inappropriate"
    result = assess_v4(case, rubric_, analysis, SemanticHumanReviewV4.model_validate(review_data))
    assert next(c for c in result.checks if c.criterion == "citation-support").outcome == "pass"
    assert next(c for c in result.checks if c.criterion == "uncertainty").outcome == "fail"
    assert "inappropriate-question" in {f.code for f in result.failures}
    # Independent disposition mismatch is retained rather than overwritten.
    assert "disposition-mismatch" in {f.code for f in result.failures}


@pytest.mark.parametrize("gate", ["case", "rubric"])
def test_passing_output_judgments_do_not_replace_expectations_approval(gate):
    case, rubric_, analysis = fixtures()
    if gate == "case":
        case = AssessmentCaseV3.model_validate(case.model_dump() | {"expectations_approval": None})
    else:
        rubric_ = rubric(False)
    result = assess_v4(case, rubric_, analysis, human_review(case, rubric_, analysis))
    assert all(c.outcome == "pass" for c in result.checks)
    assert result.status == "not-run"


def test_invalid_generated_provenance_stops_before_audit(tmp_path):
    case, rubric_, analysis = fixtures()
    request, authorization = request_pair(case, rubric_, analysis)
    data = analysis.proposal.model_dump()
    data["requirements"][0]["content"]["source_atom_ids"] = ["unknown"]
    generator = FakeGenerator([data, audit_proposal(analysis)])
    result = run_semantic_flow_v4(tmp_path, request, authorization, lambda: generator)
    assert result.failure_code == "analysis-failed"
    assert len(generator.calls) == 1
    assert result.analysis is None


def test_existing_directory_is_preserved_and_consumes_claim(tmp_path):
    case, rubric_, analysis = fixtures()
    request, authorization = request_pair(case, rubric_, analysis)
    directory = tmp_path / ".factory" / "semantic-v4-runs" / request.run_id
    directory.mkdir(parents=True)
    marker = directory / "keep.txt"
    marker.write_text("preserve")
    with pytest.raises(FileExistsError):
        run_semantic_flow_v4(tmp_path, request, authorization, lambda: pytest.fail("No overwrite"))
    assert marker.read_text() == "preserve"
    assert (tmp_path / ".factory" / "semantic-v4-claims" / f"{request.sha256}.json").is_file()


def test_all_new_flow_schemas_roundtrip_validated_artifacts(tmp_path):
    case, rubric_, analysis = fixtures()
    request, authorization = request_pair(case, rubric_, analysis)
    generator = FakeGenerator([analysis.proposal.model_dump(), audit_proposal(analysis)])
    result = run_semantic_flow_v4(tmp_path, request, authorization, lambda: generator)
    review = human_review(case, rubric_, analysis)
    values = {
        "semantic-verifier-proposal-v5": result.audit.proposal,
        "semantic-verifier-report-v5": result.audit,
        "semantic-human-review-v4": review,
        "semantic-assessment-v4": assess_v4(case, rubric_, analysis, review),
        "semantic-flow-request-v4": request,
        "semantic-flow-authorization-v4": authorization,
        "semantic-flow-result-v4": result,
    }
    for name, value in values.items():
        model = OFFLINE_MODELS[name]
        Draft202012Validator(model.model_json_schema()).validate(value.model_dump(mode="json"))
        assert model.model_validate_json(value.model_dump_json()) == value
