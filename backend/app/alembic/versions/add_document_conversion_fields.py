"""add document conversion fields for Quill editor integration

Revision ID: add_document_conversion_fields_001
Revises: update_file_schema_001
Create Date: 2025-01-15 18:00:00.000000

"""

from typing import Sequence, Union
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "add_doc_conv_fields"
down_revision: Union[str, Sequence[str], None] = "update_file_schema_001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add document conversion fields for Quill editor integration."""

    # Add new fields for document conversion
    op.add_column('file', sa.Column(
        'original_format', sa.String(length=20), nullable=True))
    op.add_column('file', sa.Column(
        'quill_content', sa.Text(), nullable=True))


def downgrade() -> None:
    """Remove document conversion fields."""

    # Remove the added columns
    op.drop_column('file', 'quill_content')
    op.drop_column('file', 'original_format')
