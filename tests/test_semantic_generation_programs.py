"""Program isolation and unsmoothed failures; synthetic responses are not model efficacy."""

from pathlib import Path

import pytest
from test_semantic_assessment import declaration
from test_semantic_flow_v4 import FakeGenerator, audit_proposal, fixtures, request_pair

from ai_harness_compiler.grounding import extract_grounding
from ai_harness_compiler.models.compact_analysis import compact_context
from ai_harness_compiler.models.semantic_analysis_v4 import SemanticAnalysisV4
from ai_harness_compiler.models.semantic_campaign import SemanticCampaignRequestV1
from ai_harness_compiler.models.semantic_flow_v4 import (
    SemanticFlowAuthorizationV4,
    SemanticFlowRequestV4,
)
from ai_harness_compiler.semantic_flow_runner_v4 import (
    run_semantic_flow_v4,
    validate_semantic_flow_v4,
)
from ai_harness_compiler.semantic_generation_programs import (
    analyze_program,
    program_digest,
    program_prompt,
    resolve_program,
)
from ai_harness_compiler.semantic_generation_v4 import (
    generation_program_v4,
    generation_prompt_v4,
    generation_schema_v4,
)

ROOT = Path(__file__).resolve().parents[1]


def request_for(case, rubric, analysis, version):
    request, _ = request_pair(case, rubric, analysis)
    data = request.model_dump()
    data["generation_program_sha256"] = program_digest(analysis.extraction, version)
    request = SemanticFlowRequestV4.model_validate(data)
    auth = SemanticFlowAuthorizationV4(
        **declaration().model_dump(), request_sha256=request.sha256, authorized=True
    )
    return request, auth


def test_legacy_program_and_eight_historical_request_hashes_are_unchanged():
    _, _, analysis = fixtures()
    extraction = analysis.extraction
    digest = generation_program_v4(extraction)
    assert program_digest(extraction, "semantic-composition/v4.0") == digest
    assert program_prompt(extraction, digest) == generation_prompt_v4(extraction)
    path = ROOT / "evals/understanding/v4/development-campaign/request.json"
    request = SemanticCampaignRequestV1.model_validate_json(path.read_bytes())
    assert request.sha256 == "a64cb6e7a779d4c5c201db9beb54238e793604fc564eb963b3987e37ffd88236"
    for flow in request.flows:
        assert flow.generation_program_sha256 == generation_program_v4(
            extract_grounding(flow.case.project)
        )


def test_candidate_changes_instructions_but_not_source_packet_schema_or_expectations():
    case, _, analysis = fixtures()
    extraction = analysis.extraction
    old = generation_program_v4(extraction)
    candidate = program_digest(extraction, "semantic-composition/v4.1")
    assert candidate != old
    legacy_prompt = program_prompt(extraction, old)
    new_prompt = program_prompt(extraction, candidate)
    assert legacy_prompt.split("\nINPUT DATA:\n")[1] == new_prompt.split("\nINPUT DATA:\n")[1]
    generator = FakeGenerator([analysis.proposal.model_dump()])
    result = analyze_program(extraction, generator, candidate)
    assert result == analysis
    assert generator.calls == [(new_prompt, generation_schema_v4(extraction))]
    assert case.expectations_approval.note not in new_prompt
    assert "expectations_approval" not in new_prompt


@pytest.mark.parametrize("version", ["unknown", "", "semantic-composition/v5"])
def test_unknown_versions_cannot_supply_arbitrary_prompts(version):
    _, _, analysis = fixtures()
    with pytest.raises(ValueError):
        program_digest(analysis.extraction, version)


def test_unknown_or_other_input_program_hash_rejected_before_generator(tmp_path):
    case, rubric, analysis = fixtures()
    request, auth = request_for(case, rubric, analysis, "semantic-composition/v4.1")
    other = case.project.model_copy(deep=True)
    other.backlog[0].acceptance_criteria.append("Another independently stated condition.")
    wrong_digest = program_digest(extract_grounding(other), "semantic-composition/v4.1")
    for digest in ["0" * 64, wrong_digest]:
        with pytest.raises(ValueError):
            resolve_program(analysis.extraction, digest)
        with pytest.raises(ValueError):
            SemanticFlowRequestV4.model_validate(
                request.model_dump() | dict(generation_program_sha256=digest)
            )
    bad_auth = auth.model_copy(update={"request_sha256": "0" * 64})
    with pytest.raises(ValueError):
        run_semantic_flow_v4(tmp_path, request, bad_auth, lambda: pytest.fail("No generator"))
    assert not (tmp_path / ".factory").exists()


@pytest.mark.parametrize("version", ["semantic-composition/v4.0", "semantic-composition/v4.1"])
def test_both_programs_run_and_replay_exact_stage_debits_without_human_pass(tmp_path, version):
    case, rubric, analysis = fixtures()
    request, auth = request_for(case, rubric, analysis, version)
    generator = FakeGenerator([analysis.proposal.model_dump(), audit_proposal(analysis)])
    result = run_semantic_flow_v4(tmp_path, request, auth, lambda: generator)
    assert result.status == "completed" and result.assessment.status == "not-run"
    assert generator.calls[0] == (
        program_prompt(analysis.extraction, request.generation_program_sha256),
        generation_schema_v4(analysis.extraction),
    )
    assert validate_semantic_flow_v4(tmp_path, request.run_id) == result
    assert result.compilation_eligibility == "not-authorized"
    assert result.model_qualification == "not-established"


