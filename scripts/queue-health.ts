import * as dotenv from 'dotenv';
import { supabase } from '../src/lib/supabase';

dotenv.config({ path: '.env.local', override: true });

async function checkHealth() {
  console.log('--- Queue Health Check ---');

  const { data: stats, error } = await supabase
    .from('seed_jobs')
    .select('status, attempts');

  if (error) {
    console.error('Error fetching job stats:', error);
    return;
  }

  const counts = stats.reduce((acc: any, job: any) => {
    acc[job.status] = (acc[job.status] || 0) + 1;
    if (job.attempts > 0) acc.total_attempts = (acc.total_attempts || 0) + job.attempts;
    return acc;
  }, { pending: 0, processing: 0, completed: 0, failed: 0, total_attempts: 0 });

  console.log(`Pending:    ${counts.pending}`);
  console.log(`Processing: ${counts.processing}`);
  console.log(`Completed:  ${counts.completed}`);
  console.log(`Failed:     ${counts.failed}`);
  console.log(`Total Jobs: ${stats.length}`);
  console.log(`Avg Attempts: ${(counts.total_attempts / stats.length || 0).toFixed(2)}`);

  if (counts.failed > 0) {
    console.log('\n--- Recent Failures ---');
    const { data: failures } = await supabase
      .from('seed_jobs')
      .select('font_name, last_error, updated_at')
      .eq('status', 'failed')
      .order('updated_at', { ascending: false })
      .limit(5);
    
    failures?.forEach(f => {
      console.log(`[${f.updated_at}] ${f.font_name}: ${f.last_error}`);
    });
  }

  if (counts.processing > 0) {
    console.log('\n--- Stuck Jobs? (Processing > 10m) ---');
    const tenMinsAgo = new Date(Date.now() - 10 * 60 * 1000).toISOString();
    const { data: stuck } = await supabase
      .from('seed_jobs')
      .select('font_name, claimed_at')
      .eq('status', 'processing')
      .lt('claimed_at', tenMinsAgo);
    
    if (stuck && stuck.length > 0) {
      stuck.forEach(s => console.log(`- ${s.font_name} (Claimed: ${s.claimed_at})`));
    } else {
      console.log('None found.');
    }
  }
}

checkHealth().catch(console.error);
