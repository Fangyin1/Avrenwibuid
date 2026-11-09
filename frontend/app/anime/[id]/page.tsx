const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";
export default async function AnimeDetail({params}:{params:Promise<{id:string}>}){
 const {id}=await params;
 let anime:any=null;
 try {const r=await fetch(`${API}/anime/${id}`,{next:{revalidate:1800}});if(r.ok)anime=await r.json();}catch{}
 if(!anime) return <main className="container"><a href="/">← Kembali</a><h1>Anime tidak ditemukan</h1></main>;
 return <main className="container" style={{paddingTop:30}}>
  <a className="muted" href="/">← Kembali ke beranda</a>
  <div style={{display:"grid",gridTemplateColumns:"minmax(180px,280px) 1fr",gap:28,marginTop:25}}>
   <img className="poster" src={anime.cover||""} alt={anime.title}/>
   <div><span className="pill">{anime.status||"ANIME"}</span><h1>{anime.title}</h1><p className="muted">{anime.genres?.join(" · ")}</p>
   <p>{anime.description?.replace(/<[^>]*>/g,"")||"Belum ada sinopsis."}</p>
   <p className="muted">Episode: {anime.episodes??"TBA"} · Score: {anime.averageScore?anime.averageScore/10:"N/A"}</p>
   <a className="pill" href={`/watch/${id}`}>Lihat episode</a></div>
  </div>
 </main>
}
