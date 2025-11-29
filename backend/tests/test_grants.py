import pytest
from httpx import AsyncClient

from src.modules.payments.services import PaymentService


@pytest.mark.asyncio
async def test_grant_lifecycle_with_roles_and_stages(client: AsyncClient, users, use_current_user):
    use_current_user(users["grantor"])

    payload = {
        "name": "STEM Program",
        "bank_account_number": "BANK-123",
        "stages": [
            {
                "order": 1,
                "amount": 1000,
                "requirements": [{"name": "Submit proposal", "description": "Initial proposal upload"}],
            },
            {"order": 2, "amount": 2000, "requirements": []},
        ],
        "participants": [
            {"user_id": str(users["grantee"].id), "role": "grantee"},
            {"user_id": str(users["supervisor"].id), "role": "supervisor"},
        ],
    }

    create_response = await client.post("/api/v1/grants/", json=payload)
    assert create_response.status_code == 201
    created = create_response.json()
    assert created["bank_account_number"] == "BANK-123"
    assert any(p["role"] == "grantor" for p in created["participants"])
    grant_id = created["id"]
    stage1 = created["stages"][0]

    # Grantor confirms the program which activates stage 1.
    confirm_response = await client.post(f"/api/v1/grants/{grant_id}/confirm")
    assert confirm_response.status_code == 200
    confirmed = confirm_response.json()
    assert confirmed["status"] == "active"
    assert confirmed["stages"][0]["completion_status"] == "active"
    assert confirmed["stages"][1]["completion_status"] == "pending"

    # Grantor invites another supervisor post-creation.
    invite_body = {"user_email": users["extra_supervisor"].email, "role": "supervisor"}
    invite_response = await client.post(f"/api/v1/grants/{grant_id}/invite", json=invite_body)
    assert invite_response.status_code == 200
    invited = invite_response.json()
    assert any(p["user_id"] == str(users["extra_supervisor"].id) for p in invited)

    # Grantee submits proof for stage 1 requirement.
    use_current_user(users["grantee"])
    proof_resp = await client.post(
        f"/api/v1/grants/requirements/{stage1['requirements'][0]['id']}/proof",
        json={"proof_url": "https://evidence.local/doc"},
    )
    assert proof_resp.status_code == 200
    assert proof_resp.json()["proof_url"] == "https://evidence.local/doc"

    # Supervisor completes stage 1 requirement after proof is in.
    use_current_user(users["supervisor"])
    req_complete = await client.post(f"/api/v1/grants/requirements/{stage1['requirements'][0]['id']}/complete")
    assert req_complete.status_code == 200
    assert req_complete.json()["status"] == "completed"

    # Supervisor completes stage 1, which should activate stage 2.
    stage1_complete = await client.post(f"/api/v1/grants/stages/{stage1['id']}/complete")
    assert stage1_complete.status_code == 200
    assert stage1_complete.json()["completion_status"] == "completed"

    grants_after_stage1 = await client.get("/api/v1/grants/")
    assert grants_after_stage1.status_code == 200
    stages = grants_after_stage1.json()[0]["stages"]
    assert stages[1]["completion_status"] == "active"

    # Grantee is not allowed to complete a stage.
    use_current_user(users["grantee"])
    forbidden = await client.post(f"/api/v1/grants/stages/{stages[1]['id']}/complete")
    assert forbidden.status_code == 403

    # Supervisor finishes the final stage, completing the grant.
    use_current_user(users["supervisor"])
    stage2_complete = await client.post(f"/api/v1/grants/stages/{stages[1]['id']}/complete")
    assert stage2_complete.status_code == 200
    grants_after_all = await client.get("/api/v1/grants/")
    assert grants_after_all.status_code == 200
    assert grants_after_all.json()[0]["status"] == "completed"


@pytest.mark.asyncio
async def test_grant_confirmation_triggers_deposit(monkeypatch, client: AsyncClient, users, use_current_user):
    use_current_user(users["grantor"])

    deposit_calls = {}
    original_deposit = PaymentService.deposit_grant

    async def fake_deposit(self, *, participant_id: str, amount: float):
        deposit_calls["participant_id"] = participant_id
        deposit_calls["amount"] = amount
        return await original_deposit(self, participant_id=participant_id, amount=amount)

    monkeypatch.setattr(PaymentService, "deposit_grant", fake_deposit)

    payload = {
        "name": "Deposit Program",
        "bank_account_number": "BANK-DEP",
        "stages": [
            {"order": 1, "amount": 500, "requirements": []},
            {"order": 2, "amount": 750, "requirements": []},
        ],
        "participants": [],
    }

    create_response = await client.post("/api/v1/grants/", json=payload)
    assert create_response.status_code == 201

    confirm_response = await client.post(f"/api/v1/grants/{create_response.json()['id']}/confirm")
    assert confirm_response.status_code == 200
    assert confirm_response.json()["status"] == "active"
    assert deposit_calls["participant_id"] == "APP-ACCOUNT"
    assert deposit_calls["amount"] == 1250.0


