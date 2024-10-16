"""add sub_parts_count to book_part

Revision ID: a6f9822d382c
Revises: f8b3da9280b7
Create Date: 2024-09-28 15:55:27.133315

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a6f9822d382c'
down_revision: Union[str, None] = 'f8b3da9280b7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('book_parts', sa.Column('sub_parts_count', sa.Integer(), server_default=sa.text('1'), nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('book_parts', 'sub_parts_count')
    # ### end Alembic commands ###
