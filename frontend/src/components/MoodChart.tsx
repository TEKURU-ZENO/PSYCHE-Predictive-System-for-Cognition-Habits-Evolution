import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';

export default function MoodChart({ data }: { data: any[] }) {
  if (!data || data.length === 0) return <div className="text-gray-500 text-center py-10 mt-8 h-48 border border-dashed border-gray-700 rounded-xl flex items-center justify-center">No mood data to display. Log a mood!</div>;

  return (
    <div className="h-64 w-full mt-4">
      <h3 className="text-gray-400 mb-4 text-sm font-semibold">Intensity Timeline</h3>
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart data={data} margin={{ top: 5, right: 0, left: -20, bottom: 0 }}>
          <defs>
            <linearGradient id="colorIntensity" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#7C3AED" stopOpacity={0.8}/>
              <stop offset="95%" stopColor="#7C3AED" stopOpacity={0}/>
            </linearGradient>
          </defs>
          <XAxis dataKey="time" stroke="#4B5563" fontSize={12} tickLine={false} axisLine={false} />
          <YAxis stroke="#4B5563" fontSize={12} domain={[0, 1]} tickLine={false} axisLine={false} />
          <Tooltip 
            contentStyle={{ backgroundColor: '#111827', border: '1px solid #374151', borderRadius: '8px', color: '#fff' }} 
            itemStyle={{ color: '#A78BFA' }}
          />
          <Area type="monotone" dataKey="intensity" stroke="#9333EA" strokeWidth={3} fillOpacity={1} fill="url(#colorIntensity)" />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}
