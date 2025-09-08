import { Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';

const Confetti = () => (
  <svg className="absolute inset-0 w-full h-full pointer-events-none" aria-hidden="true">
    <defs>
      <linearGradient id="g1" x1="0" x2="1">
        <stop offset="0%" stopColor="#60a5fa" />
        <stop offset="100%" stopColor="#22d3ee" />
      </linearGradient>
      <linearGradient id="g2" x1="0" x2="1">
        <stop offset="0%" stopColor="#a78bfa" />
        <stop offset="100%" stopColor="#60a5fa" />
      </linearGradient>
    </defs>
    {[...Array(60)].map((_, i) => (
      <rect key={i} x={Math.random()*100+'%'} y={-10} width={3} height={8} fill={i%2? 'url(#g1)':'url(#g2)'}
        style={{
          transformOrigin: 'center',
          animation: `fall ${4 + Math.random()*3}s linear ${Math.random()*2}s forwards, spin ${1+Math.random()*2}s linear infinite`
        }} />
    ))}
    <style>{`
      @keyframes fall { to { transform: translateY(120vh) rotate(360deg); opacity: 0.9; } }
      @keyframes spin { from { transform: rotate(0deg);} to { transform: rotate(360deg);} }
    `}</style>
  </svg>
);

const ChangePasswordSuccessPage = () => {
  return (
    <div className="min-h-screen dark-navy-bg relative overflow-hidden">
      <div className="pointer-events-none absolute inset-0">
        <div className="absolute w-[28rem] h-[28rem] -top-32 -left-32 rounded-full bg-blue-500/5 blur-3xl" />
        <div className="absolute w-[26rem] h-[26rem] bottom-0 -right-32 rounded-full bg-cyan-400/5 blur-3xl" />
      </div>
      <Confetti />

      <main className="relative z-10 px-6 pt-24 pb-24 flex items-center justify-center text-center">
        <div className="w-full max-w-2xl">
          <div className="glass-morphism rounded-2xl p-10 md:p-12">
            <div className="mx-auto mb-6 w-20 h-20 rounded-full bg-green-400/20 border border-green-400/30 flex items-center justify-center">
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" className="w-10 h-10 text-green-400">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4.5 12.75l6 6 9-13.5" />
              </svg>
            </div>
            <h1 className="text-4xl md:text-5xl font-extrabold tracking-tight text-white">Password changed</h1>
            <p className="mt-3 text-gray-300 max-w-xl mx-auto">Your password has been updated. You can now log in with your new password.</p>
            <div className="mt-8 flex items-center justify-center gap-3">
              <Link to="/login">
                <Button className="h-12 px-8 bg-white text-slate-900 hover:bg-gray-100 rounded-lg font-semibold">Go to Login</Button>
              </Link>
              <Link to="/">
                <Button variant="ghost" className="h-12 px-8 text-white/80 hover:text-white hover:bg-white/10 border border-white/15 rounded-lg">Back to Home</Button>
              </Link>
            </div>
          </div>
        </div>
      </main>

      <footer className="absolute bottom-5 left-0 right-0 text-center z-10">
        <p className="text-gray-500 text-xs md:text-sm">© 2025 GroupifyAssist. All rights reserved.</p>
      </footer>
    </div>
  );
};

export default ChangePasswordSuccessPage;
