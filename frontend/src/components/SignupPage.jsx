import { useEffect, useMemo, useRef, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { api } from '@/lib/api';

// Simple utility to debounce rapid calls
function useDebouncedValue(value, delay = 150) {
  const [debounced, setDebounced] = useState(value);
  useEffect(() => {
    const id = setTimeout(() => setDebounced(value), delay);
    return () => clearTimeout(id);
  }, [value, delay]);
  return debounced;
}

const SignupPage = () => {
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  // Countries
  const [countries, setCountries] = useState([]); // {name: string, cca2: string}
  const [countryQuery, setCountryQuery] = useState('');
  const debouncedQuery = useDebouncedValue(countryQuery, 80);
  const [countryOpen, setCountryOpen] = useState(false);
  const [selectedCountry, setSelectedCountry] = useState(null);
  const dropdownRef = useRef(null);
  const inputRef = useRef(null);

  // Fetch countries on mount
  useEffect(() => {
    let active = true;
    const load = async () => {
      try {
        const res = await fetch('https://restcountries.com/v3.1/all?fields=name,cca2');
        const data = await res.json();
        if (!active) return;
        // Map and sort by name.common
        const mapped = (data || [])
          .map((c) => ({ name: c?.name?.common || '', cca2: (c?.cca2 || '').toUpperCase() }))
          .filter((c) => c.name && c.cca2)
          .sort((a, b) => a.name.localeCompare(b.name));
        setCountries(mapped);
      } catch (e) {
        console.error('Failed to load countries', e);
      }
    };
    load();
    return () => { active = false; };
  }, []);

  // Filter countries by query on name or cca2
  const filtered = useMemo(() => {
    const q = debouncedQuery.trim().toLowerCase();
    if (!q) return countries;
    return countries.filter((c) => c.name.toLowerCase().includes(q) || c.cca2.toLowerCase().includes(q));
  }, [countries, debouncedQuery]);

  // Close dropdown on outside click
  useEffect(() => {
    const onClick = (e) => {
      if (!dropdownRef.current) return;
      if (!dropdownRef.current.contains(e.target)) {
        setCountryOpen(false);
      }
    };
    document.addEventListener('mousedown', onClick);
    return () => document.removeEventListener('mousedown', onClick);
  }, []);

  const handleSelectCountry = (c) => {
    setSelectedCountry(c);
    setCountryQuery(c.name);
    setCountryOpen(false);
  };

  const onSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    // Basic client-side validation
    if (!selectedCountry) {
      setError('Please select your country.');
      return;
    }
    if (password !== confirmPassword) {
      setError('Passwords do not match.');
      return;
    }
    try {
      setLoading(true);
      await api.post('/user/sign-up', {
        email,
        password,
        confirm_password: confirmPassword,
        country: selectedCountry?.name,
      });
      navigate('/verify-email');
    } catch (err) {
      const msg = err?.response?.data?.detail || 'Signup failed. Please try again.';
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen dark-navy-bg relative overflow-hidden">
      {/* Background accents */}
      <div className="pointer-events-none absolute inset-0">
        <div className="absolute w-[28rem] h-[28rem] -top-32 -left-32 rounded-full bg-blue-500/5 blur-3xl" />
        <div className="absolute w-[26rem] h-[26rem] bottom-0 -right-32 rounded-full bg-cyan-400/5 blur-3xl" />
      </div>

      {/* Header */}
      <header className="relative z-10 px-6 pt-10 text-center">
        <h1 className="text-4xl md:text-5xl font-extrabold tracking-tight text-white">
          Create your GroupifyAssist account
        </h1>
        <p className="mt-3 text-gray-300 max-w-2xl mx-auto">
          Join a modern platform for effortless grouping and smart selections. Quick setup, secure access, and a smooth experience.
        </p>
      </header>

      {/* Form Card */}
      <main className="relative z-10 px-6 pb-24 mt-10 flex justify-center">
        <div className="w-full max-w-xl">
          <div className="glass-morphism rounded-2xl p-6 md:p-8">
            <form onSubmit={onSubmit} className="space-y-5">
              {error && (
                <div className="rounded-lg border border-red-500/30 bg-red-500/10 text-red-200 px-4 py-3 text-sm">
                  {error}
                </div>
              )}
              {/* Email */}
              <div>
                <label htmlFor="email" className="block text-sm font-medium text-gray-200 mb-2">Email</label>
                <Input
                  id="email"
                  type="email"
                  autoComplete="email"
                  placeholder="you@example.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                  className="h-12 bg-white/5 border-white/15 text-white placeholder:text-gray-400 rounded-lg input-focus-glow"
                />
              </div>

              {/* Country combobox */}
              <div ref={dropdownRef}>
                <label htmlFor="country" className="block text-sm font-medium text-gray-200 mb-2">Country</label>
                <div className="relative">
                  <Input
                    id="country"
                    ref={inputRef}
                    type="text"
                    role="combobox"
                    aria-expanded={countryOpen}
                    placeholder="Search country by name or CCA2 (e.g., NG, US)"
                    value={countryQuery}
                    onChange={(e) => {
                      setCountryQuery(e.target.value);
                      setCountryOpen(true);
                    }}
                    onFocus={() => setCountryOpen(true)}
                    className="h-12 bg-white/5 border-white/15 text-white placeholder:text-gray-400 rounded-lg pr-10 input-focus-glow"
                  />
                  <button
                    type="button"
                    aria-label="Toggle country list"
                    onClick={() => setCountryOpen((v) => !v)}
                    className="absolute inset-y-0 right-2 my-auto h-8 w-8 rounded-md text-gray-300 hover:text-white hover:bg-white/10 flex items-center justify-center"
                  >
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" className={`h-5 w-5 transition-transform ${countryOpen ? 'rotate-180' : ''}`}>
                      <path fillRule="evenodd" d="M5.23 7.21a.75.75 0 011.06.02L10 10.94l3.71-3.71a.75.75 0 111.06 1.06l-4.24 4.24a.75.75 0 01-1.06 0L5.21 8.29a.75.75 0 01.02-1.08z" clipRule="evenodd" />
                    </svg>
                  </button>

                  {countryOpen && (
                    <div className="absolute z-20 mt-2 w-full max-h-64 overflow-auto rounded-lg border border-white/10 bg-slate-900/95 shadow-xl backdrop-blur-sm">
                      {filtered.length === 0 ? (
                        <div className="px-4 py-3 text-sm text-gray-400">No matches</div>
                      ) : (
                        <ul className="py-1">
                          {filtered.map((c) => (
                            <li key={c.cca2}>
                              <button
                                type="button"
                                onClick={() => handleSelectCountry(c)}
                                className={`w-full text-left px-4 py-2 text-sm flex items-center justify-between hover:bg-white/10 ${selectedCountry?.cca2 === c.cca2 ? 'bg-white/10' : ''}`}
                              >
                                <span className="text-white">{c.name}</span>
                                <span className="ml-3 text-xs text-gray-400">{c.cca2}</span>
                              </button>
                            </li>
                          ))}
                        </ul>
                      )}
                    </div>
                  )}
                </div>
                {selectedCountry && (
                  <p className="mt-2 text-xs text-gray-400">Selected: {selectedCountry.name} ({selectedCountry.cca2})</p>
                )}
              </div>

              {/* Password */}
              <div>
                <label htmlFor="password" className="block text-sm font-medium text-gray-200 mb-2">Password</label>
                <Input
                  id="password"
                  type="password"
                  autoComplete="new-password"
                  placeholder="••••••••"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  minLength={6}
                  className="h-12 bg-white/5 border-white/15 text-white placeholder:text-gray-400 rounded-lg input-focus-glow"
                />
              </div>

              {/* Confirm Password */}
              <div>
                <label htmlFor="confirm" className="block text-sm font-medium text-gray-200 mb-2">Confirm Password</label>
                <Input
                  id="confirm"
                  type="password"
                  autoComplete="new-password"
                  placeholder="••••••••"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  required
                  minLength={6}
                  className="h-12 bg-white/5 border-white/15 text-white placeholder:text-gray-400 rounded-lg input-focus-glow"
                />
              </div>

              <Button
                type="submit"
                className="w-full h-12 bg-white text-slate-900 hover:bg-gray-100 rounded-lg font-semibold button-hover-glow"
                disabled={loading}
              >
                {loading ? 'Creating…' : 'Create Account'}
              </Button>

              <div className="text-center text-sm text-gray-400">
                Already have an account?{' '}
                <Link to="/login" className="text-blue-400 hover:text-blue-300 underline underline-offset-4">Login</Link>
              </div>
            </form>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="absolute bottom-5 left-0 right-0 text-center z-10">
        <p className="text-gray-500 text-xs md:text-sm">© 2025 GroupifyAssist. All rights reserved.</p>
      </footer>
    </div>
  );
};

export default SignupPage;
