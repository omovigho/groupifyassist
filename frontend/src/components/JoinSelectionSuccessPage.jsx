import { useEffect } from 'react';
import { useLocation, useNavigate, Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';

const Confetti = () => {
  const pieces = Array.from({ length: 80 });
  return (
    <div className="pointer-events-none absolute inset-0 overflow-hidden">
      {pieces.map((_, i) => (
        <span
          key={i}
          className="absolute block w-2 h-3 rounded-sm opacity-80"
          style={{
            left: `${(i * 13) % 100}%`,
            top: `-${Math.random() * 20 + 5}%`,
            backgroundColor: [
              '#60A5FA',
              '#A78BFA',
              '#34D399',
              '#F472B6',
              '#FBBF24',
              '#22D3EE',
            ][i % 6],
            animation: `confetti-fall ${6 + (i % 5)}s linear ${i * 0.05}s forwards`,
            transform: `rotate(${(i * 47) % 360}deg)`,
          }}
        />
      ))}
    </div>
  );
};

const JoinSelectionSuccessPage = () => {
  const navigate = useNavigate();
  const { state } = useLocation();

  useEffect(() => {
    if (!state) {
      navigate('/selection/join', { replace: true });
    }
  }, [state, navigate]);

  if (!state) return null;

  return (
    <div className="min-h-screen dark-navy-bg relative overflow-hidden flex items-center justify-center px-6">
      <Confetti />
      <div className="relative z-10 text-center max-w-2xl glass-morphism rounded-2xl p-8">
        <div className="mb-4">
          <div className="mx-auto mb-4 w-20 h-20 rounded-full bg-green-500/20 flex items-center justify-center animate-[fadeIn_0.6s_ease]">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-10 h-10 text-green-400">
              <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" />
              <polyline points="22 4 12 14.01 9 11.01" />
            </svg>
          </div>
          <h1 className="text-3xl md:text-4xl font-bold gradient-text">You're In! 🎉</h1>
          <p className="text-gray-300 mt-2">{state?.message || 'Successfully joined the selection session.'}</p>
        </div>

        <div className="text-left bg-white/5 rounded-xl p-5 border border-white/10">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-sm">
            <div className="text-gray-400">Session</div>
            <div className="font-medium">{state?.session}</div>
            <div className="text-gray-400">Identifier</div>
            <div className="font-medium break-all">{state?.member_identifier}</div>
          </div>
        </div>

        <div className="mt-6 flex items-center justify-center gap-3">
          <Link to="/">
            <Button className="bg-white text-slate-900 hover:bg-gray-100 rounded-lg font-semibold">Go Home</Button>
          </Link>
          <Link to="/selection/join">
            <Button variant="outline" className="border-white/20 text-white hover:bg-white/10">Join Another</Button>
          </Link>
        </div>
      </div>

      <style>{`
        @keyframes confetti-fall {
          0% { transform: translateY(-10%) rotate(0deg); opacity: 1; }
          100% { transform: translateY(120vh) rotate(360deg); opacity: 1; }
        }
      `}</style>
    </div>
  );
};

export default JoinSelectionSuccessPage;
