"""empty message

Revision ID: 67f948165779
Revises: 780b5b51bd9b
Create Date: 2020-12-17 22:23:34.562632

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '67f948165779'
down_revision = '780b5b51bd9b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('artist', sa.Column('seeking_description', sa.String(length=500), nullable=True))
    op.add_column('artist', sa.Column('seeking_venue', sa.Boolean(), nullable=False))
    op.add_column('artist', sa.Column('website', sa.String(length=120), nullable=True))
    op.alter_column('artist', 'city',
               existing_type=sa.VARCHAR(length=120),
               nullable=False)
    op.alter_column('artist', 'genres',
               existing_type=sa.VARCHAR(length=120),
               nullable=False)
    op.alter_column('artist', 'name',
               existing_type=sa.VARCHAR(),
               nullable=False)
    op.alter_column('artist', 'phone',
               existing_type=sa.VARCHAR(length=120),
               nullable=False)
    op.alter_column('artist', 'state',
               existing_type=sa.VARCHAR(length=120),
               nullable=False)
    op.add_column('venue', sa.Column('genres', sa.String(length=120), nullable=False))
    op.add_column('venue', sa.Column('seeking_description', sa.String(length=500), nullable=True))
    op.add_column('venue', sa.Column('seeking_talent', sa.Boolean(), nullable=False))
    op.add_column('venue', sa.Column('website', sa.String(length=120), nullable=True))
    op.alter_column('venue', 'address',
               existing_type=sa.VARCHAR(length=120),
               nullable=False)
    op.alter_column('venue', 'city',
               existing_type=sa.VARCHAR(length=120),
               nullable=False)
    op.alter_column('venue', 'name',
               existing_type=sa.VARCHAR(),
               nullable=False)
    op.alter_column('venue', 'phone',
               existing_type=sa.VARCHAR(length=120),
               nullable=False)
    op.alter_column('venue', 'state',
               existing_type=sa.VARCHAR(length=120),
               nullable=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('venue', 'state',
               existing_type=sa.VARCHAR(length=120),
               nullable=True)
    op.alter_column('venue', 'phone',
               existing_type=sa.VARCHAR(length=120),
               nullable=True)
    op.alter_column('venue', 'name',
               existing_type=sa.VARCHAR(),
               nullable=True)
    op.alter_column('venue', 'city',
               existing_type=sa.VARCHAR(length=120),
               nullable=True)
    op.alter_column('venue', 'address',
               existing_type=sa.VARCHAR(length=120),
               nullable=True)
    op.drop_column('venue', 'website')
    op.drop_column('venue', 'seeking_talent')
    op.drop_column('venue', 'seeking_description')
    op.drop_column('venue', 'genres')
    op.alter_column('artist', 'state',
               existing_type=sa.VARCHAR(length=120),
               nullable=True)
    op.alter_column('artist', 'phone',
               existing_type=sa.VARCHAR(length=120),
               nullable=True)
    op.alter_column('artist', 'name',
               existing_type=sa.VARCHAR(),
               nullable=True)
    op.alter_column('artist', 'genres',
               existing_type=sa.VARCHAR(length=120),
               nullable=True)
    op.alter_column('artist', 'city',
               existing_type=sa.VARCHAR(length=120),
               nullable=True)
    op.drop_column('artist', 'website')
    op.drop_column('artist', 'seeking_venue')
    op.drop_column('artist', 'seeking_description')
    # ### end Alembic commands ###
