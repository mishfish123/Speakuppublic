"""senators

Revision ID: dc6482344e43
Revises: d37bee519061
Create Date: 2020-09-11 19:10:33.851973

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'dc6482344e43'
down_revision = 'd37bee519061'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('senate',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(length=140), nullable=True),
    sa.Column('Image', sa.String(length=140), nullable=True),
    sa.Column('Surname', sa.String(length=140), nullable=True),
    sa.Column('FirstName', sa.String(length=140), nullable=True),
    sa.Column('PreferredName', sa.String(length=140), nullable=True),
    sa.Column('Email', sa.String(length=140), nullable=True),
    sa.Column('Facebook', sa.String(length=140), nullable=True),
    sa.Column('Twitter', sa.String(length=140), nullable=True),
    sa.Column('Other', sa.String(length=140), nullable=True),
    sa.Column('ElectorateAddress', sa.String(length=140), nullable=True),
    sa.Column('ElectoratePhone', sa.String(length=140), nullable=True),
    sa.Column('ElectoratePostal', sa.String(length=140), nullable=True),
    sa.Column('ElectorateSuburb', sa.String(length=140), nullable=True),
    sa.Column('Titles', sa.String(length=140), nullable=True),
    sa.Column('Postcode', sa.String(length=140), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('senate')
    # ### end Alembic commands ###
