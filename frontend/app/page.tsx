import Navbar from "../components/Navbar";
import AnimeGrid from "../components/AnimeGrid";
import {getTrending} from "../lib/api";

export default async function Home(){
 let anime:any[]=[];
 try { anime = await getTrending(); } catch {}
 return <main className="container">
  <Navbar/>
  <section className="hero"><div><span className="pill">YOUR ANIME UNIVERSE</span><h1>Discover your<br/>next story.</h1><p className="muted">Temukan anime favoritmu di AVRWIBUID.</p></div></section>
  <section><h2 className="section-title">Trending Anime</h2><AnimeGrid items={anime}/></section>
  <footer className="muted" style={{padding:"55px 0 30px",fontSize:12}}>© {new Date().getFullYear()} AVRWIBUID. Metadata disediakan oleh AniList.</footer>
 </main>
}
