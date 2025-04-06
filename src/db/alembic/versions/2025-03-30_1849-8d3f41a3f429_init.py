"""init

Revision ID: 8d3f41a3f429
Revises:
Create Date: 2025-03-30 18:49:16.135849

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "8d3f41a3f429"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "calculation_results",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("output_files", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("output_data", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "fetched_files",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("file_name", sa.String(), nullable=False),
        sa.Column("file_name_hash", sa.String(), nullable=False),
        sa.Column("molecule_id", sa.String(), nullable=False),
        sa.Column("site", sa.Enum("alphafold", "rcsb_pdb", "pubchem", name="moleculerepositeenum"), nullable=False),
        sa.Column("extension", sa.Enum("cif", "pdb", "sdf", name="moleculefileextensionenum"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "pipelines",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=True),
        sa.Column("user_host", sa.String(), nullable=True),
        sa.Column("requested_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "user_files",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("file_name", sa.String(), nullable=False),
        sa.Column("file_name_hash", sa.String(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "calculation_requests",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("tool_name", sa.Enum("chargefw2", "mole2", "gesamt", name="dockerizedtoolenum"), nullable=False),
        sa.Column(
            "status",
            sa.Enum("pending", "running", "success", "cached", "failure", name="calculationstatusenum"),
            nullable=False,
        ),
        sa.Column("input_files", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("input_data", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("calculation_result_id", sa.Uuid(), nullable=True),
        sa.Column("pipeline_id", sa.Uuid(), nullable=True),
        sa.Column("sequence_number", sa.Integer(), nullable=True),
        sa.Column("user_id", sa.Uuid(), nullable=True),
        sa.Column("user_host", sa.String(), nullable=True),
        sa.Column("requested_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["calculation_result_id"],
            ["calculation_results.id"],
        ),
        sa.ForeignKeyConstraint(
            ["pipeline_id"],
            ["pipelines.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("calculation_requests")
    op.drop_table("user_files")
    op.drop_table("pipelines")
    op.drop_table("fetched_files")
    op.drop_table("calculation_results")
    # ### end Alembic commands ###
