"""Initial schema with all 13 tables

Revision ID: 001
Revises: 
Create Date: 2025-12-16 19:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create companies table
    op.create_table('companies',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    # Create profiles table
    op.create_table('profiles',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('role', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.CheckConstraint("role IN ('OWNER', 'USER')", name='check_role'),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create customers table
    op.create_table('customers',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(), nullable=True),
        sa.Column('email', sa.String(), nullable=True),
        sa.Column('phone', sa.String(), nullable=True),
        sa.Column('city', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create projects table
    op.create_table('projects',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('customer_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(), nullable=True),
        sa.Column('status', sa.String(), server_default='draft', nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ),
        sa.ForeignKeyConstraint(['customer_id'], ['customers.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create facades table
    op.create_table('facades',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('project_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('code', sa.String(), nullable=True),
        sa.Column('duplicated_from', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['duplicated_from'], ['facades.id'], ),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create photos table
    op.create_table('photos',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('facade_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('storage_path', sa.String(), nullable=False),
        sa.Column('quality', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.CheckConstraint("quality IN ('green', 'orange', 'red')", name='check_quality'),
        sa.ForeignKeyConstraint(['facade_id'], ['facades.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create metrage_refs table
    op.create_table('metrage_refs',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('project_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('type', sa.String(), nullable=True),
        sa.Column('width_cm', sa.Numeric(), nullable=True),
        sa.Column('height_cm', sa.Numeric(), nullable=True),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create quotes table
    op.create_table('quotes',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('project_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('status', sa.String(), nullable=True),
        sa.Column('current_version', sa.Integer(), server_default='1', nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create quote_versions table
    op.create_table('quote_versions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('quote_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False),
        sa.Column('total', sa.Numeric(), nullable=True),
        sa.Column('pdf_path', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['quote_id'], ['quotes.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create quote_lines table
    op.create_table('quote_lines',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('quote_version_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('label', sa.String(), nullable=True),
        sa.Column('quantity', sa.Numeric(), nullable=True),
        sa.Column('unit_price', sa.Numeric(), nullable=True),
        sa.Column('total', sa.Numeric(), nullable=True),
        sa.ForeignKeyConstraint(['quote_version_id'], ['quote_versions.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create plans table
    op.create_table('plans',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('max_projects', sa.Integer(), nullable=True),
        sa.Column('max_users', sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    # Insert default plans
    op.execute("""
        INSERT INTO plans (id, max_projects, max_users) VALUES
            ('TRIAL', 1, 1),
            ('PRO', NULL, 1),
            ('ENTREPRISE', NULL, 5)
    """)

    # Create subscriptions table
    op.create_table('subscriptions',
        sa.Column('company_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('plan_id', sa.String(), nullable=True),
        sa.Column('status', sa.String(), nullable=True),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ),
        sa.ForeignKeyConstraint(['plan_id'], ['plans.id'], ),
        sa.PrimaryKeyConstraint('company_id')
    )

    # Create audit_logs table
    op.create_table('audit_logs',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('action', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['profiles.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create indexes
    op.create_index('idx_profiles_company_id', 'profiles', ['company_id'], unique=False)
    op.create_index('idx_customers_company_id', 'customers', ['company_id'], unique=False)
    op.create_index('idx_projects_company_id', 'projects', ['company_id'], unique=False)
    op.create_index('idx_projects_customer_id', 'projects', ['customer_id'], unique=False)
    op.create_index('idx_facades_project_id', 'facades', ['project_id'], unique=False)
    op.create_index('idx_photos_facade_id', 'photos', ['facade_id'], unique=False)
    op.create_index('idx_metrage_refs_project_id', 'metrage_refs', ['project_id'], unique=False)
    op.create_index('idx_quotes_project_id', 'quotes', ['project_id'], unique=False)
    op.create_index('idx_quote_versions_quote_id', 'quote_versions', ['quote_id'], unique=False)
    op.create_index('idx_quote_lines_quote_version_id', 'quote_lines', ['quote_version_id'], unique=False)
    op.create_index('idx_audit_logs_company_id', 'audit_logs', ['company_id'], unique=False)


def downgrade() -> None:
    # Drop indexes
    op.drop_index('idx_audit_logs_company_id', table_name='audit_logs')
    op.drop_index('idx_quote_lines_quote_version_id', table_name='quote_lines')
    op.drop_index('idx_quote_versions_quote_id', table_name='quote_versions')
    op.drop_index('idx_quotes_project_id', table_name='quotes')
    op.drop_index('idx_metrage_refs_project_id', table_name='metrage_refs')
    op.drop_index('idx_photos_facade_id', table_name='photos')
    op.drop_index('idx_facades_project_id', table_name='facades')
    op.drop_index('idx_projects_customer_id', table_name='projects')
    op.drop_index('idx_projects_company_id', table_name='projects')
    op.drop_index('idx_customers_company_id', table_name='customers')
    op.drop_index('idx_profiles_company_id', table_name='profiles')

    # Drop tables in reverse order
    op.drop_table('audit_logs')
    op.drop_table('subscriptions')
    op.drop_table('plans')
    op.drop_table('quote_lines')
    op.drop_table('quote_versions')
    op.drop_table('quotes')
    op.drop_table('metrage_refs')
    op.drop_table('photos')
    op.drop_table('facades')
    op.drop_table('projects')
    op.drop_table('customers')
    op.drop_table('profiles')
    op.drop_table('companies')
