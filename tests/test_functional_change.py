"""Synthetic functional planning and review declarations; no actual business acceptance."""

import hashlib
import runpy
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

from ai_harness_compiler.functional_changes import (
    FunctionalReadinessV1,
    assess_functional_change,
    validate_change_worklog,
)
from ai_harness_compiler.models.evidence import canonical_project_digest
from ai_harness_compiler.models.functional_change import (
    BusinessExampleV1,
    ChangeRuleV1,
    ChangeWorkLogV1,
    FunctionalChangeReviewV1,
    FunctionalChangeV1,
    QuestionDecisionV1,
    RuleConfirmationV1,
)
from ai_harness_compiler.models.understanding import UnderstandingRequest, reference_value

ROOT = Path(__file__).resolve().parents[1]
DECLARATION = dict(
    reviewer="synthetic-reviewer", note="Synthetic declaration, not actual PO acceptance."
)


@pytest.fixture
def change(project):
    project.domain = None
    project.name = "Synthetic batch registry"
    project.conception = "Organize batches. Handling more than three entries is undefined."
    rule_text = "Mark a batch complete if and only if it contains exactly three entries."
    project.backlog[0].acceptance_criteria = [rule_text]
    source = UnderstandingRequest.model_validate(
        dict(
            original_input=project,
            original_sha256=canonical_project_digest(project.model_dump()),
            references=[
                dict(
                    id="rule-source",
                    project_id=project.id,
                    pointer="/backlog/0/acceptance_criteria/0",
                    value=rule_text,
                ),
                dict(
                    id="intent-source",
                    project_id=project.id,
                    pointer="/conception",
                    value=project.conception,
                ),
            ],
        )
    )
    rule = ChangeRuleV1(
        id="batch-rule", statement=rule_text, origin="declared", source_refs=["rule-source"]
    )
    confirmation = RuleConfirmationV1(
        **DECLARATION,
        rule_id=rule.id,
        rule_sha256=rule.sha256,
        source_sha256=canonical_project_digest(source.model_dump()),
    )
    examples = [
        BusinessExampleV1(
            id=f"example-{kind}",
            rule_id=rule.id,
            kind=kind,
            given=f"A batch with {count} entries.",
            when="Evaluate completion.",
            then=f"Completion is {result}.",
        )
        for kind, count, result in [
            ("success", 3, "true"),
            ("failure", 4, "false"),
            ("boundary", 2, "false"),
        ]
    ]
    return FunctionalChangeV1.model_validate(
        dict(
            id="batch-completion",
            revision=1,
            source=source,
            capability_ids=[project.backlog[0].id],
            intent="Represent batch completion without running the workflow.",
            rules=[rule],
            confirmations=[confirmation],
            examples=examples,
            questions=[
                dict(
                    id="overflow-question",
                    text="How should a batch with more than three entries be handled?",
                    rule_ids=[rule.id],
                    source_refs=["rule-source", "intent-source"],
                    owner="product-owner",
                    impact="outcome",
                )
            ],
            requirements=[dict(id="completion-requirement", text=rule_text, rule_ids=[rule.id])],
            scenarios=[
                dict(
                    id=f"scenario-{e.kind}",
                    requirement_id="completion-requirement",
                    example_id=e.id,
                    test_ref="tests/test_functional_change.py::test_missing_example_kind_is_explicit_not_assumed_covered",
                )
                for e in examples
            ],
        )
    )


def without_questions(change):
    return FunctionalChangeV1.model_validate(change.model_dump() | dict(questions=[]))


def review_for(change, **updates):
    return FunctionalChangeReviewV1.model_validate(
        dict(
            **DECLARATION,
            project_id=change.source.original_input.id,
            change_id=change.id,
            revision=change.revision,
            content_sha256=change.sha256,
            decision="approved",
        )
        | updates
    )


def test_explicit_material_question_preserves_owner_and_blocks_even_with_approval(change):
    result = assess_functional_change(change, review_for(change))
    assert result.status == "blocked"
    assert [(b.code, b.reference) for b in result.blockers] == [
        ("unresolved-question", "overflow-question")
    ]
    assert result.change.questions[0].owner == "product-owner"
    assert (
        result.test_execution_status == "not-run"
        and result.compilation_eligibility == "not-authorized"
    )


def test_a_bound_human_decision_resolves_only_its_exact_question(change):
    question = change.questions[0]
    decision = QuestionDecisionV1(
        **DECLARATION,
        question_id=question.id,
        question_sha256=question.sha256,
        source_sha256=canonical_project_digest(change.source.model_dump()),
        answer="Retain the batch for manual correction; do not declare it complete.",
    )
    resolved = FunctionalChangeV1.model_validate(change.model_dump() | dict(decisions=[decision]))
    assert assess_functional_change(resolved).status == "ready-for-human-review"
    assert assess_functional_change(resolved, review_for(resolved)).status == "approved"
    data = resolved.model_dump()
    data["questions"][0]["text"] = "A different business question."
    with pytest.raises(ValueError, match="Question decision"):
        FunctionalChangeV1.model_validate(data)


