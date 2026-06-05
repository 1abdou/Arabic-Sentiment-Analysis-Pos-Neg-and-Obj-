"use client";

import FormUser from "../localComps/FormUser";

const HomePage = () => {
  const value = 25;
  return (
    <div className="flex flex-col gap-4 mx-auto w-full pt-6">
      <div className="flex flex-col items-center text-center space-y-2 mb-8 mx-auto w-full">
        <span className="text-xs font-semibold tracking-widest uppercase text-primary">
          AI-Powered Insights
        </span>

        <h1 className="text-6xl w-[80%] font-extrabold tracking-tight leading-18  text-foreground">
          Uncover Hidden Emotional Intelligence
        </h1>
      </div>
      <div className="w-full min-h-[200px]">
        <FormUser />
      </div>
  
    </div>
  );
};

export default HomePage;
