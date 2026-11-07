"""Add product photography metadata without changing customer tables."""
from alembic import op
from backend.catalog import initialize_media
revision='002'
down_revision='001'
branch_labels=None
depends_on=None

def upgrade():
    initialize_media(op.get_bind())

def downgrade():
    op.drop_table('product_media')
