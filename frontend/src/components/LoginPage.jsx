import { Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { useState } from 'react';
import { api } from '@/lib/api';
// Logo temporarily removed

const LoginPage = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const onSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    try {
  const { data } = await api.post('/user/login', { email, password });
  if (!data?.access_token) throw new Error('Invalid credentials');
      try { localStorage.setItem('access_token', data.access_token); } catch {}
      // Optionally store token (e.g., in memory or localStorage) for Authorization header usage
      // localStorage.setItem('access_token', data.access_token);
      setSuccess('Login successful');
      setTimeout(() => {
        setSuccess('');
        window.location.replace('/dashboard');
      }, 500);
    } catch (err) {
  const msg = err?.response?.data?.detail || 'Login failed. Please check your credentials.';
  setError(msg);
    }
  };

  return (
    <div className="min-h-screen dark-navy-bg relative overflow-hidden">
      <div className="pointer-events-none absolute inset-0">
        <div className="absolute w-[28rem] h-[28rem] -top-32 -left-32 rounded-full bg-blue-500/5 blur-3xl" />
        <div className="absolute w-[26rem] h-[26rem] bottom-0 -right-32 rounded-full bg-cyan-400/5 blur-3xl" />
      </div>

      <header className="relative z-10 px-6 pt-10 text-center">
  <div className="flex items-center justify-center mb-4" />
        <h1 className="text-4xl md:text-5xl font-extrabold tracking-tight text-white">Welcome back</h1>
        <p className="mt-3 text-gray-300 max-w-2xl mx-auto">Sign in to continue to GroupifyAssist.</p>
      </header>

      <main className="relative z-10 px-6 pb-24 mt-10 flex justify-center">
        <div className="w-full max-w-md">
          <div className="glass-morphism rounded-2xl p-6 md:p-8">
            <form onSubmit={onSubmit} className="space-y-5">
              {success && (
                <div className="rounded-lg border border-emerald-500/40 bg-emerald-500/10 text-emerald-200 px-4 py-3">
                  {success}
                </div>
              )}
              {error && (
                <div className="rounded-lg border border-red-500/40 bg-red-500/10 text-red-300 px-4 py-3">
                  {error}
                </div>
              )}
              <div>
                <label htmlFor="email" className="block text-sm font-medium text-gray-200 mb-2">Email</label>
                <Input id="email" type="email" value={email} onChange={(e)=>setEmail(e.target.value)} required className="h-12 bg-white/5 border-white/15 text-white placeholder:text-gray-400 rounded-lg input-focus-glow" />
              </div>
              <div>
                <label htmlFor="password" className="block text-sm font-medium text-gray-200 mb-2">Password</label>
                <Input id="password" type="password" value={password} onChange={(e)=>setPassword(e.target.value)} required className="h-12 bg-white/5 border-white/15 text-white placeholder:text-gray-400 rounded-lg input-focus-glow" />
              </div>
              <Button type="submit" className="w-full h-12 bg-white text-slate-900 hover:bg-gray-100 rounded-lg font-semibold button-hover-glow">Login</Button>
              <div className="flex items-center justify-between text-sm text-gray-400">
                <div>
                  New here? <Link to="/signup" className="text-blue-400 hover:text-blue-300 underline underline-offset-4">Create an account</Link>
                </div>
                <Link to="/forgot-password" className="text-blue-400 hover:text-blue-300 underline underline-offset-4">Forgot password?</Link>
              </div>
            </form>
          </div>
        </div>
      </main>

      <footer className="absolute bottom-5 left-0 right-0 text-center z-10">
        <p className="text-gray-500 text-xs md:text-sm">© 2025 GroupifyAssist. All rights reserved.</p>
      </footer>
    </div>
  );
};

export default LoginPage;
