"""add protocol domain tables and metric-compatible fields

Revision ID: 20260227_0001
Revises: 
Create Date: 2026-02-27
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = "20260227_0001"
down_revision = None
branch_labels = None
depends_on = None


def json_type():
    return sa.JSON().with_variant(postgresql.JSONB(astext_type=sa.Text()), "postgresql")


def upgrade() -> None:
    op.add_column("habits", sa.Column("source_type", sa.String(length=50), nullable=False, server_default="manual"))
    op.add_column("habits", sa.Column("source_ref_id", sa.Integer(), nullable=True))
    op.add_column("habits", sa.Column("target_metric_key", sa.String(length=100), nullable=True))

    op.add_column("check_ins", sa.Column("metric_key", sa.String(length=100), nullable=True))
    op.add_column("check_ins", sa.Column("value_numeric", sa.Numeric(), nullable=True))
    op.add_column("check_ins", sa.Column("value_text", sa.Text(), nullable=True))

    op.create_table(
        "protocol_templates",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("code", sa.String(length=100), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("version", sa.String(length=50), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=True),
        sa.Column("default_program_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["default_program_id"], ["programs.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_protocol_templates_id", "protocol_templates", ["id"])
    op.create_index("ix_protocol_templates_code", "protocol_templates", ["code"], unique=True)

    op.create_table(
        "protocol_phases",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("protocol_template_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("phase_key", sa.String(length=50), nullable=False),
        sa.Column("phase_order", sa.Integer(), nullable=False),
        sa.Column("entry_criteria_json", json_type(), nullable=True),
        sa.Column("exit_criteria_json", json_type(), nullable=True),
        sa.ForeignKeyConstraint(["protocol_template_id"], ["protocol_templates.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_protocol_phases_id", "protocol_phases", ["id"])
    op.create_index("ix_protocol_phases_protocol_template_id", "protocol_phases", ["protocol_template_id"])
    op.create_index("idx_protocol_phase_template_order", "protocol_phases", ["protocol_template_id", "phase_order"], unique=True)

    op.create_table(
        "artifact_definitions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("protocol_template_id", sa.Integer(), nullable=False),
        sa.Column("artifact_key", sa.String(length=100), nullable=False),
        sa.Column("type", sa.String(length=50), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("schema_json", json_type(), nullable=True),
        sa.Column("scoring_json", json_type(), nullable=True),
        sa.ForeignKeyConstraint(["protocol_template_id"], ["protocol_templates.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_artifact_definitions_id", "artifact_definitions", ["id"])
    op.create_index("ix_artifact_definitions_protocol_template_id", "artifact_definitions", ["protocol_template_id"])
    op.create_index("idx_artifact_definition_template_key", "artifact_definitions", ["protocol_template_id", "artifact_key"], unique=True)

    op.create_table(
        "protocol_runs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("protocol_template_id", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("current_phase_id", sa.Integer(), nullable=True),
        sa.Column("started_at", sa.DateTime(), nullable=True),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["current_phase_id"], ["protocol_phases.id"]),
        sa.ForeignKeyConstraint(["protocol_template_id"], ["protocol_templates.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_protocol_runs_id", "protocol_runs", ["id"])
    op.create_index("ix_protocol_runs_user_id", "protocol_runs", ["user_id"])
    op.create_index("ix_protocol_runs_protocol_template_id", "protocol_runs", ["protocol_template_id"])
    op.create_index("idx_protocol_runs_user_status", "protocol_runs", ["user_id", "status"])

    op.create_table(
        "artifact_instances",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("protocol_run_id", sa.Integer(), nullable=False),
        sa.Column("artifact_definition_id", sa.Integer(), nullable=False),
        sa.Column("collected_at", sa.DateTime(), nullable=False),
        sa.Column("payload_json", json_type(), nullable=True),
        sa.Column("computed_json", json_type(), nullable=True),
        sa.Column("source", sa.String(length=50), nullable=True),
        sa.ForeignKeyConstraint(["artifact_definition_id"], ["artifact_definitions.id"]),
        sa.ForeignKeyConstraint(["protocol_run_id"], ["protocol_runs.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_artifact_instances_id", "artifact_instances", ["id"])
    op.create_index("ix_artifact_instances_protocol_run_id", "artifact_instances", ["protocol_run_id"])
    op.create_index("ix_artifact_instances_artifact_definition_id", "artifact_instances", ["artifact_definition_id"])
    op.create_index(
        "idx_artifact_instances_run_definition_collected",
        "artifact_instances",
        ["protocol_run_id", "artifact_definition_id", sa.text("collected_at desc")],
    )

    op.create_table(
        "intervention_templates",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("protocol_template_id", sa.Integer(), nullable=False),
        sa.Column("intervention_key", sa.String(length=100), nullable=False),
        sa.Column("type", sa.String(length=50), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("habit_blueprint_json", json_type(), nullable=True),
        sa.Column("activation_rules_json", json_type(), nullable=True),
        sa.ForeignKeyConstraint(["protocol_template_id"], ["protocol_templates.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_intervention_templates_id", "intervention_templates", ["id"])
    op.create_index("ix_intervention_templates_protocol_template_id", "intervention_templates", ["protocol_template_id"])
    op.create_index("idx_intervention_template_key", "intervention_templates", ["protocol_template_id", "intervention_key"], unique=True)

    op.create_table(
        "protocol_generated_items",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("protocol_run_id", sa.Integer(), nullable=False),
        sa.Column("intervention_template_id", sa.Integer(), nullable=False),
        sa.Column("generated_habit_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["generated_habit_id"], ["habits.id"]),
        sa.ForeignKeyConstraint(["intervention_template_id"], ["intervention_templates.id"]),
        sa.ForeignKeyConstraint(["protocol_run_id"], ["protocol_runs.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_protocol_generated_items_id", "protocol_generated_items", ["id"])
    op.create_index("ix_protocol_generated_items_protocol_run_id", "protocol_generated_items", ["protocol_run_id"])

    op.create_index("idx_habits_program_source", "habits", ["program_id", "source_type", "source_ref_id"])
    op.create_index("idx_checkins_user_metric_date", "check_ins", ["user_id", "metric_key", "check_in_date"])

    op.alter_column("habits", "source_type", server_default=None)


def downgrade() -> None:
    op.drop_index("idx_checkins_user_metric_date", table_name="check_ins")
    op.drop_index("idx_habits_program_source", table_name="habits")

    op.drop_index("ix_protocol_generated_items_protocol_run_id", table_name="protocol_generated_items")
    op.drop_index("ix_protocol_generated_items_id", table_name="protocol_generated_items")
    op.drop_table("protocol_generated_items")

    op.drop_index("idx_intervention_template_key", table_name="intervention_templates")
    op.drop_index("ix_intervention_templates_protocol_template_id", table_name="intervention_templates")
    op.drop_index("ix_intervention_templates_id", table_name="intervention_templates")
    op.drop_table("intervention_templates")

    op.drop_index("idx_artifact_instances_run_definition_collected", table_name="artifact_instances")
    op.drop_index("ix_artifact_instances_artifact_definition_id", table_name="artifact_instances")
    op.drop_index("ix_artifact_instances_protocol_run_id", table_name="artifact_instances")
    op.drop_index("ix_artifact_instances_id", table_name="artifact_instances")
    op.drop_table("artifact_instances")

    op.drop_index("idx_protocol_runs_user_status", table_name="protocol_runs")
    op.drop_index("ix_protocol_runs_protocol_template_id", table_name="protocol_runs")
    op.drop_index("ix_protocol_runs_user_id", table_name="protocol_runs")
    op.drop_index("ix_protocol_runs_id", table_name="protocol_runs")
    op.drop_table("protocol_runs")

    op.drop_index("idx_artifact_definition_template_key", table_name="artifact_definitions")
    op.drop_index("ix_artifact_definitions_protocol_template_id", table_name="artifact_definitions")
    op.drop_index("ix_artifact_definitions_id", table_name="artifact_definitions")
    op.drop_table("artifact_definitions")

    op.drop_index("idx_protocol_phase_template_order", table_name="protocol_phases")
    op.drop_index("ix_protocol_phases_protocol_template_id", table_name="protocol_phases")
    op.drop_index("ix_protocol_phases_id", table_name="protocol_phases")
    op.drop_table("protocol_phases")

    op.drop_index("ix_protocol_templates_code", table_name="protocol_templates")
    op.drop_index("ix_protocol_templates_id", table_name="protocol_templates")
    op.drop_table("protocol_templates")

    op.drop_column("check_ins", "value_text")
    op.drop_column("check_ins", "value_numeric")
    op.drop_column("check_ins", "metric_key")

    op.drop_column("habits", "target_metric_key")
    op.drop_column("habits", "source_ref_id")
    op.drop_column("habits", "source_type")
