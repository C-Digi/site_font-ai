-- Migration 006: Add seed job queue for async B2 rollout

-- Create custom enum for job status
DO $$ BEGIN
    CREATE TYPE public.job_status AS ENUM ('pending', 'processing', 'completed', 'failed');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Create the seed_jobs table
CREATE TABLE IF NOT EXISTS public.seed_jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    font_name TEXT NOT NULL,
    source TEXT NOT NULL,
    source_payload JSONB NOT NULL DEFAULT '{}',
    status public.job_status NOT NULL DEFAULT 'pending',
    attempts INTEGER NOT NULL DEFAULT 0,
    max_attempts INTEGER NOT NULL DEFAULT 3,
    priority INTEGER NOT NULL DEFAULT 0,
    last_error TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    claimed_at TIMESTAMP WITH TIME ZONE,
    finished_at TIMESTAMP WITH TIME ZONE
);

-- Indices for performance
CREATE INDEX IF NOT EXISTS idx_seed_jobs_status_priority_created 
ON public.seed_jobs (status, priority DESC, created_at ASC) 
WHERE status = 'pending';

CREATE INDEX IF NOT EXISTS idx_seed_jobs_updated_at 
ON public.seed_jobs (updated_at);

-- Prevent double-queueing of the same font if it's already being handled
CREATE UNIQUE INDEX IF NOT EXISTS idx_unique_active_seed_job 
ON public.seed_jobs (font_name) 
WHERE status IN ('pending', 'processing');

-- Helper functions for queue management

-- 1. Claim a job
CREATE OR REPLACE FUNCTION public.claim_seed_job(worker_id TEXT DEFAULT NULL)
RETURNS SETOF public.seed_jobs AS $$
BEGIN
    RETURN QUERY
    UPDATE public.seed_jobs
    SET 
        status = 'processing',
        claimed_at = timezone('utc'::text, now()),
        updated_at = timezone('utc'::text, now()),
        attempts = attempts + 1,
        last_error = NULL
    WHERE id = (
        SELECT id
        FROM public.seed_jobs
        WHERE status = 'pending'
          AND attempts < max_attempts
        ORDER BY priority DESC, created_at ASC
        FOR UPDATE SKIP LOCKED
        LIMIT 1
    )
    RETURNING *;
END;
$$ LANGUAGE plpgsql;

-- 2. Complete a job
CREATE OR REPLACE FUNCTION public.complete_seed_job(job_id UUID)
RETURNS VOID AS $$
BEGIN
    UPDATE public.seed_jobs
    SET 
        status = 'completed',
        finished_at = timezone('utc'::text, now()),
        updated_at = timezone('utc'::text, now())
    WHERE id = job_id;
END;
$$ LANGUAGE plpgsql;

-- 3. Fail a job
CREATE OR REPLACE FUNCTION public.fail_seed_job(job_id UUID, error_msg TEXT)
RETURNS VOID AS $$
BEGIN
    UPDATE public.seed_jobs
    SET 
        status = CASE 
            WHEN attempts >= max_attempts THEN 'failed'::public.job_status
            ELSE 'pending'::public.job_status
        END,
        last_error = error_msg,
        updated_at = timezone('utc'::text, now()),
        claimed_at = NULL
    WHERE id = job_id;
END;
$$ LANGUAGE plpgsql;

-- Trigger to automatically update updated_at
CREATE OR REPLACE FUNCTION public.handle_seed_jobs_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = timezone('utc'::text, now());
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DO $$ BEGIN
    CREATE TRIGGER set_seed_jobs_updated_at
    BEFORE UPDATE ON public.seed_jobs
    FOR EACH ROW
    EXECUTE FUNCTION public.handle_seed_jobs_updated_at();
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;
