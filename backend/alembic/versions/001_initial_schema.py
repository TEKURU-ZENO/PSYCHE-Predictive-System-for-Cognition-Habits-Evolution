"""initial_schema

Revision ID: 001_initial_schema
Revises: 
Create Date: 2026-11-08 15:15:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '001_initial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # 1. users
    op.create_table(
        'users',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('email', sa.String(), nullable=True),
        sa.Column('name', sa.String(), nullable=True),
        sa.Column('password_hash', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)

    # 2. mood_logs
    op.create_table(
        'mood_logs',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=True),
        sa.Column('mood_type', sa.String(), nullable=True),
        sa.Column('intensity', sa.Float(), nullable=True),
        sa.Column('timestamp', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # 3. event_logs
    op.create_table(
        'event_logs',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=True),
        sa.Column('session_id', sa.String(), nullable=True),
        sa.Column('type', sa.String(), nullable=True),
        sa.Column('metadata_col', sa.String(), nullable=True),
        sa.Column('timestamp', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_event_logs_user_id'), 'event_logs', ['user_id'], unique=False)
    op.create_index(op.f('ix_event_logs_session_id'), 'event_logs', ['session_id'], unique=False)
    op.create_index(op.f('ix_event_logs_type'), 'event_logs', ['type'], unique=False)
    op.create_index(op.f('ix_event_logs_timestamp'), 'event_logs', ['timestamp'], unique=False)

    # 4. user_states
    op.create_table(
        'user_states',
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('current_emotion', sa.String(), nullable=True),
        sa.Column('intensity', sa.Float(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('user_id')
    )

    # 5. behavior_logs
    op.create_table(
        'behavior_logs',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=True),
        sa.Column('type', sa.String(), nullable=True),
        sa.Column('value', sa.Float(), nullable=True),
        sa.Column('context', sa.String(), nullable=True),
        sa.Column('timestamp', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # 6. triggers
    op.create_table(
        'triggers',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=True),
        sa.Column('event', sa.String(), nullable=True),
        sa.Column('emotion', sa.String(), nullable=True),
        sa.Column('frequency', sa.Float(), nullable=True),
        sa.Column('confidence', sa.Float(), nullable=True),
        sa.Column('stability', sa.Float(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # 7. user_policies
    op.create_table(
        'user_policies',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=True),
        sa.Column('state', sa.String(), nullable=True),
        sa.Column('action', sa.String(), nullable=True),
        sa.Column('q_score', sa.Float(), nullable=True),
        sa.Column('stable_q_score', sa.Float(), nullable=True),
        sa.Column('visits', sa.Integer(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_policies_user_id'), 'user_policies', ['user_id'], unique=False)

    # 8. pending_rewards
    op.create_table(
        'pending_rewards',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=True),
        sa.Column('state', sa.String(), nullable=True),
        sa.Column('action', sa.String(), nullable=True),
        sa.Column('intensity_before', sa.Float(), nullable=True),
        sa.Column('timestamp', sa.DateTime(), nullable=True),
        sa.Column('resolved', sa.Boolean(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_pending_rewards_user_id'), 'pending_rewards', ['user_id'], unique=False)

    # 9. goals
    op.create_table(
        'goals',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=True),
        sa.Column('goal', sa.String(), nullable=True),
        sa.Column('priority', sa.String(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_goals_user_id'), 'goals', ['user_id'], unique=False)

    # 10. evolution_snapshots
    op.create_table(
        'evolution_snapshots',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=True),
        sa.Column('week', sa.String(), nullable=True),
        sa.Column('archetype', sa.String(), nullable=True),
        sa.Column('stress_avg', sa.Float(), nullable=True),
        sa.Column('dissonance', sa.Float(), nullable=True),
        sa.Column('top_strategy', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_evolution_snapshots_user_id'), 'evolution_snapshots', ['user_id'], unique=False)

    # 11. system_state
    op.create_table(
        'system_state',
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('alpha', sa.Float(), nullable=True),
        sa.Column('epsilon', sa.Float(), nullable=True),
        sa.Column('epsilon_history', sa.String(), nullable=True),
        sa.Column('recovery_mode_active', sa.Boolean(), nullable=True),
        sa.Column('policy_entropy', sa.Float(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('user_id')
    )

    # 12. agent_metrics
    op.create_table(
        'agent_metrics',
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('agent_id', sa.String(), nullable=False),
        sa.Column('total_invocations', sa.Integer(), nullable=True),
        sa.Column('timeouts', sa.Integer(), nullable=True),
        sa.Column('overrides', sa.Integer(), nullable=True),
        sa.Column('successful_contributions', sa.Integer(), nullable=True),
        sa.Column('historical_accuracy', sa.Float(), nullable=True),
        sa.Column('contribution_impact_score', sa.Float(), nullable=True),
        sa.Column('last_success_timestamp', sa.DateTime(), nullable=True),
        sa.Column('trust_tier', sa.Enum('Trusted', 'Stable', 'Uncertain', 'Degraded', name='trusttier'), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('user_id', 'agent_id')
    )

    # 13. episodic_memories
    op.create_table(
        'episodic_memories',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('episode_type', sa.String(50), nullable=False),
        sa.Column('scenario_text', sa.Text(), nullable=False),
        sa.Column('trigger_context', sa.String(255), nullable=True),
        sa.Column('cognitive_distortion', sa.String(100), nullable=True),
        sa.Column('emotional_valence', sa.Float(), nullable=True),
        sa.Column('intensity', sa.Float(), nullable=True),
        sa.Column('intervention_applied', sa.String(100), nullable=True),
        sa.Column('outcome_delta', sa.Float(), nullable=True),
        sa.Column('key_learnings', sa.Text(), nullable=True),
        sa.Column('embedding_json', sa.Text(), nullable=True),
        sa.Column('importance_score', sa.Float(), nullable=True),
        sa.Column('access_count', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('last_accessed_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_episodic_memories_id'), 'episodic_memories', ['id'], unique=False)
    op.create_index(op.f('ix_episodic_memories_user_id'), 'episodic_memories', ['user_id'], unique=False)
    op.create_index(op.f('ix_episodic_memories_episode_type'), 'episodic_memories', ['episode_type'], unique=False)
    op.create_index(op.f('ix_episodic_memories_created_at'), 'episodic_memories', ['created_at'], unique=False)

    # 14. associative_links
    op.create_table(
        'associative_links',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('source_node', sa.String(150), nullable=False),
        sa.Column('target_node', sa.String(150), nullable=False),
        sa.Column('relation_type', sa.String(50), nullable=False),
        sa.Column('weight', sa.Float(), nullable=True),
        sa.Column('occurrences', sa.Integer(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_associative_links_id'), 'associative_links', ['id'], unique=False)
    op.create_index(op.f('ix_associative_links_user_id'), 'associative_links', ['user_id'], unique=False)
    op.create_index(op.f('ix_associative_links_source_node'), 'associative_links', ['source_node'], unique=False)
    op.create_index(op.f('ix_associative_links_target_node'), 'associative_links', ['target_node'], unique=False)

    # 15. schema_consolidations
    op.create_table(
        'schema_consolidations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('theme', sa.String(100), nullable=False),
        sa.Column('consolidated_insight', sa.Text(), nullable=False),
        sa.Column('evidence_count', sa.Integer(), nullable=True),
        sa.Column('confidence', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_schema_consolidations_id'), 'schema_consolidations', ['id'], unique=False)
    op.create_index(op.f('ix_schema_consolidations_user_id'), 'schema_consolidations', ['user_id'], unique=False)

    # 16. proactive_alerts
    op.create_table(
        'proactive_alerts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('alert_type', sa.String(50), nullable=False),
        sa.Column('severity', sa.String(20), nullable=True),
        sa.Column('title', sa.String(150), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('preemptive_action', sa.String(100), nullable=True),
        sa.Column('circadian_phase', sa.String(50), nullable=True),
        sa.Column('is_acknowledged', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_proactive_alerts_id'), 'proactive_alerts', ['id'], unique=False)
    op.create_index(op.f('ix_proactive_alerts_user_id'), 'proactive_alerts', ['user_id'], unique=False)
    op.create_index(op.f('ix_proactive_alerts_alert_type'), 'proactive_alerts', ['alert_type'], unique=False)
    op.create_index(op.f('ix_proactive_alerts_created_at'), 'proactive_alerts', ['created_at'], unique=False)

    # 17. counterfactual_branches
    op.create_table(
        'counterfactual_branches',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('scenario', sa.Text(), nullable=False),
        sa.Column('decision_hash', sa.String(64), nullable=True),
        sa.Column('branch_name', sa.String(100), nullable=False),
        sa.Column('projected_stress_48h', sa.Float(), nullable=True),
        sa.Column('projected_burnout_risk', sa.Float(), nullable=True),
        sa.Column('projected_dissonance', sa.Float(), nullable=True),
        sa.Column('cognitive_energy_delta', sa.Float(), nullable=True),
        sa.Column('expected_q_value', sa.Float(), nullable=True),
        sa.Column('recommendation_rank', sa.Integer(), nullable=True),
        sa.Column('tradeoff_analysis', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_counterfactual_branches_id'), 'counterfactual_branches', ['id'], unique=False)
    op.create_index(op.f('ix_counterfactual_branches_user_id'), 'counterfactual_branches', ['user_id'], unique=False)
    op.create_index(op.f('ix_counterfactual_branches_decision_hash'), 'counterfactual_branches', ['decision_hash'], unique=False)

    # 18. post_mortem_reports
    op.create_table(
        'post_mortem_reports',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('decision_hash', sa.String(64), nullable=True),
        sa.Column('failed_action', sa.String(100), nullable=False),
        sa.Column('responsible_agent', sa.String(50), nullable=False),
        sa.Column('root_cause', sa.String(100), nullable=False),
        sa.Column('penalty_applied', sa.Float(), nullable=True),
        sa.Column('corrective_adaptation', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_post_mortem_reports_id'), 'post_mortem_reports', ['id'], unique=False)
    op.create_index(op.f('ix_post_mortem_reports_user_id'), 'post_mortem_reports', ['user_id'], unique=False)
    op.create_index(op.f('ix_post_mortem_reports_decision_hash'), 'post_mortem_reports', ['decision_hash'], unique=False)
    op.create_index(op.f('ix_post_mortem_reports_created_at'), 'post_mortem_reports', ['created_at'], unique=False)

    # 19. red_team_audit_logs
    op.create_table(
        'red_team_audit_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('decision_hash', sa.String(64), nullable=True),
        sa.Column('critique_score', sa.Float(), nullable=True),
        sa.Column('vulnerabilities_detected', sa.Text(), nullable=True),
        sa.Column('veto_triggered', sa.Boolean(), nullable=True),
        sa.Column('counter_critique', sa.Text(), nullable=True),
        sa.Column('suggested_amendment', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_red_team_audit_logs_id'), 'red_team_audit_logs', ['id'], unique=False)
    op.create_index(op.f('ix_red_team_audit_logs_user_id'), 'red_team_audit_logs', ['user_id'], unique=False)
    op.create_index(op.f('ix_red_team_audit_logs_decision_hash'), 'red_team_audit_logs', ['decision_hash'], unique=False)

def downgrade() -> None:
    op.drop_table('red_team_audit_logs')
    op.drop_table('post_mortem_reports')
    op.drop_table('counterfactual_branches')
    op.drop_table('proactive_alerts')
    op.drop_table('schema_consolidations')
    op.drop_table('associative_links')
    op.drop_table('episodic_memories')
    op.drop_table('agent_metrics')
    op.drop_table('system_state')
    op.drop_table('evolution_snapshots')
    op.drop_table('goals')
    op.drop_table('pending_rewards')
    op.drop_table('user_policies')
    op.drop_table('triggers')
    op.drop_table('behavior_logs')
    op.drop_table('user_states')
    op.drop_table('event_logs')
    op.drop_table('mood_logs')
    op.drop_table('users')
