import WatchPlayer from "../../../components/WatchPlayer";
export default async function WatchPage({params}:{params:Promise<{id:string}>}){
 const {id}=await params;
 return <main className="container" style={{paddingTop:30}}>
  <a className="muted" href={`/anime/${id}`}>← Kembali ke detail anime</a>
  <h1>AVRWIBUID Player</h1>
  <WatchPlayer animeId={id}/>
 </main>
}