def test_hypothesis_and_unconfirmed_rule_cannot_be_promoted_by_overall_review(change):
    data = without_questions(change).model_dump()
    data["rules"][0]["origin"] = "hypothesis"
    data["confirmations"] = []
    draft = FunctionalChangeV1.model_validate(data)
    assert "unconfirmed-rule" in [
        b.code for b in assess_functional_change(draft, review_for(draft)).blockers
    ]


@pytest.mark.parametrize("kind", ["success", "failure", "boundary"])
def test_missing_example_kind_is_explicit_not_assumed_covered(change, kind):
    data = without_questions(change).model_dump()
    data["examples"] = [e for e in data["examples"] if e["kind"] != kind]
    data["scenarios"] = [s for s in data["scenarios"] if s["example_id"] != f"example-{kind}"]
    draft = FunctionalChangeV1.model_validate(data)
    assert ("missing-example", f"batch-rule:{kind}") in [
        (b.code, b.reference) for b in assess_functional_change(draft).blockers
    ]
    data["exemptions"] = [
        dict(
            rule_id="batch-rule",
            kind=kind,
            reason="Synthetic applicability justification requiring human review.",
        )
    ]
    exempted = FunctionalChangeV1.model_validate(data)
    assert assess_functional_change(exempted).status == "ready-for-human-review"


def test_exempting_every_kind_cannot_replace_all_concrete_examples(change):
    data = without_questions(change).model_dump() | dict(
        examples=[],
        scenarios=[],
        exemptions=[
            dict(rule_id="batch-rule", kind=k, reason="Synthetic exemption.")
            for k in ["success", "failure", "boundary"]
        ],
    )
    draft = FunctionalChangeV1.model_validate(data)
    assert ("missing-example", "batch-rule:concrete") in [
        (b.code, b.reference) for b in assess_functional_change(draft).blockers
    ]


@pytest.mark.parametrize(
    "mutation",
    [
        "source-text",
        "rule-text",
        "source-remap",
        "foreign-capability",
        "rule-ref",
        "example-ref",
        "scenario-ref",
        "duplicate",
        "duplicate-confirmation",
        "duplicate-exemption",
        "question-sources",
    ],
)
def test_broken_provenance_and_cross_references_are_rejected(change, mutation):
    data = change.model_dump()
    if mutation == "source-text":
        data["source"]["references"][0]["value"] = "Altered source"
    elif mutation == "rule-text":
        data["rules"][0]["statement"] = "A different rule"
    elif mutation == "source-remap":
        data["source"]["references"][0]["pointer"] = "/conception"
        data["source"]["references"][0]["value"] = data["source"]["original_input"]["conception"]
    elif mutation == "foreign-capability":
        data["capability_ids"] = ["foreign-project-story"]
    elif mutation == "rule-ref":
        data["requirements"][0]["rule_ids"] = ["missing-rule"]
    elif mutation == "example-ref":
        data["examples"][0]["rule_id"] = "missing-rule"
    elif mutation == "scenario-ref":
        data["scenarios"][0]["example_id"] = "missing-example"
    elif mutation == "duplicate":
        data["examples"][0]["id"] = "batch-rule"
    elif mutation == "duplicate-confirmation":
        data["confirmations"] *= 2
    elif mutation == "duplicate-exemption":
        data["exemptions"] = [
            dict(rule_id="batch-rule", kind="success", reason="Not applicable.")
        ] * 2
    elif mutation == "question-sources":
        data["questions"][0]["source_refs"] = ["intent-source"]
    with pytest.raises(ValueError):
        FunctionalChangeV1.model_validate(data)


def test_missing_requirement_and_scenario_remain_blockers(change):
    draft = FunctionalChangeV1.model_validate(
        without_questions(change).model_dump() | dict(requirements=[], scenarios=[])
    )
    codes = [b.code for b in assess_functional_change(draft).blockers]
    assert codes.count("missing-requirement") == 1 and codes.count("unmapped-example") == 3


@pytest.mark.parametrize(
    "field,value",
    [
        ("project_id", "another-project"),
        ("change_id", "another-change"),
        ("revision", 2),
        ("content_sha256", "0" * 64),
    ],
)
def test_approval_from_another_scope_is_visible_as_stale(change, field, value):
    ready = without_questions(change)
    result = assess_functional_change(ready, review_for(ready, **{field: value}))
    assert result.status == "blocked" and result.blockers[0].code == "stale-review"


