import pytest
from httpx import AsyncClient


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
    invite_body = {"user_id": str(users["extra_supervisor"].id), "role": "supervisor"}
    invite_response = await client.post(f"/api/v1/grants/{grant_id}/invite", json=invite_body)
    assert invite_response.status_code == 200
    invited = invite_response.json()
    assert any(p["user_id"] == str(users["extra_supervisor"].id) for p in invited)

    # Supervisor completes stage 1 requirement.
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
        "participants": [{"user_id": str(users["supervisor"].id), "role": "supervisor"}],
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
        json={"user_id": str(users["supervisor"].id), "role": "supervisor"},
    )
    assert dup_invite.status_code == 400
    assert dup_invite.json()["detail"] == "User already invited to grant"
