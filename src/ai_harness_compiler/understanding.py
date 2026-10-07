"""Prepare grounded model input; does not infer a domain or invoke a provider."""

from ai_harness_compiler.models.evidence import canonical_project_digest
from ai_harness_compiler.models.project import ProjectInput
from ai_harness_compiler.models.understanding import (
    InputReference,
    UnderstandingRequest,
    reference_value,
)


def prepare_understanding(project: ProjectInput) -> UnderstandingRequest:
    snapshot = ProjectInput.model_validate(project.model_dump())
    pointers = ["/conception", "/branding", "/constraints"]
    for index, item in enumerate(snapshot.backlog):
        pointers.append(f"/backlog/{index}/description")
        pointers.extend(
            f"/backlog/{index}/acceptance_criteria/{number}"
            for number in range(len(item.acceptance_criteria))
        )
    if snapshot.domain:
        pointers.append("/domain")
    if snapshot.domain_profile:
        pointers.append("/domain_profile")
    if snapshot.assets:
        pointers.append("/assets")
    if snapshot.evidence_pack:
        pointers.extend(
            f"/evidence_pack/evidence/{index}/claim"
            for index in range(len(snapshot.evidence_pack.evidence))
        )
    return UnderstandingRequest(
        original_input=snapshot,
        original_sha256=canonical_project_digest(snapshot.model_dump()),
        references=[
            InputReference(
                id=f"input-{index + 1}",
                project_id=snapshot.id,
                pointer=pointer,
                value=reference_value(snapshot, pointer),
            )
            for index, pointer in enumerate(pointers)
        ],
    )
