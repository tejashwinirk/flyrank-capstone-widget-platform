CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE tenants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL,
    owner_email VARCHAR(255) NOT NULL UNIQUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE widgets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    type VARCHAR(30) NOT NULL,
    title VARCHAR(150) NOT NULL,
    description TEXT,
    status VARCHAR(20) NOT NULL DEFAULT 'active',
    version INTEGER NOT NULL DEFAULT 1,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT widgets_type_check
        CHECK (type IN ('signup', 'contact', 'cta', 'popover')),

    CONSTRAINT widgets_status_check
        CHECK (status IN ('active', 'inactive'))
);

CREATE TABLE submissions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    widget_id UUID NOT NULL REFERENCES widgets(id) ON DELETE CASCADE,
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,

    name VARCHAR(150),
    email VARCHAR(255),
    message TEXT,

    ip_address INET,
    user_agent TEXT,

    country VARCHAR(100),
    region VARCHAR(100),
    city VARCHAR(100),

    spam BOOLEAN NOT NULL DEFAULT FALSE,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_widgets_tenant_id
    ON widgets(tenant_id);

CREATE INDEX idx_submissions_widget_id
    ON submissions(widget_id);

CREATE INDEX idx_submissions_tenant_id
    ON submissions(tenant_id);

CREATE INDEX idx_submissions_created_at
    ON submissions(created_at);