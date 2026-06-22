import { test, expect } from "@playwright/test";
import { createServerClient } from "@supabase/ssr";
import { mkdirSync, readFileSync } from "node:fs";
import { join } from "node:path";

const OUT = join(__dirname, "screenshots");
mkdirSync(OUT, { recursive: true });

const EMAIL = process.env.DEMO_EMAIL || "demo@salondemo.es";
const PASSWORD = process.env.DEMO_PASSWORD || "DemoSalon2026!";

// Lee .env.local sin dependencias
function loadEnv(): Record<string, string> {
  const raw = readFileSync(join(__dirname, "..", ".env.local"), "utf8");
  const env: Record<string, string> = {};
  for (const line of raw.split("\n")) {
    const m = line.match(/^\s*([A-Z0-9_]+)\s*=\s*(.*)\s*$/i);
    if (m) env[m[1]] = m[2].replace(/^["']|["']$/g, "").trim();
  }
  return env;
}

// Genera las cookies de sesión usando la MISMA librería que la app
// (@supabase/ssr) y las inyecta en el contexto del navegador.
async function injectSession(context: import("@playwright/test").BrowserContext) {
  const env = loadEnv();
  const captured: { name: string; value: string }[] = [];
  const supa = createServerClient(
    env.NEXT_PUBLIC_SUPABASE_URL,
    env.NEXT_PUBLIC_SUPABASE_ANON_KEY,
    {
      cookies: {
        getAll: () => [],
        setAll: (cookies: { name: string; value: string }[]) => {
          for (const c of cookies) captured.push({ name: c.name, value: c.value });
        },
      },
    }
  );
  const { error } = await supa.auth.signInWithPassword({ email: EMAIL, password: PASSWORD });
  if (error) throw new Error("Login Supabase falló: " + error.message);
  if (captured.length === 0) throw new Error("No se capturó ninguna cookie de sesión");

  await context.addCookies(
    captured.map((c) => ({
      name: c.name,
      value: c.value,
      domain: "localhost",
      path: "/",
      httpOnly: false,
      secure: false,
      sameSite: "Lax" as const,
      expires: Math.floor(Date.now() / 1000) + 60 * 60 * 24,
    }))
  );
}

const SHOTS = [
  { path: "/dashboard", name: "01-resumen" },
  { path: "/dashboard/calendario", name: "02-calendario" },
  { path: "/dashboard/citas", name: "03-citas" },
  { path: "/dashboard/clientes", name: "04-clientes" },
  { path: "/dashboard/informes", name: "05-informes" },
  { path: "/dashboard/caja", name: "06-caja" },
] as const;

test("login y capturas de pantallas", async ({ page, context }) => {
  // --- Login: inyectar sesión directamente (robusto) ---
  await injectSession(context);
  await page.goto("/dashboard", { waitUntil: "domcontentloaded" });
  await page.waitForTimeout(1500);
  expect(/\/dashboard/.test(page.url()) && !/\/login/.test(page.url()), "no se inició sesión").toBe(true);

  // --- Capturas desktop (full page) ---
  for (const shot of SHOTS) {
    await page.goto(shot.path, { waitUntil: "domcontentloaded" });
    await page.waitForTimeout(1800); // dejar que rendericen gráficos/listas
    await page.screenshot({
      path: join(OUT, `${shot.name}.png`),
      fullPage: true,
    });
    console.log(`  captura: ${shot.name}.png`);
  }

  // --- Capturas móvil del calendario y resumen (mobile-first) ---
  await page.setViewportSize({ width: 414, height: 896 });
  for (const shot of [SHOTS[0], SHOTS[1]]) {
    await page.goto(shot.path, { waitUntil: "domcontentloaded" });
    await page.waitForTimeout(1500);
    await page.screenshot({
      path: join(OUT, `mobile-${shot.name}.png`),
      fullPage: true,
    });
    console.log(`  captura: mobile-${shot.name}.png`);
  }

  expect(true).toBe(true);
});
