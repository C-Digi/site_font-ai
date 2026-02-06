import * as dotenv from 'dotenv';
import { supabase } from '../src/lib/supabase';
import { enqueueSeedJob } from '../src/lib/jobs';

dotenv.config({ path: '.env.local', override: true });

const DRY_RUN = process.argv.includes('--dry-run');
const BATCH_SIZE = parseInt(process.env.BACKFILL_CHUNK_SIZE || '100', 10);

async function backfill() {
  console.log(`Starting B2 backfill... ${DRY_RUN ? '[DRY RUN]' : ''}`);

  // We'll fetch fonts that haven't been processed by the new worker yet.
  // For now, we'll just fetch all fonts and let the queue deduplication handle it,
  // or we could filter by updated_at if we had a cut-off date.
  
  let count = 0;
  let enqueued = 0;
  let skipped = 0;

  const { data: fonts, error } = await supabase
    .from('fonts')
    .select('name, source, category, tags, description, files');

  if (error) {
    console.error('Error fetching fonts:', error);
    return;
  }

  console.log(`Found ${fonts.length} fonts in database.`);

  for (let i = 0; i < fonts.length; i += BATCH_SIZE) {
    const batch = fonts.slice(i, i + BATCH_SIZE);
    
    for (const font of batch) {
      count++;
      if (DRY_RUN) {
        console.log(`[DRY RUN] Would enqueue: ${font.name}`);
        enqueued++;
        continue;
      }

      const { error: enqueueError, alreadyExists } = await enqueueSeedJob({
        font_name: font.name,
        source: font.source || 'Google Fonts',
        source_payload: {
          category: font.category,
          tags: font.tags,
          description: font.description,
          files: font.files
        },
        priority: 0 // Backfill jobs have lower priority than JIT
      });

      if (enqueueError) {
        console.error(`Failed to enqueue ${font.name}:`, enqueueError);
      } else if (alreadyExists) {
        skipped++;
      } else {
        enqueued++;
      }
    }
    
    console.log(`Progress: ${count}/${fonts.length} (Enqueued: ${enqueued}, Skipped: ${skipped})`);
  }

  console.log(`Backfill complete. Total fonts: ${count}, Enqueued: ${enqueued}, Already in queue: ${skipped}`);
}

backfill().catch(err => {
  console.error('Backfill failed:', err);
  process.exit(1);
});
