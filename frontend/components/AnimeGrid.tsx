import AnimeCard, {Anime} from "./AnimeCard";
export default function AnimeGrid({items}:{items:Anime[]}){
 if(!items.length) return <p className="muted">Belum ada anime yang ditemukan.</p>;
 return <div className="grid">{items.map(a=><AnimeCard key={a.id} anime={a}/>)}</div>
}
