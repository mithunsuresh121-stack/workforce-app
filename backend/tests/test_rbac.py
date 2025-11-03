import pytest
from sqlalchemy.orm import Session
from app.core.rbac import RBACService
from app.models.user import User, UserRole
from app.models.company import Company
from app.models.company_department import CompanyDepartment
from app.models.company_team import CompanyTeam
from app.models.channels import Channel, ChannelType
from app.models.meetings import Meeting
from app.base_crud import create_user, create_company
from app.crud.org import create_department, create_team
from app.crud.crud_channels import create_channel
from app.crud.crud_meetings import create_meeting
from datetime import datetime

@pytest.fixture
def superadmin_user(db: Session):
    return create_user(db, email="super@test.com", password="pass", full_name="Super", role=UserRole.SUPERADMIN)

@pytest.fixture
def company_admin_user(db: Session, test_company):
    user = create_user(db, email="admin@test.com", password="pass", full_name="Admin", role=UserRole.COMPANY_ADMIN, company_id=test_company.id)
    return user

@pytest.fixture
def department_admin_user(db: Session, test_company):
    dept = create_department(db, company_id=test_company.id, name="Test Dept", created_by=1)
    user = create_user(db, email="deptadmin@test.com", password="pass", full_name="Dept Admin", role=UserRole.DEPARTMENT_ADMIN, company_id=test_company.id)
    user.department_id = dept.id
    db.commit()
    return user, dept

@pytest.fixture
def team_lead_user(db: Session, test_company, department_admin_user):
    dept = department_admin_user[1]
    team = create_team(db, department_id=dept.id, name="Test Team", created_by=1)
    user = create_user(db, email="teamlead@test.com", password="pass", full_name="Team Lead", role=UserRole.TEAM_LEAD, company_id=test_company.id)
    user.department_id = dept.id
    user.team_id = team.id
    db.commit()
    return user, team

@pytest.fixture
def employee_user(db: Session, test_company, team_lead_user):
    team = team_lead_user[1]
    user = create_user(db, email="emp@test.com", password="pass", full_name="Employee", role=UserRole.EMPLOYEE, company_id=test_company.id)
    user.department_id = team.department_id
    user.team_id = team.id
    db.commit()
    return user

@pytest.fixture
def public_channel(db: Session, test_company):
    return create_channel(db, name="Public", type=ChannelType.PUBLIC, company_id=test_company.id, created_by=1)  # Assuming creator id=1 for test

@pytest.fixture
def team_channel(db: Session, test_company, team_lead_user):
    team = team_lead_user[1]
    return create_channel(db, name="Team Chat", type=ChannelType.GROUP, company_id=test_company.id, team_id=team.id, created_by=1)

@pytest.fixture
def company_meeting(db: Session, test_company):
    return create_meeting(db, title="Company Meeting", organizer_id=1, company_id=test_company.id, start_time=datetime(2024, 1, 1, 10, 0, 0), end_time=datetime(2024, 1, 1, 11, 0, 0))

@pytest.fixture
def team_meeting(db: Session, test_company, team_lead_user):
    team = team_lead_user[1]
    return create_meeting(db, title="Team Meeting", organizer_id=1, company_id=test_company.id, team_id=team.id, start_time=datetime(2024, 1, 1, 10, 0, 0), end_time=datetime(2024, 1, 1, 11, 0, 0))

