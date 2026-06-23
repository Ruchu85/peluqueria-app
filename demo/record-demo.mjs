/**
 * record-demo.mjs — Graba demo-anim.html como video WebM.
 * Uso: node demo/record-demo.mjs
 */
import { chromium } from '@playwright/test';
import { mkdirSync, readdirSync, renameSync, existsSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const ANIM_FILE = join(__dirname, 'landing', 'demo-anim.html');
const VIDEO_DIR = join(__dirname, 'landing', 'video');
const OUT_FILE  = join(VIDEO_DIR, 'demo.webm');

mkdirSync(VIDEO_DIR, { recursive: true });

// Remove previous video if exists so we can detect the new one
if (existsSync(OUT_FILE)) {
  console.log('Eliminando video anterior…');
  const { unlinkSync } = await import('node:fs');
  unlinkSync(OUT_FILE);
}

console.log('Lanzando Chromium…');
const browser = await chromium.launch({ headless: true });

const context = await browser.newContext({
  viewport: { width: 1280, height: 720 },
  recordVideo: {
    dir: VIDEO_DIR,
    size: { width: 1280, height: 720 },
  },
});

const page = await context.newPage();

// Navigate to animation (file:// URL)
const fileUrl = `file:///${ANIM_FILE.replace(/\\/g, '/')}`;
console.log(`Cargando animación: ${fileUrl}`);
await page.goto(fileUrl, { waitUntil: 'domcontentloaded' });

// Wait for full animation (42s) + 1.5s buffer
console.log('Grabando animación de 42 segundos…');
await page.waitForTimeout(43500);

console.log('Cerrando contexto y guardando video…');
await context.close();
await browser.close();

// Find the generated video file (has a random UUID name)
const files = readdirSync(VIDEO_DIR).filter(f => f.endsWith('.webm') && f !== 'demo.webm');
if (files.length === 0) {
  console.error('❌ No se encontró ningún archivo .webm generado.');
  process.exit(1);
}

// Rename to demo.webm
const generated = join(VIDEO_DIR, files[0]);
renameSync(generated, OUT_FILE);
console.log(`✅ Video guardado en: ${OUT_FILE}`);
