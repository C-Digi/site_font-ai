const fs = require('fs');
const path = require('path');
require('dotenv').config({ path: '.env.local' });

const OUTPUT_FILE = path.join(process.cwd(), 'openrouter_multimodal_models.json');
const JAN_2024_TIMESTAMP = 1704067200;

async function consolidateModels() {
  try {
    console.log('Fetching models from OpenRouter...');
    const response = await fetch('https://openrouter.ai/api/v1/models');
    if (!response.ok) {
      throw new Error(`Failed to fetch models: ${response.statusText}`);
    }

    const { data } = await response.json();
    console.log(`Total models fetched: ${data.length}`);

    const filteredModels = data.filter(model => {
      const inputModalities = model.architecture?.input_modalities || [];
      const outputModalities = model.architecture?.output_modalities || [];
      const created = model.created || 0;

      const hasImageInput = inputModalities.includes('image');
      const hasTextOutput = outputModalities.includes('text');
      const isNewEnough = created >= JAN_2024_TIMESTAMP;

      return hasImageInput && hasTextOutput && isNewEnough;
    });

    console.log(`Filtered models (Image Input, Text Output, Released after Jan 2024): ${filteredModels.length}`);

    const consolidatedData = filteredModels.map(model => ({
      id: model.id,
      name: model.name,
      created: new Date(model.created * 1000).toISOString(),
      description: model.description,
      pricing: model.pricing,
      context_length: model.context_length,
      architecture: model.architecture,
      top_provider: model.top_provider
    }));

    fs.writeFileSync(OUTPUT_FILE, JSON.stringify(consolidatedData, null, 2));
    console.log(`Successfully saved consolidated data to ${OUTPUT_FILE}`);

  } catch (error) {
    console.error('Error:', error.message);
    process.exit(1);
  }
}

consolidateModels();
