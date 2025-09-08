import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { api } from '@/lib/api';

const SimpleLandingPage = () => {
  const [accessCode, setAccessCode] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleJoinGroup = async (e) => {
    e.preventDefault();
    if (accessCode.trim()) {
      setError('');
      setLoading(true);
      try {
        // Resolve the code to either group or selection and navigate accordingly
        const { data } = await api.post('/join/resolve', { code: accessCode.trim() });
        if (data.kind === 'group') {
          navigate(`/join?code=${encodeURIComponent(accessCode.trim())}`);
        } else if (data.kind === 'selection') {
          navigate(`/selection/join?code=${encodeURIComponent(accessCode.trim())}`);
        } else {
          setError('Unknown code type');
        }
      } catch (e) {
        const msg = e?.response?.data?.detail || e?.response?.data?.message || e.message || 'Invalid access code';
        setError(msg);
      } finally {
        setLoading(false);
      }
    }
  };

  return (
    <div className="min-h-screen dark-navy-bg relative overflow-hidden">
      {/* Subtle accents */}
      <div className="pointer-events-none absolute inset-0">
        <div className="absolute w-[32rem] h-[32rem] -top-40 -left-40 rounded-full bg-blue-500/5 blur-3xl" />
        <div className="absolute w-[30rem] h-[30rem] bottom-0 -right-40 rounded-full bg-cyan-400/5 blur-3xl" />
      </div>

      {/* Top-right navigation */}
      <nav className="absolute top-6 right-6 z-20 flex gap-3">
        <Link to="/login">
          <Button
            variant="ghost"
            className="text-white/80 hover:text-white hover:bg-white/10 border border-white/15 rounded-lg px-6 h-10"
          >
            Login
          </Button>
        </Link>
        <Link to="/signup">
          <Button
            className="bg-white text-slate-900 hover:bg-gray-100 rounded-lg px-6 h-10 font-medium shadow-sm"
          >
            Sign Up
          </Button>
        </Link>
      </nav>

      {/* Centered hero block */}
      <div className="absolute inset-0 flex items-center justify-center px-6 text-center z-10">
        <div className="w-full max-w-4xl">
          <div className="mb-8">
            <h1 className="font-bold leading-tight text-white tracking-tight text-[2.75rem] md:text-[4rem]">
              <span className="block">Welcome to</span>
              <span className="block">GroupifyAssist</span>
            </h1>
          </div>
          <p className="text-base md:text-xl text-gray-300 mb-10 max-w-2xl mx-auto">
            Effortless Grouping & Smart Selection, Anytime, Anywhere.
          </p>
          <form onSubmit={handleJoinGroup} className="max-w-2xl mx-auto mb-4">
            <div className="form flex flex-col sm:flex-row items-stretch sm:items-center justify-center gap-3">
              <Input
                type="text"
                placeholder="Enter Access Code..."
                value={accessCode}
                onChange={(e) => setAccessCode(e.target.value)}
                className="flex-1 h-14 bg-white/10 border-white/25 text-white placeholder:text-gray-400 rounded-lg focus:border-blue-300 focus:ring-2 focus:ring-blue-300/40 transition"
                maxLength={64}
                required
              />
              <Button
                type="submit"
                disabled={loading}
                className="h-14 px-8 bg-white text-slate-900 hover:bg-gray-100 disabled:opacity-60 rounded-lg font-semibold whitespace-nowrap"
              >
                {loading ? 'Checking…' : 'Join'}
              </Button>
            </div>
          </form>
          {error && (
            <p className="text-sm text-red-400 mt-2">{error}</p>
          )}
          <p className="text-sm text-gray-400">Have a code from an organizer? Paste it above and jump right in.</p>
        </div>
      </div>

      {/* Bottom-center footer */}
      <footer className="absolute bottom-5 left-0 right-0 text-center z-10">
        <p className="text-gray-500 text-xs md:text-sm">© 2025 GroupifyAssist. All rights reserved.</p>
      </footer>

      {/* Help button bottom-right */}
      <button
        type="button"
        className="help-btn help-pulse fixed bottom-6 right-6 z-30 bg-indigo-600 hover:bg-indigo-500 text-white rounded-full w-12 h-12 flex items-center justify-center shadow-lg shadow-indigo-900/40 focus:outline-none focus:ring-2 focus:ring-indigo-400/50"
        aria-label="Help"
      >
        ?
      </button>
    </div>
  );
};

export default SimpleLandingPage;