def test_semantic_content_edit_invalidates_old_review_but_progress_does_not(change):
    ready = without_questions(change)
    review = review_for(ready)
    initial = ready.sha256
    log = ChangeWorkLogV1(change_sha256=initial)
    validate_change_worklog(ready, log)
    log.prepared_scenario_ids.append("scenario-boundary")
    validate_change_worklog(ready, log)
    assert ready.sha256 == initial and assess_functional_change(ready, review).status == "approved"
    data = ready.model_dump()
    data["examples"][0]["given"] = "A different synthetic example."
    changed = FunctionalChangeV1.model_validate(data)
    assert changed.sha256 != initial
    assert assess_functional_change(changed, review).status == "blocked"
    with pytest.raises(ValueError):
        validate_change_worklog(changed, log)


def test_worklog_cannot_invent_a_prepared_scenario_or_test_pass(change):
    with pytest.raises(ValueError):
        validate_change_worklog(
            change, ChangeWorkLogV1(change_sha256=change.sha256, prepared_scenario_ids=["invented"])
        )
    with pytest.raises(ValueError):
        ChangeWorkLogV1.model_validate(dict(change_sha256=change.sha256, test_status="pass"))


def test_nonblocking_question_is_preserved_without_inventing_a_business_gate(change):
    data = change.model_dump()
    data["questions"][0]["impact"] = "implementation-detail"
    draft = FunctionalChangeV1.model_validate(data)
    assert assess_functional_change(draft).status == "ready-for-human-review"
    assert len(draft.questions) == 1


@pytest.mark.parametrize("mutation", ["status", "blockers", "tests", "compilation"])
def test_serialized_readiness_cannot_hide_blockers_or_claim_execution(change, mutation):
    data = assess_functional_change(change).model_dump()
    if mutation == "status":
        data["status"] = "approved"
    elif mutation == "blockers":
        data["blockers"] = []
    elif mutation == "tests":
        data["test_execution_status"] = "pass"
    else:
        data["compilation_eligibility"] = "authorized"
    with pytest.raises(ValueError):
        FunctionalReadinessV1.model_validate(data)


def test_synthetic_contracts_roundtrip_and_rejection_is_not_acceptance(change):
    ready = without_questions(change)
    rejected = assess_functional_change(ready, review_for(ready, decision="rejected"))
    assert rejected.status == "rejected"
    for model in [
        change,
        review_for(change),
        rejected,
        ChangeWorkLogV1(change_sha256=change.sha256),
    ]:
        assert type(model).model_validate_json(model.model_dump_json()) == model
        Draft202012Validator(type(model).model_json_schema()).validate(
            model.model_dump(mode="json")
        )


@pytest.mark.parametrize(
    "locator",
    [
        "../tests/test_x.py::test_x",
        "/tests/test_x.py::test_x",
        "tests/test_x.py;echo secret",
        "tests/test_x.py::test_x --output result",
        "tests/../test_x.py::test_x",
    ],
)
def test_test_locator_cannot_be_a_command_or_escape(change, locator):
    data = change.model_dump()
    data["scenarios"][0]["test_ref"] = locator
    with pytest.raises(ValueError):
        FunctionalChangeV1.model_validate(data)


def test_offline_command_preserves_inputs_and_refuses_overwrite_and_escape(
    change, tmp_path, capsys
):
    main = runpy.run_path(str(ROOT / "scripts/inspect_functional_change.py"))["main"]
    path = tmp_path / "change.json"
    path.write_text(change.model_dump_json(), encoding="utf-8")
    original = hashlib.sha256(path.read_bytes()).hexdigest()
    args = ["--repository", str(tmp_path), "--input", "change.json", "--output", "report.json"]
    main(args)
    result = FunctionalReadinessV1.model_validate_json((tmp_path / "report.json").read_bytes())
    assert result.status == "blocked" and "tests not-run" in capsys.readouterr().out
    assert hashlib.sha256(path.read_bytes()).hexdigest() == original
    with pytest.raises(FileExistsError):
        main(args)
    with pytest.raises(ValueError):
        main(args[:-1] + ["../escaped.json"])
    with pytest.raises(FileExistsError):
        main(args[:-1] + ["change.json"])


def test_offline_command_bounds_input_without_importing_or_executing_it(tmp_path):
    ns = runpy.run_path(str(ROOT / "scripts/inspect_functional_change.py"))
    path = tmp_path / "oversized.json"
    path.write_bytes(b"x" * (ns["MAX_INPUT_BYTES"] + 1))
    with pytest.raises(ValueError, match="byte limit"):
        ns["_read"](path)


def test_committed_demo_is_generalist_and_retains_its_material_blocker():
    change = FunctionalChangeV1.model_validate_json(
        (ROOT / "examples/functional-change/change.json").read_bytes()
    )
    result = assess_functional_change(change)
    assert change.source.original_input.domain is None
    assert len(change.rules) == 1 and len(change.examples) == len(change.scenarios) == 3
    assert result.status == "blocked" and result.blockers[0].reference == "overflow-question"
    assert change.confirmations[0].reviewer == "synthetic-reviewer"
    assert all(s.execution_status == "not-run" for s in change.scenarios)


