import { createClient } from "@supabase/supabase-js";

export function createAdminClient() {
  return createClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.SUPABASE_SERVICE_ROLE_KEY!,
    { auth: { autoRefreshToken: false, persistSession: false } }
  );
}

export async function getSalonId(): Promise<string | null> {
  const slug = process.env.NEXT_PUBLIC_SALON_SLUG || "salon-demo";
  const admin = createAdminClient();
  const { data } = await admin.from("salons").select("id").eq("slug", slug).single();
  return data?.id ?? null;
}
