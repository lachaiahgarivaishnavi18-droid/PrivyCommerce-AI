"""Initial academic demo schema."""
from alembic import op
from backend.main import initialize_schema
revision='001'
down_revision=None
branch_labels=None
depends_on=None

def upgrade():
    initialize_schema(op.get_bind())

def downgrade():
    for table in ['nodes','audit','orders','cart','memory','consent','sessions','users']:
        op.drop_table(table)