@pytest.mark.asyncio
async def test_grantor_can_promote_to_supervisor(client: AsyncClient, users, use_current_user):
    use_current_user(users["grantor"])
    payload = {
        "name": "Promotion Program",
        "bank_account_number": "BANK-PROMO",
        "stages": [{"order": 1, "amount": 100, "requirements": []}],
        "participants": [{"user_id": str(users["grantee"].id), "role": "grantee"}],
    }
    create_response = await client.post("/api/v1/grants/", json=payload)
    assert create_response.status_code == 201
    grant_id = create_response.json()["id"]
    participant_id = create_response.json()["participants"][1]["id"]

    promote_resp = await client.patch(
        f"/api/v1/grants/{grant_id}/participants/{participant_id}", json={"role": "supervisor"}
    )
    assert promote_resp.status_code == 200
    roles = {p["id"]: p["role"] for p in promote_resp.json()}
    assert roles[participant_id] == "supervisor"


@pytest.mark.asyncio
async def test_grantor_can_demote_supervisor_to_grantee(client: AsyncClient, users, use_current_user):
    use_current_user(users["grantor"])
    payload = {
        "name": "Demotion Program",
        "bank_account_number": "BANK-DEMOTE",
        "stages": [{"order": 1, "amount": 100, "requirements": []}],
        "participants": [{"user_id": str(users["supervisor"].id), "role": "supervisor"}],
    }
    create_response = await client.post("/api/v1/grants/", json=payload)
    assert create_response.status_code == 201
    grant_id = create_response.json()["id"]
    participant_id = create_response.json()["participants"][1]["id"]

    demote_resp = await client.patch(
        f"/api/v1/grants/{grant_id}/participants/{participant_id}", json={"role": "grantee"}
    )
    assert demote_resp.status_code == 200
    roles = {p["id"]: p["role"] for p in demote_resp.json()}
    assert roles[participant_id] == "grantee"


@pytest.mark.asyncio
async def test_stage_payout_triggers_for_non_contract_stage(monkeypatch, client: AsyncClient, users, use_current_user):
    use_current_user(users["grantor"])

    payout_calls = []

    async def fake_payout(self, stage):
        payout_calls.append({"stage_id": str(stage.id), "amount": float(stage.amount)})
        return None

    monkeypatch.setattr(PaymentService, "send_stage_payout", fake_payout)

    payload = {
        "name": "Payout Program",
        "bank_account_number": "BANK-PAY",
        "stages": [
            {"order": 1, "amount": 150, "requirements": []},
        ],
        "participants": [{"user_id": str(users["supervisor"].id), "role": "supervisor"}],
    }

    create_response = await client.post("/api/v1/grants/", json=payload)
    assert create_response.status_code == 201
    grant = create_response.json()
    stage_id = grant["stages"][0]["id"]

    await client.post(f"/api/v1/grants/{grant['id']}/confirm")

    # Supervisor completes stage directly; payout should fire.
    use_current_user(users["supervisor"])
    complete_resp = await client.post(f"/api/v1/grants/stages/{stage_id}/complete")
    assert complete_resp.status_code == 200
    assert payout_calls and payout_calls[0]["stage_id"] == stage_id


@pytest.mark.asyncio
async def test_stage_payout_skipped_for_contract_stage(monkeypatch, client: AsyncClient, users, use_current_user):
    use_current_user(users["grantor"])

    payout_calls = []

    async def fake_payout(self, stage):
        payout_calls.append(str(stage.id))
        return None

    monkeypatch.setattr(PaymentService, "send_stage_payout", fake_payout)

    payload = {
        "name": "Contract Stage",
        "bank_account_number": "BANK-PAY",
        "stages": [
            {
                "order": 1,
                "amount": 150,
                "requirements": [{"name": "Smart", "description": "payment_contract_id:abc"}],
            },
        ],
        "participants": [{"user_id": str(users["grantee"].id), "role": "grantee"}],
    }

    create_response = await client.post("/api/v1/grants/", json=payload)
    assert create_response.status_code == 201
    stage_id = create_response.json()["stages"][0]["id"]
    await client.post(f"/api/v1/grants/{create_response.json()['id']}/confirm")

    # Grantee can complete contract stage but payout should not trigger.
    use_current_user(users["grantee"])
    complete_resp = await client.post(f"/api/v1/grants/stages/{stage_id}/complete")
    assert complete_resp.status_code == 200
    assert payout_calls == []


