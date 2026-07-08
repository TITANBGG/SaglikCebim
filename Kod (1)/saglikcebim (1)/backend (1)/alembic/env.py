import os
import sys
from pathlib import Path

# Backend klasörünü bul
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

# .env dosyasını explicit yükle
from dotenv import load_dotenv
env_path = backend_dir / '.env'
load_dotenv(dotenv_path=env_path)

from app.core.database import Base
from app.models.user import User, AnamnesisState
from app.models.report import Report
from app.models.test_result import TestResult
from app.models.notification import Notification
from app.models.push_subscription import PushSubscription
from app.models.radiology_image import RadiologyImage
from app.models.radiology_finding import RadiologyFinding
from app.models.anamnesis import PatientProfile
from app.models.patient_conditions import PatientCondition
from app.models.patient_medications import PatientMedication
from app.models.patient_allergies import PatientAllergy
from app.models.patient_family_history import PatientFamilyHistory
from app.models.patient_symptom_snapshot import PatientSymptomSnapshot
from app.models.radiology_context_link import RadiologyContextLink
from app.models.anamnesis_audit_log import AnamnesisAuditLog
from app.models.roadmap_session import RoadmapSession
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = os.getenv("DATABASE_URL")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    from sqlalchemy import create_engine 
    connectable = create_engine(os.getenv("DATABASE_URL"))
    

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
