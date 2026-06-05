import Image from "next/image";
export default function AboutTeamSection() {
  const teamMembers = [
    { id: 1, name: "benyahya abdel ghafour", role: "leader." },
    { id: 2, name: "Dehina abdelhakim", role: "front-end dev" },
    { id: 3, name: "boulmehad abderrahmane", role: "back-end dev " },
  ];
  const socials = [
    {
      name: "github",
      icon: (
        <svg role="img" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
          <title>GitHub</title>
          <path d="M12 .297c-6.63 0-12 5.373-12 12 0 5.303 3.438 9.8 8.205 11.385.6.113.82-.258.82-.577 0-.285-.01-1.04-.015-2.04-3.338.724-4.042-1.61-4.042-1.61C4.422 18.07 3.633 17.7 3.633 17.7c-1.087-.744.084-.729.084-.729 1.205.084 1.838 1.236 1.838 1.236 1.07 1.835 2.809 1.305 3.495.998.108-.776.417-1.305.76-1.605-2.665-.3-5.466-1.332-5.466-5.93 0-1.31.465-2.38 1.235-3.22-.135-.303-.54-1.523.105-3.176 0 0 1.005-.322 3.3 1.23.96-.267 1.98-.399 3-.405 1.02.006 2.04.138 3 .405 2.28-1.552 3.285-1.23 3.285-1.23.645 1.653.24 2.873.12 3.176.765.84 1.23 1.91 1.23 3.22 0 4.61-2.805 5.625-5.475 5.92.42.36.81 1.096.81 2.22 0 1.606-.015 2.896-.015 3.286 0 .315.21.69.825.57C20.565 22.092 24 17.592 24 12.297c0-6.627-5.373-12-12-12" />
        </svg>
      ),
    },
    {
      name: "Facebook",
      icon: (
        <svg role="img" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
          <title>Facebook</title>
          <path d="M9.101 23.691v-7.98H6.627v-3.667h2.474v-1.58c0-4.085 1.848-5.978 5.858-5.978.401 0 .955.042 1.468.103a8.68 8.68 0 0 1 1.141.195v3.325a8.623 8.623 0 0 0-.653-.036 26.805 26.805 0 0 0-.733-.009c-.707 0-1.259.096-1.675.309a1.686 1.686 0 0 0-.679.622c-.258.42-.374.995-.374 1.752v1.297h3.919l-.386 2.103-.287 1.564h-3.246v8.245C19.396 23.238 24 18.179 24 12.044c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.628 3.874 10.35 9.101 11.647Z" />
        </svg>
      ),
    },
    {
      name: "X",
      icon: (
        <svg role="img" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
          <title>X</title>
          <path d="M14.234 10.162 22.977 0h-2.072l-7.591 8.824L7.251 0H.258l9.168 13.343L.258 24H2.33l8.016-9.318L16.749 24h6.993zm-2.837 3.299-.929-1.329L3.076 1.56h3.182l5.965 8.532.929 1.329 7.754 11.09h-3.182z" />
        </svg>
      ),
    },
  ];
  return (
    <section className="bg-background py-16 md:py-24">
      <div>
        <div className="text-center mb-12 sm:mb-16">
          <p className="text-xs uppercase tracking-[0.3em] text-muted-foreground/80 mb-2">
            YOUR SUBTITLE GOES HERE
          </p>
          <h2 className="text-4xl md:text-5xl font-bold uppercase tracking-wider text-foreground mb-6">
            MEET OUR TEAM
          </h2>
          <p className="text-muted-foreground/50 dark:text-muted-foreground dark:brightness-120 text-sm leading-relaxed">
            We are a team of passionate developers focused on building
            intelligent solutions to real-world problems. Our project leverages
            artificial intelligence to analyze data, automate decision-making,
            and deliver efficient, scalable results. We aim to bridge the gap
            between innovation and practical impact through smart, user-centered
            design.
          </p>
        </div>

        <div className="h-[400px] grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-12 lg:gap-16">
          {teamMembers.map((member) => (
            <div key={member.id} className="flex flex-col items-center">
              <div className="w-80 h-92 bg-foreground/50 mb-6 grayscale overflow-hidden group rounded-lg"></div>
              <div className="flex flex-col">
                <h3 className="text-center text-lg font-bold uppercase  tracking-wide text-foreground mb-1">
                  {member.name}
                </h3>
                <p className="text-xs text-muted-foreground/50 text-center mb-4">
                  {member.role}
                </p>
              </div>

              <ul className="flex items-center space-x-2 mt-auto rounded-full gap-4">
                {socials.map((icon, i) => (
                  <li className="w-4 h-4" key={i}>
                    {icon.icon}
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
