"use client";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import Image from "next/image";
import { useTheme } from "@/lib/theme-provider";
import { ThemeToggle } from "./ThemeToggle";

const Header = () => {
  const { theme } = useTheme();
  const scrollToSection = (id: string) => {
    const element = document.getElementById(id);
    if (element) {
      element.scrollIntoView({ behavior: "smooth" });
    }
  };
  return (
    <header className="flex items-center justify-between  ">
      <div className="">
        <Image
          src={"hybrid_logo.svg"}
          alt="Hybrid Logo"
          width={80}
          height={80}
          sizes="80px"
          className={theme === "light" ? "brightness-0" : "brightness-100"}
        />
      </div>
      <div className="flex items-center gap-4">
        <Tabs defaultValue="home">
          <TabsList variant="line">
            <TabsTrigger value="home" onClick={() => scrollToSection("home")}>
              Home
            </TabsTrigger>
            <TabsTrigger value="about" onClick={() => scrollToSection("about")}>
              About
            </TabsTrigger>
            <TabsTrigger value="faq" onClick={() => scrollToSection("faq")}>
              FAQ
            </TabsTrigger>
          </TabsList>
        </Tabs>
        <ThemeToggle />
      </div>
    </header>
  );
};

export default Header;
