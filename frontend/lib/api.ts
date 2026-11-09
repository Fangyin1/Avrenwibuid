const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";

export async function getTrending() {
  const response = await fetch(`${API}/anime/trending`, { next: { revalidate: 1800 } });
  if (!response.ok) throw new Error("Gagal mengambil katalog anime");
  return response.json();
}
export async function searchAnime(q: string) {
  const response = await fetch(`${API}/anime/search?q=${encodeURIComponent(q)}`, { cache: "no-store" });
  if (!response.ok) throw new Error("Pencarian gagal");
  return response.json();
}
