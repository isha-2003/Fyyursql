"""Initial migration.

Revision ID: 4dc5efd967ce
Revises: 
Create Date: 2025-04-03 14:19:11.459328

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4dc5efd967ce'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('artists',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('city', sa.String(length=120), nullable=False),
    sa.Column('state', sa.String(length=120), nullable=False),
    sa.Column('phone', sa.String(length=120), nullable=True),
    sa.Column('genres', sa.ARRAY(sa.String()), nullable=False),
    sa.Column('image_link', sa.String(length=500), nullable=True),
    sa.Column('facebook_link', sa.String(length=120), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('venues',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('city', sa.String(length=120), nullable=False),
    sa.Column('state', sa.String(length=120), nullable=False),
    sa.Column('address', sa.String(length=120), nullable=False),
    sa.Column('phone', sa.String(length=120), nullable=True),
    sa.Column('image_link', sa.String(length=500), nullable=True),
    sa.Column('facebook_link', sa.String(length=120), nullable=True),
    sa.Column('genres', sa.ARRAY(sa.String()), nullable=False),
    sa.Column('website', sa.String(length=250), nullable=True),
    sa.Column('seeking_talent', sa.Boolean(), nullable=True),
    sa.Column('seeking_description', sa.String(length=250), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('shows',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('artist_id', sa.Integer(), nullable=False),
    sa.Column('venue_id', sa.Integer(), nullable=False),
    sa.Column('start_time', sa.DateTime(), nullable=False),
    sa.Column('venue_name', sa.Integer(), nullable=False),
    sa.Column('artist_name', sa.Integer(), nullable=False),
    sa.Column('venue_city', sa.Integer(), nullable=False),
    sa.Column('artist_city', sa.Integer(), nullable=False),
    sa.Column('venue_state', sa.Integer(), nullable=False),
    sa.Column('artist_state', sa.Integer(), nullable=False),
    sa.Column('venue_phone', sa.Integer(), nullable=False),
    sa.Column('artist_phone', sa.Integer(), nullable=False),
    sa.Column('venue_website', sa.Integer(), nullable=False),
    sa.Column('venue_genres', sa.Integer(), nullable=False),
    sa.Column('artist_genres', sa.Integer(), nullable=False),
    sa.Column('venue_address', sa.Integer(), nullable=False),
    sa.Column('venue_facebook_link', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['artist_city'], ['artist.city'], ),
    sa.ForeignKeyConstraint(['artist_genres'], ['artist.genres'], ),
    sa.ForeignKeyConstraint(['artist_id'], ['artist.id'], ),
    sa.ForeignKeyConstraint(['artist_name'], ['artist.name'], ),
    sa.ForeignKeyConstraint(['artist_phone'], ['artist.phone'], ),
    sa.ForeignKeyConstraint(['artist_state'], ['artist.state'], ),
    sa.ForeignKeyConstraint(['venue_address'], ['venue.address'], ),
    sa.ForeignKeyConstraint(['venue_city'], ['venue.city'], ),
    sa.ForeignKeyConstraint(['venue_facebook_link'], ['venue.facebook_link'], ),
    sa.ForeignKeyConstraint(['venue_genres'], ['venue.genres'], ),
    sa.ForeignKeyConstraint(['venue_id'], ['venue.id'], ),
    sa.ForeignKeyConstraint(['venue_name'], ['venue.name'], ),
    sa.ForeignKeyConstraint(['venue_phone'], ['venue.phone'], ),
    sa.ForeignKeyConstraint(['venue_state'], ['venue.state'], ),
    sa.ForeignKeyConstraint(['venue_website'], ['venue.website'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('shows')
    op.drop_table('venues')
    op.drop_table('artists')
    # ### end Alembic commands ###
