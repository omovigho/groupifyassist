import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
// eslint-disable-next-line no-unused-vars
import { motion, AnimatePresence } from 'framer-motion';
import { Users, Menu, X, LogIn, UserPlus } from 'lucide-react';

// Landing page focused on a modern hero with animated blended background
const LandingPage = () => {
  // UI state
  const [menuOpen, setMenuOpen] = useState(false);
  const [accessCode, setAccessCode] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!accessCode.trim()) return;
    setSubmitting(true);
    // Simulate join and navigate
    setTimeout(() => navigate('/dashboard'), 1000);
  };

  return (
    <div className="relative min-h-screen text-gray-900">
      {/* Embedded minimal custom CSS for background, animated gradient blobs, wave & motion effects */}
      <style>{`/* === BACKGROUND LAYERS === */
      .ga-hero-bg { position: fixed; inset: 0; overflow:hidden; background: radial-gradient(900px 560px at 50% 42%, rgba(248,250,252,0.85), rgba(241,245,249,0.35) 40%, rgba(15,23,42,0.9) 70%); }
      /* Optional subtle texture / hero reference image (swap or remove) */
      .ga-hero-bg::before { content:''; position:absolute; inset:0; background-image:linear-gradient(rgba(255,255,255,0.05),rgba(255,255,255,0.05)),url('/visual-ref.png'); background-size:cover; background-position:center; mix-blend-mode:overlay; opacity:.9; pointer-events:none; }
      /* Animated soft gradient glows */
      .ga-hero-bg::after { content:''; position:absolute; inset:-25%; background:linear-gradient(120deg, rgba(15,23,42,.65), rgba(2,132,199,.28), rgba(124,58,237,.3), rgba(15,23,42,.65)); background-size:220% 220%; filter:blur(50px); animation:gaGradientMove 20s ease-in-out infinite; pointer-events:none; }
      @keyframes gaGradientMove { 0%,100%{background-position:0% 50%;} 50%{background-position:100% 50%;} }

      /* === FLOATING PARTICLES === */
      .ga-particle { position:absolute; border-radius:9999px; filter:blur(8px); opacity:.33; will-change:transform; }
      .ga-float-1 { animation:gaFloat 16s ease-in-out infinite; }
      .ga-float-2 { animation:gaFloat 22s ease-in-out infinite; }
      .ga-float-3 { animation:gaFloat 28s ease-in-out infinite; }
      @keyframes gaFloat { 0%,100%{ transform:translate3d(0,0,0);} 50%{ transform:translate3d(22px,-28px,0);} }

      /* === WAVE (bottom decorative, sits behind footer) === */
      .ga-wave-wrap { position:fixed; bottom:0; left:0; width:100%; pointer-events:none; }
      .ga-wave path { animation:gaWaveShift 14s linear infinite; }
      @keyframes gaWaveShift { 0%{ d:path('M0 120 Q 180 90 360 115 T 720 110 T 1080 125 T 1440 118 V240 H0 Z'); } 50%{ d:path('M0 120 Q 180 140 360 115 T 720 130 T 1080 100 T 1440 125 V240 H0 Z'); } 100%{ d:path('M0 120 Q 180 90 360 115 T 720 110 T 1080 125 T 1440 118 V240 H0 Z'); } }
      /* Fallback for browsers without animated path (keeps still wave) */
      @supports not (d:path('M0 0')) { .ga-wave path { animation:none; } }

      /* === PAGE FADE-IN === */
      .ga-fade-in { animation:gaFade .7s ease forwards; opacity:0; }
      @keyframes gaFade { to { opacity:1; } }

      /* === FORM / BUTTON ENHANCEMENTS === */
      .ga-access-input { box-shadow:0 0 0 0 rgba(59,130,246,0.4); transition: box-shadow .35s, border-color .3s, background-color .3s, transform .3s; }
      .ga-access-input:focus { box-shadow:0 0 0 4px rgba(59,130,246,0.25), 0 0 0 1px rgba(59,130,246,0.6); }
      .ga-btn-gradient { background-image:linear-gradient(to right,var(--tw-gradient-stops)); transition: background-position .6s ease, transform .3s ease; background-size:200% 100%; background-position:0% 50%; }
      .ga-btn-gradient:hover { background-position:100% 50%; }
      .ga-btn-gradient:active { transform:translateY(2px) scale(.98); }

      /* Skip link accessibility */
      .ga-skip-link { position:absolute; left:1rem; top:-3rem; background:#fff; color:#111827; padding:.75rem 1.25rem; border-radius:.75rem; font-weight:600; box-shadow:0 4px 18px -2px rgba(0,0,0,.15); transition:top .3s; z-index:50; }
      .ga-skip-link:focus { top:1rem; outline:2px solid #3b82f6; }

      /* Respect reduced motion */
      @media (prefers-reduced-motion: reduce) { .ga-float-1, .ga-float-2, .ga-float-3, .ga-hero-bg::after, .ga-wave path, .ga-fade-in { animation:none!important; } }
      `}</style>

      {/* Background & motion layers */}
      <div aria-hidden className="ga-hero-bg" />
      <div aria-hidden className="pointer-events-none fixed inset-0 overflow-hidden">
        <span className="ga-particle ga-float-1 w-24 h-24 bg-cyan-400/25 left-12 top-24" />
        <span className="ga-particle ga-float-2 w-16 h-16 bg-indigo-400/30 right-16 top-40" />
        <span className="ga-particle ga-float-3 w-20 h-20 bg-blue-500/25 left-1/3 bottom-24" />
      </div>
      {/* Animated wave decorative background */}
      <div aria-hidden className="ga-wave-wrap">
        <svg className="ga-wave w-full h-40 opacity-50 mix-blend-overlay" viewBox="0 0 1440 240" fill="none" preserveAspectRatio="none">
          <defs>
            <linearGradient id="gaWaveGradient" x1="0" x2="1440" y1="0" y2="0" gradientUnits="userSpaceOnUse">
              <stop stopColor="#3b82f6" stopOpacity="0.35" />
              <stop offset="0.5" stopColor="#6366f1" stopOpacity="0.35" />
              <stop offset="1" stopColor="#0ea5e9" stopOpacity="0.35" />
            </linearGradient>
          </defs>
          <path d="M0 120 Q 180 90 360 115 T 720 110 T 1080 125 T 1440 118 V240 H0 Z" fill="url(#gaWaveGradient)" />
        </svg>
      </div>

      {/* Skip link for keyboard users */}
      <a href="#main-content" className="ga-skip-link">Skip to main content</a>

      {/* Page container: centers content, footer sticks to bottom */}
      <div className="relative z-10 flex min-h-screen flex-col">
        {/* Header */}
  <header className="px-4 sm:px-6 lg:px-8 py-4" role="banner">
          <nav className="mx-auto max-w-7xl flex items-center justify-between" aria-label="Global">
            {/* Logo */}
            <Link to="/" className="inline-flex items-center gap-2 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 rounded-lg">
              <span className="inline-flex items-center justify-center rounded-xl bg-blue-600 p-2 shadow-sm">
                <Users className="h-5 w-5 text-white" aria-hidden />
              </span>
              <span className="text-lg font-semibold tracking-tight bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">GroupifyAssist</span>
            </Link>

            {/* Desktop actions */}
      <div className="hidden md:flex items-center gap-3">
              <Link
                to="/login"
        className="inline-flex items-center gap-2 rounded-full px-4 py-2 text-sm font-semibold text-gray-800 bg-white/70 backdrop-blur border border-white/60 shadow hover:bg-white focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500/70 focus-visible:ring-offset-2 focus-visible:ring-offset-white transition"
              >
                <LogIn className="h-4 w-4" aria-hidden />
                Login
              </Link>
              <Link
                to="/signup"
        className="ga-btn-gradient inline-flex items-center gap-2 rounded-full px-5 py-2 text-sm font-semibold text-white bg-gradient-to-r from-blue-600 via-indigo-600 to-sky-500 shadow hover:shadow-lg focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500/70 focus-visible:ring-offset-2 focus-visible:ring-offset-white transition"
              >
                <UserPlus className="h-4 w-4" aria-hidden />
                Sign Up
              </Link>
            </div>

            {/* Mobile menu toggle */}
            <button
              type="button"
              aria-label="Open menu"
              className="md:hidden inline-flex items-center justify-center rounded-lg p-2 text-gray-700 bg-white/70 backdrop-blur border border-white/60 shadow hover:bg-white focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 transition"
              onClick={() => setMenuOpen(true)}
            >
              <Menu className="h-5 w-5" />
            </button>
          </nav>

          {/* Mobile sheet */}
          <AnimatePresence>
            {menuOpen && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="fixed inset-0 z-50 bg-black/30 backdrop-blur-sm md:hidden"
                onClick={() => setMenuOpen(false)}
                aria-hidden
              />
            )}
          </AnimatePresence>
          <AnimatePresence>
            {menuOpen && (
              <motion.div
                initial={{ x: '100%' }}
                animate={{ x: 0 }}
                exit={{ x: '100%' }}
                transition={{ type: 'spring', stiffness: 320, damping: 30 }}
                className="fixed right-0 top-0 z-50 h-full w-80 max-w-[85%] bg-white shadow-xl md:hidden"
                role="dialog"
                aria-modal="true"
              >
                <div className="flex items-center justify-between p-4 border-b">
                  <div className="inline-flex items-center gap-2">
                    <span className="inline-flex items-center justify-center rounded-xl bg-blue-600 p-2">
                      <Users className="h-5 w-5 text-white" aria-hidden />
                    </span>
                    <span className="text-base font-semibold">GroupifyAssist</span>
                  </div>
                  <button
                    type="button"
                    aria-label="Close menu"
                    className="inline-flex items-center justify-center rounded-lg p-2 text-gray-700 hover:bg-gray-100 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500"
                    onClick={() => setMenuOpen(false)}
                  >
                    <X className="h-5 w-5" />
                  </button>
                </div>
                <div className="p-4 flex flex-col gap-3">
                  <Link
                    to="/login"
                    className="inline-flex items-center gap-2 rounded-lg px-4 py-3 text-sm font-semibold text-gray-800 bg-gray-50 hover:bg-gray-100 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500"
                    onClick={() => setMenuOpen(false)}
                  >
                    <LogIn className="h-4 w-4" /> Login
                  </Link>
                  <Link
                    to="/signup"
                    className="inline-flex items-center gap-2 rounded-lg px-4 py-3 text-sm font-semibold text-white bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500"
                    onClick={() => setMenuOpen(false)}
                  >
                    <UserPlus className="h-4 w-4" /> Sign Up
                  </Link>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </header>

        {/* Main hero - centered content */}
        <main id="main-content" className="flex-1 grid place-items-center px-4 sm:px-6 lg:px-8" role="main">
          <section className="ga-fade-in w-full">
            <div className="mx-auto max-w-3xl text-center">
              {/* Hero heading with motion */}
              <motion.h1
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.7, ease: 'easeOut' }}
                className="text-4xl sm:text-5xl md:text-6xl font-extrabold tracking-tight"
              >
                Welcome to <span className="bg-gradient-to-r from-blue-600 via-indigo-600 to-sky-500 bg-clip-text text-transparent">GroupifyAssist</span>
              </motion.h1>
              <motion.p
                initial={{ opacity: 0, y: 14 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.1, duration: 0.7 }}
                className="mt-4 text-lg sm:text-xl text-gray-600 max-w-2xl mx-auto"
              >
                Effortless Grouping & Smart Selection, Anytime, Anywhere.
              </motion.p>

              {/* Access Code form */}
              <motion.form
                onSubmit={handleSubmit}
                initial={{ opacity: 0, y: 16 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.25, duration: 0.7 }}
                className="mt-9 mx-auto flex w-full max-w-xl flex-col items-stretch gap-3 sm:flex-row sm:items-center"
                aria-labelledby="access-code-label"
              >
                <label id="access-code-label" htmlFor="access-code" className="sr-only">Access Code</label>
                <input
                  id="access-code"
                  type="text"
                  inputMode="text"
                  placeholder="Enter Access Code..."
                  value={accessCode}
                  onChange={(e) => setAccessCode(e.target.value)}
                  className="ga-access-input flex-1 rounded-full border-2 border-white/60 bg-white/80 backdrop-blur px-5 py-3 text-base text-gray-900 placeholder:text-gray-500 shadow focus:border-blue-500 focus:ring-2 focus:ring-blue-500/30 outline-none"
                  aria-label="Enter Access Code"
                  autoComplete="off"
                  maxLength={64}
                />
                <button
                  type="submit"
                  disabled={!accessCode.trim() || submitting}
                  className="ga-btn-gradient inline-flex justify-center items-center rounded-full px-7 py-3 font-semibold text-white bg-gradient-to-r from-blue-600 via-indigo-600 to-sky-500 shadow hover:shadow-blue-500/30 hover:scale-[1.03] disabled:opacity-60 disabled:cursor-not-allowed focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500/70 focus-visible:ring-offset-2 focus-visible:ring-offset-white transition"
                  aria-live="polite"
                >
                  {submitting ? 'Joining…' : 'Join Group'}
                </button>
              </motion.form>
              {/* Helper text */}
              <motion.p
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.5, duration: 0.7 }}
                className="mt-3 text-sm text-gray-500"
              >
                Have a code from an organizer? Paste it above and jump right in.
              </motion.p>
            </div>
          </section>
        </main>

        {/* Footer (sticks to bottom via flex layout) */}
        <footer className="mt-auto px-4 sm:px-6 lg:px-8 py-6 relative" role="contentinfo">
          <div className="mx-auto max-w-7xl text-center text-sm text-gray-600 backdrop-blur-sm/10">
            © 2025 GroupifyAssist. All rights reserved.
          </div>
        </footer>
      </div>
    </div>
  );
};

export default LandingPage;
