const axios = require('axios');

const GEMINI_MODEL = 'gemini-2.5-flash';
const GEMINI_API_URL = `https://generativelanguage.googleapis.com/v1beta/models/${GEMINI_MODEL}:generateContent`;

function normalizeField(value) {
  if (typeof value !== 'string') return '';
  return value.trim();
}

function parseJsonResponse(rawText) {
  if (!rawText || typeof rawText !== 'string') {
    throw new Error('Empty Gemini response');
  }

  const cleaned = rawText
    .replace(/^```json/i, '')
    .replace(/^```/, '')
    .replace(/```$/, '')
    .trim();

  try {
    return JSON.parse(cleaned);
  } catch (parseError) {
    const jsonMatch = cleaned.match(/\{[\s\S]*\}/);
    if (!jsonMatch) {
      throw parseError;
    }
    return JSON.parse(jsonMatch[0]);
  }
}

function sanitizeMetadata(parsed) {
  return {
    position: normalizeField(parsed?.position),
    companyName: normalizeField(parsed?.companyName || parsed?.company),
    location: normalizeField(parsed?.location),
  };
}

async function extractJobMetadata(jobDescription) {
  const apiKey = process.env.GEMINI_API_KEY;
  if (!apiKey) {
    throw new Error('Missing GEMINI_API_KEY');
  }

  const prompt = [
    'Extract job metadata from the provided job description.',
    'Return only valid JSON with exactly these keys: position, companyName, location.',
    'Rules:',
    '- Use empty string when a value is not present.',
    '- Do not include additional keys.',
    '- Do not include markdown or explanations.',
    '',
    `Job Description: """${jobDescription}"""`,
  ].join('\n');

  const response = await axios.post(
    `${GEMINI_API_URL}?key=${apiKey}`,
    {
      contents: [
        {
          role: 'user',
          parts: [{ text: prompt }],
        },
      ],
      generationConfig: {
        responseMimeType: 'application/json',
      },
    },
    {
      headers: { 'Content-Type': 'application/json' },
      timeout: 15000,
    }
  );

  const rawText =
    response?.data?.candidates?.[0]?.content?.parts?.[0]?.text ||
    response?.data?.candidates?.[0]?.content?.parts
      ?.map((part) => part?.text || '')
      .join('\n');

  const parsed = parseJsonResponse(rawText);
  return sanitizeMetadata(parsed);
}

module.exports = {
  extractJobMetadata,
};
