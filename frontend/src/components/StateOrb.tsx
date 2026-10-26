export default function StateOrb({ emotion }: { emotion: string }) {
  const moodStyles: Record<string, string> = {
    stressed: "from-red-500 to-orange-500",
    calm: "from-cyan-400 to-blue-500",
    motivated: "from-purple-500 to-pink-500",
    fatigued: "from-gray-500 to-slate-700 blur-sm",
    neutral: "from-gray-600 to-gray-400"
  };

  const animStyles: Record<string, string> = {
    stressed: "animate-ping",
    calm: "animate-pulse",
    motivated: "animate-bounce",
    fatigued: "opacity-50",
    neutral: ""
  };

  const activeStyle = moodStyles[emotion] || moodStyles.neutral;
  const activeAnim = animStyles[emotion] || animStyles.neutral;

  return (
    <div className="flex justify-center items-center h-48 w-48 relative mx-auto my-8 group cursor-pointer transition-transform duration-500 hover:scale-105 active:scale-95">
      <div className={`absolute inset-0 rounded-full bg-gradient-to-br ${activeStyle} ${activeAnim} transition-all duration-700 shadow-xl opacity-90 group-hover:opacity-100`}></div>
      <div className={`absolute inset-2 rounded-full bg-gradient-to-tl ${activeStyle} bg-opacity-70 blur-xl group-hover:blur-2xl transition-all duration-700`}></div>
    </div>
  );
}