def test_relational_components_and_unconditional_obligation_remain_separate(tmp_path):
    case, rubric, old = fixtures()
    project = case.project.model_copy(deep=True)
    project.backlog[0].acceptance_criteria = [
        "A technician must acknowledge the sample before archiving."
    ]
    extraction = extract_grounding(project)
    atom = next(a for a in extraction.atoms if a.kind == "acceptance-criterion")
    data = old.proposal.model_dump()
    data["project_analysis"]["criteria"] = [
        dict(
            source_atom_id=atom.id,
            kind="business-rule",
            condition=dict(text="Archiving the sample.", source_atom_ids=[atom.id]),
            outcome=dict(
                text="A technician must acknowledge the sample first.", source_atom_ids=[atom.id]
            ),
            note="Synthetic necessary temporal relation; not a grant to archive.",
        )
    ]
    analysis = SemanticAnalysisV4(extraction=extraction, proposal=data)
    changed = case.model_copy(deep=True)
    changed.project = project
    changed.obligations = [
        dict(id="relation", source_pointer=atom.pointer, quote=atom.quote, disposition="rule")
    ]
    # Revalidate data updates instead of bypassing model invariants via copy.
    changed = type(case).model_validate(changed.model_dump())
    req, auth = request_for(changed, rubric, analysis, "semantic-composition/v4.1")
    generator = FakeGenerator([analysis.proposal.model_dump(), audit_proposal(analysis)])
    result = run_semantic_flow_v4(tmp_path, req, auth, lambda: generator)
    assert result.status == "completed" and result.assessment.status == "not-run"
    rule = next(f for f in result.analysis.findings if f.kind == "rule")
    assert rule.condition and rule.outcome and len(rule.component_bindings) == 2
    assert result.analysis.proposal.requirements[0].applicability is None
    assert result.analysis.proposal.requirements[0].content == old.proposal.requirements[0].content


@pytest.mark.parametrize(
    "impact,disposition", [("implementation-detail", "ready"), ("rule", "blocked")]
)
def test_candidate_never_rewrites_model_question_impact_to_force_ready(
    tmp_path, impact, disposition
):
    case, rubric, old = fixtures()
    proposal = old.proposal.model_dump()
    index = next(
        i for i, a in enumerate(compact_context(old.extraction)) if a.pointer == "/conception"
    )
    proposal["project_analysis"]["issues"] = [
        dict(
            kind="question",
            text="Who fills the stated role?",
            context_indices=[index],
            impact=impact,
            rationale="Synthetic role-holder detail for contract tests.",
        )
    ]
    analysis = SemanticAnalysisV4(extraction=old.extraction, proposal=proposal)
    req, auth = request_for(case, rubric, analysis, "semantic-composition/v4.1")
    generator = FakeGenerator([analysis.proposal.model_dump(), audit_proposal(analysis)])
    result = run_semantic_flow_v4(tmp_path, req, auth, lambda: generator)
    assert result.analysis.disposition == disposition
    assert result.analysis.proposal.project_analysis.issues[0].impact == impact
    assert result.assessment.status == ("fail" if impact == "rule" else "not-run")


def test_one_campaign_cannot_mix_programs_to_hide_an_experiment_change():
    request = SemanticCampaignRequestV1.model_validate_json(
        (ROOT / "evals/understanding/v4/development-campaign/request.json").read_bytes()
    )
    data = request.model_dump()
    flow = request.flows[1]
    data["flows"][1]["generation_program_sha256"] = program_digest(
        extract_grounding(flow.case.project), "semantic-composition/v4.1"
    )
    with pytest.raises(ValueError):
        SemanticCampaignRequestV1.model_validate(data)


def test_candidate_supervision_uses_fixed_local_workers_and_replays(tmp_path, monkeypatch):
    from test_supervised_transport import prepare

    from ai_harness_compiler.models.supervised_transport import SupervisedFlowAuthorizationV1
    from ai_harness_compiler.supervised_semantic_flow import (
        prepare_supervised_flow,
        run_supervised_flow,
        validate_supervised_flow,
    )

    root, old, _ = prepare(tmp_path, monkeypatch)
    extraction = extract_grounding(old.flow.case.project)
    nested = SemanticFlowRequestV4.model_validate(
        old.flow.model_dump()
        | dict(generation_program_sha256=program_digest(extraction, "semantic-composition/v4.1"))
    )
    request = prepare_supervised_flow(root, nested, old.limits)
    authorization = SupervisedFlowAuthorizationV1(
        **declaration().model_dump(), request_sha256=request.sha256, authorized=True
    )
    result = run_supervised_flow(root, request, authorization)
    assert result.status == "completed" and result.flow_result.assessment.status == "not-run"
    assert all(r.root_reaped for r in result.receipts)
    assert validate_supervised_flow(root, nested.run_id) == result


def test_candidate_global_campaign_replays_without_changing_approved_cases(tmp_path, monkeypatch):
    from test_semantic_campaign import prepare

    from ai_harness_compiler.models.semantic_campaign import SemanticCampaignAuthorizationV1
    from ai_harness_compiler.semantic_campaign import run_campaign, validate_campaign

    root, old, _, _, seen, _ = prepare(tmp_path, monkeypatch)
    data = old.model_dump()
    for flow in data["flows"]:
        extraction = extract_grounding(SemanticFlowRequestV4.model_validate(flow).case.project)
        flow["generation_program_sha256"] = program_digest(extraction, "semantic-composition/v4.1")
    request = SemanticCampaignRequestV1.model_validate(data)
    authorization = SemanticCampaignAuthorizationV1(
        **declaration().model_dump(), request_sha256=request.sha256, authorized=True
    )
    result = run_campaign(root, request, authorization)
    assert len(seen) == 4 and result.status == "completed"
    assert all(a.case == b.case for a, b in zip(request.flows, old.flows, strict=True))
    assert all(r.assessment.status == "not-run" for r in result.results)
    assert validate_campaign(root, request.campaign_id) == result
