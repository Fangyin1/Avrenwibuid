"use client";
import { useEffect, useMemo, useRef, useState } from "react";

type Stream = {id:number;label:string;kind:"embed"|"file";url:string;mime_type?:string|null};
type Episode = {id:number;episode_number:number;title:string;streams:Stream[]};

export default function WatchPlayer({animeId}:{animeId:string}) {
  const [episodes,setEpisodes]=useState<Episode[]>([]);
  const [selectedEpisode,setSelectedEpisode]=useState(0);
  const [selectedStream,setSelectedStream]=useState(0);
  const [autoNext,setAutoNext]=useState(true);
  const [error,setError]=useState("");
  const videoRef=useRef<HTMLVideoElement|null>(null);
  const current=episodes[selectedEpisode];
  const stream=current?.streams[selectedStream];

  useEffect(()=>{
    fetch(`${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api"}/episodes/${animeId}`)
      .then(r=>{if(!r.ok) throw new Error("Gagal memuat episode");return r.json();})
      .then(data=>setEpisodes(data.episodes||[]))
      .catch(e=>setError(e.message));
  },[animeId]);

  const nextEpisode=()=>{
    if(selectedEpisode < episodes.length-1) {
      setSelectedEpisode(v=>v+1);
      setSelectedStream(0);
    }
  };

  useEffect(()=>{
    const onMessage=(event:MessageEvent)=>{
      // Embed providers must explicitly implement this documented completion message.
      if(event.data?.type==="AVRWIBUID_EPISODE_ENDED" && stream?.kind==="embed"){
        const allowedOrigin=new URL(stream.url).origin;
        if(event.origin===allowedOrigin && autoNext) nextEpisode();
      }
    };
    window.addEventListener("message",onMessage);
    return ()=>window.removeEventListener("message",onMessage);
  },[stream,autoNext,episodes,selectedEpisode]);

  const isHls=stream?.mime_type==="application/vnd.apple.mpegurl" || stream?.url?.includes(".m3u8");
  useEffect(()=>{
    const video=videoRef.current;
    if(!video || stream?.kind!=="file" || !isHls) return;
    let hls:any;
    import("hls.js").then(({default:Hls})=>{
      if(Hls.isSupported()){
        hls=new Hls();hls.loadSource(stream.url);hls.attachMedia(video);
      } else if(video.canPlayType("application/vnd.apple.mpegurl")) video.src=stream.url;
    }).catch(()=>setError("Tidak dapat memuat pemutar HLS."));
    return ()=>hls?.destroy();
  },[stream,isHls]);

  if(error) return <p className="muted">{error}</p>;
  if(!episodes.length) return <div className="player-empty">Episode belum tersedia. Admin perlu menambahkan episode dan sumber video berizin.</div>;

  return <section className="watch-layout">
    <div>
      <div className="player-frame">
        {!stream ? <div className="player-empty">Belum ada server streaming berizin untuk episode ini.</div> :
          stream.kind==="embed" ?
            <iframe key={stream.id} src={stream.url} title={current.title} allow="autoplay; fullscreen; picture-in-picture" allowFullScreen referrerPolicy="strict-origin-when-cross-origin"/> :
            <video ref={videoRef} key={stream.id} controls playsInline autoPlay onEnded={()=>autoNext&&nextEpisode()} src={isHls?undefined:stream.url}/>
        }
      </div>
      <div className="player-controls">
        <label>Server
          <select value={selectedStream} onChange={e=>setSelectedStream(Number(e.target.value))}>
            {current.streams.map((s,i)=><option key={s.id} value={i}>{s.label}</option>)}
          </select>
        </label>
        <label className="autonext"><input type="checkbox" checked={autoNext} onChange={e=>setAutoNext(e.target.checked)}/> Auto Next</label>
        <button onClick={nextEpisode} disabled={selectedEpisode>=episodes.length-1}>Episode berikutnya →</button>
      </div>
      <h2>{current.title}</h2>
      <p className="muted">Episode {current.episode_number}</p>
    </div>
    <aside className="episode-panel">
      <h3>Daftar Episode</h3>
      {episodes.map((ep,i)=><button key={ep.id} className={i===selectedEpisode?"episode active":"episode"} onClick={()=>{setSelectedEpisode(i);setSelectedStream(0);}}>
        <span>Episode {ep.episode_number}</span><small>{ep.title}</small>
      </button>)}
    </aside>
  </section>;
}