def test_asset_metadata_is_not_evidence_of_functional_business_behavior(change):
    data = change.model_dump()
    asset = data["source"]["original_input"]["assets"][0]
    data["source"]["references"].append(
        dict(
            id="asset-ref",
            project_id=change.source.original_input.id,
            pointer="/assets/0/description",
            value=asset["description"],
        )
    )
    data["rules"][0]["source_refs"] = ["asset-ref"]
    data["confirmations"] = []
    with pytest.raises(ValueError, match="Asset metadata"):
        FunctionalChangeV1.model_validate(data)


def test_rule_cannot_silently_expand_selected_capability_scope(change):
    data = change.model_dump()
    other = data["source"]["original_input"]["backlog"][1]
    data["source"]["references"].append(
        dict(
            id="other-ref",
            project_id=change.source.original_input.id,
            pointer="/backlog/1/acceptance_criteria/0",
            value=other["acceptance_criteria"][0],
        )
    )
    data["rules"][0]["source_refs"] = ["other-ref"]
    data["confirmations"] = []
    with pytest.raises(ValueError, match="unselected capability"):
        FunctionalChangeV1.model_validate(data)


def test_nested_mutation_is_revalidated_before_assessment(change):
    change.source.references[0].value = "Changed after model construction."
    with pytest.raises(ValueError):
        assess_functional_change(change)


def test_present_example_cannot_also_be_declared_inapplicable(change):
    data = change.model_dump()
    data["exemptions"] = [dict(rule_id="batch-rule", kind="boundary", reason="Not applicable.")]
    with pytest.raises(ValueError, match="Exemption"):
        FunctionalChangeV1.model_validate(data)


def test_an_additional_requirement_needs_its_own_scenario_binding(change):
    data = without_questions(change).model_dump()
    data["requirements"].append(
        dict(
            id="additional-requirement",
            text="Another representation requiring its own verification.",
            rule_ids=["batch-rule"],
        )
    )
    draft = FunctionalChangeV1.model_validate(data)
    result = assess_functional_change(draft, review_for(draft))
    assert result.status == "blocked"
    assert ("unmapped-requirement", "additional-requirement") in [
        (b.code, b.reference) for b in result.blockers
    ]


def test_claimed_rule_confirmation_cannot_follow_a_different_rule_id(change):
    data = change.model_dump()
    data["confirmations"][0]["rule_id"] = "unknown-rule"
    with pytest.raises(ValueError, match="Rule confirmation"):
        FunctionalChangeV1.model_validate(data)


def test_valid_maximum_draft_preserves_all_simultaneous_blockers(change):
    data = change.model_dump()
    data["rules"] = [
        dict(
            id=f"rule-{i}",
            statement="Synthetic unconfirmed rule.",
            origin="hypothesis",
            source_refs=["rule-source"],
        )
        for i in range(64)
    ]
    data["confirmations"] = []
    data["examples"] = [
        dict(
            id=f"example-{i}",
            rule_id="rule-0",
            kind="success",
            given="Synthetic setup.",
            when="Observe.",
            then="Synthetic expectation.",
        )
        for i in range(512)
    ]
    data["requirements"] = [
        dict(id=f"requirement-{i}", text="Synthetic requirement.", rule_ids=["rule-0"])
        for i in range(128)
    ]
    data["scenarios"] = []
    data["questions"] = [
        dict(
            id=f"question-{i}",
            text="Which outcome is intended?",
            rule_ids=["rule-0"],
            source_refs=["rule-source"],
            owner="synthetic-owner",
            impact="outcome",
        )
        for i in range(64)
    ]
    draft = FunctionalChangeV1.model_validate(data)
    result = assess_functional_change(draft)
    assert result.status == "blocked" and len(result.blockers) > 1024
    assert len(result.blockers) == len(set((b.code, b.reference) for b in result.blockers))
    assert FunctionalReadinessV1.model_validate_json(result.model_dump_json()) == result


@pytest.mark.parametrize("pointer", ["/assets", "/backlog"])
def test_broad_collection_reference_cannot_bypass_asset_or_capability_scope(change, pointer):
    data = change.model_dump()
    data["source"]["references"].append(
        dict(
            id="broad-ref",
            project_id=change.source.original_input.id,
            pointer=pointer,
            value=reference_value(change.source.original_input, pointer),
        )
    )
    data["rules"][0]["source_refs"] = ["broad-ref"]
    data["confirmations"] = []
    with pytest.raises(ValueError):
        FunctionalChangeV1.model_validate(data)
