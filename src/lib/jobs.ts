import { supabase } from './supabase';
import { SeedJob } from './types';

/**
 * Enqueue a new seed job.
 * Deduplication is handled by the database (unique index on font_name for active jobs).
 */
export async function enqueueSeedJob(job: {
  font_name: string;
  source: string;
  source_payload?: any;
  priority?: number;
}) {
  const { data, error } = await supabase
    .from('seed_jobs')
    .insert([
      {
        font_name: job.font_name,
        source: job.source,
        source_payload: job.source_payload || {},
        priority: job.priority || 0,
        status: 'pending',
      },
    ])
    .select()
    .single();

  if (error) {
    // Code 23505 is unique_violation in Postgres (handled by our partial unique index)
    if (error.code === '23505') {
      return { data: null, error: null, alreadyExists: true };
    }
    return { data: null, error };
  }

  return { data: data as SeedJob, error: null, alreadyExists: false };
}

/**
 * Claim the next available job from the queue using the atomic claim_seed_job RPC.
 */
export async function claimSeedJob(workerId?: string) {
  const { data, error } = await supabase.rpc('claim_seed_job', {
    worker_id: workerId || null,
  });

  if (error) return { data: null, error };
  
  // rpc returns a list, even if it's one row
  const jobs = data as SeedJob[];
  return { data: jobs.length > 0 ? jobs[0] : null, error: null };
}

/**
 * Mark a job as completed.
 */
export async function completeSeedJob(jobId: string) {
  const { error } = await supabase.rpc('complete_seed_job', {
    job_id: jobId,
  });

  return { error };
}

/**
 * Mark a job as failed. Updates status to 'failed' if max attempts reached, else back to 'pending'.
 */
export async function failSeedJob(jobId: string, errorMsg: string) {
  const { error } = await supabase.rpc('fail_seed_job', {
    job_id: jobId,
    error_msg: errorMsg,
  });

  return { error };
}
