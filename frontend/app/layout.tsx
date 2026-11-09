import type { Metadata } from "next";
import "./globals.css";
export const metadata: Metadata = {title:"AVRWIBUID — Anime Universe",description:"Jelajahi katalog anime terbaru di AVRWIBUID."};
export default function RootLayout({children}:{children:React.ReactNode}){
 return <html lang="id"><body>{children}</body></html>;
}
