import Link from "next/link";
export type Anime = {id:number;title:string;cover:string|null;averageScore:number|null;status:string|null};
export default function AnimeCard({anime}:{anime:Anime}){
 return <Link href={`/anime/${anime.id}`} className="card">
  <img className="poster" src={anime.cover || ""} alt={anime.title} loading="lazy"/>
  <h3>{anime.title}</h3>
  <p className="muted" style={{fontSize:12,marginTop:0}}>{anime.status || "Anime"} {anime.averageScore ? `· ★ ${(anime.averageScore/10).toFixed(1)}` : ""}</p>
 </Link>
}
