import os
import sys
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context

# Ensure app root is on python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.config import settings
from db.postgres import Base

# Import all models to register them on Base.metadata
from models.user import User
from models.mood import MoodLog
from models.event import EventLog
from models.user_state import UserState
from models.behavior import BehaviorLog
from models.pattern import Trigger
from models.personalization import UserPolicy, PendingReward
from models.evolution import EvolutionSnapshot
from models.goals import Goal
from models.system_state import SystemState
from models.agent_metrics import AgentMetrics
from models.memory import EpisodicMemory, AssociativeLink, SchemaConsolidation
from models.proactive import ProactiveAlert, CounterfactualBranch
from models.post_mortem import PostMortemReport, RedTeamAuditLog

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

def get_url():
    return settings.DATABASE_URL

def run_migrations_offline() -> None:
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    configuration = config.get_section(config.config_ini_section) or {}
    configuration["sqlalchemy.url"] = get_url()
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
