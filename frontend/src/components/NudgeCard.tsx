import { useState, useEffect } from 'react';
import { X, Sparkles, ThumbsUp, ThumbsDown } from 'lucide-react';
import { sendFeedback } from "@/lib/api";

export default function NudgeCard({ nudge, onClose }: { nudge: any | null, onClose: () => void }) {
  const [visible, setVisible] = useState(false);
  const [feedbackSent, setFeedbackSent] = useState(false);

  useEffect(() => {
    if (nudge) {
      setVisible(true);
      setFeedbackSent(false); // Reset on new nudge
      const timer = setTimeout(() => {
        setVisible(false);
        setTimeout(onClose, 300); // Wait for transition
      }, 15000); // extended auto-close to read stats and vote
      return () => clearTimeout(timer);
    }
  }, [nudge, onClose]);

  if (!nudge) return null;

  const handleFeedback = async (rating: number) => {
    setFeedbackSent(true);
    try {
      if (nudge.state_key && nudge.action) {
        await sendFeedback(nudge.state_key, nudge.action, rating);
      }
    } catch(e) {}
  };

  return (
    <div className={`fixed bottom-8 right-8 p-6 w-[400px] rounded-2xl bg-[#111827] border border-gray-700 shadow-2xl transition-all duration-300 transform group z-50 ${visible ? 'translate-x-0 opacity-100' : 'translate-x-full opacity-0'}`}>
      <button onClick={() => { setVisible(false); setTimeout(onClose, 300); }} className="absolute top-4 right-4 text-gray-500 hover:text-white transition">
        <X size={18} />
      </button>

      <div className="flex items-center space-x-3 mb-4">
        <div className="p-2 bg-purple-500/20 rounded-xl text-purple-400 shadow-inner">
          <Sparkles size={24} />
        </div>
        <div>
          <h3 className="font-semibold text-lg capitalize text-white">{nudge.action ? nudge.action.replace(/_/g, " ") : "Action"}</h3>
        </div>
      </div>
      
      {nudge.confidence > 0 && nudge.q_score > 0 ? (
        <p className="text-purple-300 text-sm mb-4">
          This system intervention has helped you reduce stress {(nudge.q_score * 100).toFixed(0)}% of the time.
        </p>
      ) : (
         <p className="text-gray-400 text-sm mb-4">Adaptive Learning Pattern Started...</p>
      )}

      <p className="text-gray-200 text-sm bg-gray-900/50 p-4 rounded-xl italic border border-gray-800">
        "{nudge.text}"
      </p>

      {nudge.confidence > 0 && (
         <div className="text-xs text-gray-500 mt-3 text-right">Based on {nudge.visits} prior experiences</div>
      )}

      {/* Explicit Feedback Hook */}
      {!feedbackSent ? (
        <div className="mt-4 pt-4 border-t border-gray-800 flex justify-between items-center opacity-0 group-hover:opacity-100 transition-opacity duration-300">
            <span className="text-xs text-gray-400 font-medium tracking-wide">Was this effective?</span>
            <div className="flex space-x-2">
               <button onClick={() => handleFeedback(1.0)} className="p-2 bg-green-900/20 text-green-400 border border-green-500/20 hover:bg-green-900/40 rounded-lg transition"><ThumbsUp size={14}/></button>
               <button onClick={() => handleFeedback(-1.0)} className="p-2 bg-red-900/20 text-red-400 border border-red-500/20 hover:bg-red-900/40 rounded-lg transition"><ThumbsDown size={14}/></button>
            </div>
        </div>
      ) : (
        <div className="mt-4 pt-4 border-t border-gray-800 flex justify-end">
             <span className="text-xs text-purple-400 font-medium animate-pulse">Feedback integrated into learning model.</span>
        </div>
      )}
    </div>
  );
}