@pytest.mark.asyncio
async def test_grantor_can_update_payout_account(client: AsyncClient, users, use_current_user):
    use_current_user(users["grantor"])
    payload = {
        "name": "Update Bank",
        "bank_account_number": "BANK-ORIG",
        "stages": [{"order": 1, "amount": 100, "requirements": []}],
        "participants": [],
    }
    create_response = await client.post("/api/v1/grants/", json=payload)
    assert create_response.status_code == 201
    grant_id = create_response.json()["id"]

    update_resp = await client.patch(
        f"/api/v1/grants/{grant_id}/bank-account", json={"bank_account_number": "BANK-NEW"}
    )
    assert update_resp.status_code == 200
    assert update_resp.json()["bank_account_number"] == "BANK-NEW"
@pytest.mark.asyncio
async def test_stages_must_be_sequential(client: AsyncClient, users, use_current_user):
    use_current_user(users["grantor"])

    payload = {
        "name": "Broken Program",
        "bank_account_number": "BANK-999",
        "stages": [
            {"order": 1, "amount": 1000, "requirements": []},
            {"order": 3, "amount": 2000, "requirements": []},
        ],
        "participants": [],
    }

    response = await client.post("/api/v1/grants/", json=payload)
    assert response.status_code == 400
    assert response.json()["detail"] == "Stages must be sequential and start at 1"


@pytest.mark.asyncio
async def test_requirement_needs_active_stage_and_role(client: AsyncClient, users, use_current_user):
    use_current_user(users["grantor"])
    payload = {
        "name": "Inactive Stage Program",
        "bank_account_number": "BANK-111",
        "stages": [
            {
                "order": 1,
                "amount": 100,
                "requirements": [{"name": "Doc", "description": "Upload doc"}],
            }
        ],
        "participants": [
            {"user_email": users["supervisor"].email, "role": "supervisor"},
            {"user_id": str(users["grantee"].id), "role": "grantee"},
        ],
    }
    create_response = await client.post("/api/v1/grants/", json=payload)
    assert create_response.status_code == 201
    requirement_id = create_response.json()["stages"][0]["requirements"][0]["id"]

    # Grantor cannot complete requirement while stage pending.
    pending_resp = await client.post(f"/api/v1/grants/requirements/{requirement_id}/complete")
    assert pending_resp.status_code == 400

    # After activation, a grantee still cannot complete requirement.
    await client.post(f"/api/v1/grants/{create_response.json()['id']}/confirm")
    use_current_user(users["grantee"])
    forbidden = await client.post(f"/api/v1/grants/requirements/{requirement_id}/complete")
    assert forbidden.status_code == 403

    # Grantee can submit proof but still cannot approve.
    proof = await client.post(f"/api/v1/grants/requirements/{requirement_id}/proof", json={"proof_url": "https://file"})
    assert proof.status_code == 200


@pytest.mark.asyncio
async def test_inviting_same_user_twice_returns_error(client: AsyncClient, users, use_current_user):
    use_current_user(users["grantor"])
    payload = {
        "name": "Invite Program",
        "bank_account_number": "BANK-222",
        "stages": [{"order": 1, "amount": 100, "requirements": []}],
        "participants": [{"user_id": str(users["supervisor"].id), "role": "supervisor"}],
    }
    create_response = await client.post("/api/v1/grants/", json=payload)
    assert create_response.status_code == 201
    grant_id = create_response.json()["id"]

    dup_invite = await client.post(
        f"/api/v1/grants/{grant_id}/invite",
        json={"user_email": users["supervisor"].email, "role": "supervisor"},
    )
    assert dup_invite.status_code == 400
    assert dup_invite.json()["detail"] == "User already invited to grant"


@pytest.mark.asyncio
async def test_supervisor_cannot_complete_requirement_without_proof(client: AsyncClient, users, use_current_user):
    use_current_user(users["grantor"])
    payload = {
        "name": "Proof Needed",
        "bank_account_number": "BANK-333",
        "stages": [
            {
                "order": 1,
                "amount": 100,
                "requirements": [{"name": "Evidence", "description": "Upload evidence"}],
            }
        ],
        "participants": [{"user_email": users["supervisor"].email, "role": "supervisor"}],
    }
    create_response = await client.post("/api/v1/grants/", json=payload)
    assert create_response.status_code == 201
    grant_id = create_response.json()["id"]
    requirement_id = create_response.json()["stages"][0]["requirements"][0]["id"]

    await client.post(f"/api/v1/grants/{grant_id}/confirm")
    use_current_user(users["supervisor"])
    without_proof = await client.post(f"/api/v1/grants/requirements/{requirement_id}/complete")
    assert without_proof.status_code == 400
    assert without_proof.json()["detail"] == "Proof not submitted yet"
