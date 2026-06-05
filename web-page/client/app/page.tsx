import Image from "next/image";
import HomePage from "@/components/sections/HomePage";
import AboutTeamSection from "@/components/localComps/About";
import { SentimentAnalysisFAQ } from "@/components/localComps/FAQ";

export default function Home() {
  return (
    <div className=" bg-background">
      <main className=" flex items-center w-full">
        <section className="py-6 w-full">
          <HomePage />
          <AboutTeamSection />
          <SentimentAnalysisFAQ />
        </section>
      </main>
    </div>
  );
}
