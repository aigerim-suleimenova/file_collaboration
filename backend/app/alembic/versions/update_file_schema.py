"""update file schema for S3 integration

Revision ID: update_file_schema_001
Revises: 5566abc09711
Create Date: 2025-01-15 17:00:00.000000

"""

from typing import Sequence, Union
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "update_file_schema_001"
down_revision: Union[str, Sequence[str], None] = "5566abc09711"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema for S3 integration."""

    # Add new S3-related columns to existing file table
    op.add_column('file', sa.Column(
        's3_key', sa.String(length=500), nullable=True))
    op.add_column('file', sa.Column(
        'file_size', sa.BigInteger(), nullable=True))
    op.add_column('file', sa.Column(
        'mime_type', sa.String(length=100), nullable=True))
    op.add_column('file', sa.Column(
        'created_at', sa.DateTime(), nullable=True))
    op.add_column('file', sa.Column(
        'updated_at', sa.DateTime(), nullable=True))

    # Create index for s3_key
    op.create_index(op.f("ix_file_s3_key"), "file", ["s3_key"], unique=False)

    # Drop the old content column (after ensuring data is migrated if needed)
    op.drop_column('file', 'content')


def downgrade() -> None:
    """Downgrade schema."""
    # Remove S3-related columns
    op.drop_index(op.f("ix_file_s3_key"), table_name="file")
    op.drop_column('file', 's3_key')
    op.drop_column('file', 'file_size')
    op.drop_column('file', 'mime_type')
    op.drop_column('file', 'created_at')
    op.drop_column('file', 'updated_at')

    # Recreate the old content column
    op.add_column('file', sa.Column('content', sa.Text(), nullable=True))