class TestRBACService:
    def test_superadmin_checks(self, superadmin_user):
        assert RBACService.check_superadmin(superadmin_user)
        assert RBACService.can_access_company(superadmin_user, 123)
        assert RBACService.can_manage_department(superadmin_user, 123)
        assert RBACService.can_manage_team(superadmin_user, 123)
        assert RBACService.can_create_channel(superadmin_user)
        assert RBACService.can_create_meeting(superadmin_user)

    def test_company_admin_checks(self, company_admin_user, test_company):
        assert RBACService.check_company_admin(company_admin_user, test_company.id)
        assert RBACService.can_access_company(company_admin_user, test_company.id)
        assert not RBACService.can_access_company(company_admin_user, 999)
        assert RBACService.can_manage_department(company_admin_user, test_company.id)  # Simplified
        assert RBACService.can_manage_team(company_admin_user, test_company.id)
        assert RBACService.can_create_channel(company_admin_user)
        assert RBACService.can_create_meeting(company_admin_user)

    def test_department_admin_checks(self, department_admin_user):
        user, dept = department_admin_user
        assert RBACService.check_department_admin(user, dept.id)
        assert RBACService.can_manage_department(user, dept.id)
        assert not RBACService.can_manage_department(user, 999)
        assert RBACService.can_create_channel(user, department_id=dept.id)
        assert RBACService.can_create_meeting(user, department_id=dept.id)

    def test_team_lead_checks(self, team_lead_user):
        user, team = team_lead_user
        assert RBACService.check_team_lead(user, team.id)
        assert RBACService.can_manage_team(user, team.id)
        assert not RBACService.can_manage_team(user, 999)
        assert RBACService.can_create_channel(user, team_id=team.id)
        assert RBACService.can_create_meeting(user, team_id=team.id)

    def test_employee_checks(self, employee_user):
        assert RBACService.check_employee(employee_user)
        assert not RBACService.check_superadmin(employee_user)
        assert not RBACService.check_company_admin(employee_user, 123)
        assert not RBACService.can_create_channel(employee_user)
        assert not RBACService.can_create_meeting(employee_user)

    def test_can_join_channel_public(self, company_admin_user, public_channel):
        assert RBACService.can_join_channel(company_admin_user, public_channel)

    def test_can_join_channel_team(self, team_lead_user, team_channel):
        user, _ = team_lead_user
        assert RBACService.can_join_channel(user, team_channel)

    def test_cannot_join_wrong_team_channel(self, company_admin_user, team_channel):
        assert not RBACService.can_join_channel(company_admin_user, team_channel)

    def test_can_join_meeting_company(self, company_admin_user, company_meeting):
        assert RBACService.can_join_meeting(company_admin_user, company_meeting)

    def test_can_join_meeting_team(self, team_lead_user, team_meeting):
        user, _ = team_lead_user
        assert RBACService.can_join_meeting(user, team_meeting)

    def test_cannot_join_wrong_team_meeting(self, company_admin_user, team_meeting):
        assert not RBACService.can_join_meeting(company_admin_user, team_meeting)

    def test_can_manage_users_same_scope(self, company_admin_user, employee_user):
        assert RBACService.can_manage_users(company_admin_user, employee_user)

    def test_cannot_manage_users_different_scope(self, db: Session, company_admin_user):
        other_user = create_user(db, email="other@test.com", password="pass", full_name="Other User", role=UserRole.EMPLOYEE, company_id=999)
        assert not RBACService.can_manage_users(company_admin_user, other_user)

    def test_cross_org_message_block(self, company_admin_user, employee_user):
        # Same company - should allow
        assert RBACService.can_send_cross_org_message(company_admin_user, employee_user)

        # Different company - should block
        employee_user.company_id = 999
        assert not RBACService.can_send_cross_org_message(company_admin_user, employee_user)

    def test_cross_org_channel_invite_block(self, company_admin_user, team_channel, employee_user):
        # Same company - should allow
        assert RBACService.can_invite_to_channel(company_admin_user, team_channel, employee_user)

        # Different company - should block
        employee_user.company_id = 999
        assert not RBACService.can_invite_to_channel(company_admin_user, team_channel, employee_user)

    def test_cross_org_meeting_invite_block(self, company_admin_user, team_meeting, employee_user):
        # Same company - should allow
        assert RBACService.can_invite_to_meeting(company_admin_user, team_meeting, employee_user)

        # Different company - should block
        employee_user.company_id = 999
        assert not RBACService.can_invite_to_meeting(company_admin_user, team_meeting, employee_user)

# Note: CRUD functions like create_channel, create_meeting need to be defined or mocked for these tests
# For now, assuming they exist or adjust fixtures accordingly
