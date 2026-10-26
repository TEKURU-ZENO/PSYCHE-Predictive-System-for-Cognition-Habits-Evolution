"""initial_schema

Revision ID: 001_initial_schema
Revises: 
Create Date: 2026-10-25 18:35:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '001_initial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # 1. users
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(), nullable=False),
        sa.Column('hashed_password', sa.String(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('username')
    )

    # 2. mood_logs
    op.create_table(
        'mood_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('score', sa.Integer(), nullable=True),
        sa.Column('context', sa.String(), nullable=True),
        sa.Column('timestamp', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # 3. event_logs
    op.create_table(
        'event_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('event_type', sa.String(), nullable=True),
        sa.Column('details', sa.JSON(), nullable=True),
        sa.Column('timestamp', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # 4. user_states
    op.create_table(
        'user_states',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('current_state', sa.String(), nullable=True),
        sa.Column('stress_level', sa.Float(), nullable=True),
        sa.Column('cognitive_load', sa.Float(), nullable=True),
        sa.Column('energy', sa.Float(), nullable=True),
        sa.Column('timestamp', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # 5. behavior_logs
    op.create_table(
        'behavior_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('action', sa.String(), nullable=True),
        sa.Column('context', sa.JSON(), nullable=True),
        sa.Column('timestamp', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # 6. triggers
    op.create_table(
        'triggers',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('trigger_name', sa.String(), nullable=True),
        sa.Column('severity', sa.Float(), nullable=True),
        sa.Column('frequency', sa.Integer(), nullable=True),
        sa.Column('last_observed', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # 7. user_policies
    op.create_table(
        'user_policies',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('state_key', sa.String(), nullable=True),
        sa.Column('action', sa.String(), nullable=True),
        sa.Column('q_value', sa.Float(), nullable=True),
        sa.Column('exploration_rate', sa.Float(), nullable=True),
        sa.Column('update_count', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # 8. pending_rewards
    op.create_table(
        'pending_rewards',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('state_key', sa.String(), nullable=True),
        sa.Column('action', sa.String(), nullable=True),
        sa.Column('baseline_burnout_risk', sa.Float(), nullable=True),
        sa.Column('timestamp', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # 9. evolution_snapshots
    op.create_table(
        'evolution_snapshots',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('archetype', sa.String(), nullable=True),
        sa.Column('baseline_stress', sa.Float(), nullable=True),
        sa.Column('adaptability_index', sa.Float(), nullable=True),
        sa.Column('primary_triggers', sa.JSON(), nullable=True),
        sa.Column('active_strategy', sa.String(), nullable=True),
        sa.Column('snapshot_date', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # 10. goals
    op.create_table(
        'goals',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('title', sa.String(), nullable=True),
        sa.Column('target_date', sa.DateTime(), nullable=True),
        sa.Column('status', sa.String(), nullable=True),
        sa.Column('progress', sa.Float(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # 11. system_states
    op.create_table(
        'system_states',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('last_drift_score', sa.Float(), nullable=True),
        sa.Column('safe_mode', sa.Boolean(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # 12. agent_metrics
    op.create_table(
        'agent_metrics',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('agent_name', sa.String(), nullable=False),
        sa.Column('total_invocations', sa.Integer(), nullable=True),
        sa.Column('successful_contributions', sa.Integer(), nullable=True),
        sa.Column('overridden_count', sa.Integer(), nullable=True),
        sa.Column('timeouts', sa.Integer(), nullable=True),
        sa.Column('average_latency', sa.Float(), nullable=True),
        sa.Column('contribution_impact_score', sa.Float(), nullable=True),
        sa.Column('trust_tier', sa.String(), nullable=True),
        sa.Column('last_success_timestamp', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('agent_name')
    )

    # 13. episodic_memories
    op.create_table(
        'episodic_memories',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('scenario_summary', sa.String(), nullable=False),
        sa.Column('emotional_valence', sa.Float(), nullable=True),
        sa.Column('chosen_action', sa.String(), nullable=False),
        sa.Column('outcome_delta', sa.Float(), nullable=True),
        sa.Column('reflection', sa.Text(), nullable=True),
        sa.Column('retrieval_keywords', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # 14. associative_links
    op.create_table(
        'associative_links',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('concept_a', sa.String(), nullable=False),
        sa.Column('concept_b', sa.String(), nullable=False),
        sa.Column('weight', sa.Float(), nullable=True),
        sa.Column('link_type', sa.String(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # 15. schema_consolidations
    op.create_table(
        'schema_consolidations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('recurring_pattern', sa.String(), nullable=False),
        sa.Column('generalized_rule', sa.Text(), nullable=False),
        sa.Column('support_count', sa.Integer(), nullable=True),
        sa.Column('confidence', sa.Float(), nullable=True),
        sa.Column('consolidated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # 16. proactive_alerts
    op.create_table(
        'proactive_alerts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('alert_type', sa.String(), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('severity', sa.String(), nullable=False),
        sa.Column('acknowledged', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # 17. counterfactual_branches
    op.create_table(
        'counterfactual_branches',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('scenario', sa.String(), nullable=False),
        sa.Column('branch_name', sa.String(), nullable=False),
        sa.Column('proposed_action', sa.String(), nullable=False),
        sa.Column('simulated_burnout_delta', sa.Float(), nullable=True),
        sa.Column('simulated_stress_delta', sa.Float(), nullable=True),
        sa.Column('simulated_energy_delta', sa.Float(), nullable=True),
        sa.Column('composite_score', sa.Float(), nullable=True),
        sa.Column('rank', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # 18. post_mortem_reports
    op.create_table(
        'post_mortem_reports',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('decision_hash', sa.String(), nullable=False),
        sa.Column('scenario', sa.String(), nullable=False),
        sa.Column('action_taken', sa.String(), nullable=False),
        sa.Column('outcome_description', sa.Text(), nullable=False),
        sa.Column('root_cause_agent', sa.String(), nullable=False),
        sa.Column('failure_type', sa.String(), nullable=False),
        sa.Column('corrective_guidance', sa.Text(), nullable=False),
        sa.Column('penalty_applied', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # 19. red_team_audit_logs
    op.create_table(
        'red_team_audit_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('scenario', sa.String(), nullable=False),
        sa.Column('candidate_action', sa.String(), nullable=False),
        sa.Column('vulnerability_type', sa.String(), nullable=False),
        sa.Column('critique', sa.Text(), nullable=False),
        sa.Column('veto_applied', sa.Boolean(), nullable=True),
        sa.Column('audited_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

def downgrade() -> None:
    op.drop_table('red_team_audit_logs')
    op.drop_table('post_mortem_reports')
    op.drop_table('counterfactual_branches')
    op.drop_table('proactive_alerts')
    op.drop_table('schema_consolidations')
    op.drop_table('associative_links')
    op.drop_table('episodic_memories')
    op.drop_table('agent_metrics')
    op.drop_table('system_states')
    op.drop_table('goals')
    op.drop_table('evolution_snapshots')
    op.drop_table('pending_rewards')
    op.drop_table('user_policies')
    op.drop_table('triggers')
    op.drop_table('behavior_logs')
    op.drop_table('user_states')
    op.drop_table('event_logs')
    op.drop_table('mood_logs')
    op.drop_table('users')
