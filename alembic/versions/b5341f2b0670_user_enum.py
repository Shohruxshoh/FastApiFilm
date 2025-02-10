"""user enum

Revision ID: b5341f2b0670
Revises: 81283e677368
Create Date: 2025-02-09 21:25:04.384294

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import ENUM

# revision identifiers, used by Alembic.
revision: str = 'b5341f2b0670'
down_revision: Union[str, None] = '81283e677368'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

role_enum = ENUM("admin", "user", name="roleenum", create_type=True)

def upgrade() -> None:
    role_enum.create(op.get_bind(), checkfirst=True)
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('hashed_password', sa.String(), nullable=False))
    op.add_column('users', sa.Column("role", role_enum, nullable=False, server_default="user"))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'role')
    op.drop_column('users', 'hashed_password')
    # ### end Alembic commands ###
