import { useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';

const ChangePasswordPage = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const email = location?.state?.email;

  const [password, setPassword] = useState('');
  const [confirm, setConfirm] = useState('');
  const [error, setError] = useState('');
  const [submitting, setSubmitting] = useState(false);

  const onSubmit = async (e) => {
    e.preventDefault();
    setError('');
    if (password.length < 8) {
      setError('Password must be at least 8 characters.');
      return;
    }
    if (password !== confirm) {
      setError('Passwords do not match.');
      return;
    }
    try {
      setSubmitting(true);
      // TODO: integrate with backend to set new password (token/email from state or query)
      await new Promise((res) => setTimeout(res, 700));
      navigate('/change-password-success');
    } catch (err) {
      setError(err?.message || 'Could not change password, please try again.');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen dark-navy-bg relative overflow-hidden">
      <div className="pointer-events-none absolute inset-0">
        <div className="absolute w-[28rem] h-[28rem] -top-32 -left-32 rounded-full bg-blue-500/5 blur-3xl" />
        <div className="absolute w-[26rem] h-[26rem] bottom-0 -right-32 rounded-full bg-cyan-400/5 blur-3xl" />
      </div>

      <header className="relative z-10 px-6 pt-10 text-center">
        <h1 className="text-4xl md:text-5xl font-extrabold tracking-tight text-white">Create new password</h1>
        <p className="mt-3 text-gray-300 max-w-2xl mx-auto">Enter and confirm your new password to continue.</p>
      </header>

      <main className="relative z-10 px-6 pb-24 mt-10 flex justify-center">
        <div className="w-full max-w-md">
          <div className="glass-morphism rounded-2xl p-6 md:p-8">
            <form onSubmit={onSubmit} className="space-y-5">
              {/* Error placeholder from backend */}
              {error && (
                <div className="rounded-lg border border-red-500/40 bg-red-500/10 text-red-300 px-4 py-3">{error}</div>
              )}

              <div>
                <label htmlFor="password" className="block text-sm font-medium text-gray-200 mb-2">New password</label>
                <Input
                  id="password"
                  type="password"
                  value={password}
                  onChange={(e)=>setPassword(e.target.value)}
                  required
                  className="h-12 bg-white/5 border-white/15 text-white placeholder:text-gray-400 rounded-lg input-focus-glow"
                />
                <p className="mt-1 text-xs text-gray-400">Minimum 8 characters.</p>
              </div>

              <div>
                <label htmlFor="confirm" className="block text-sm font-medium text-gray-200 mb-2">Confirm password</label>
                <Input
                  id="confirm"
                  type="password"
                  value={confirm}
                  onChange={(e)=>setConfirm(e.target.value)}
                  required
                  className="h-12 bg-white/5 border-white/15 text-white placeholder:text-gray-400 rounded-lg input-focus-glow"
                />
                {confirm && password !== confirm && (
                  <p className="mt-1 text-xs text-red-300">Passwords do not match.</p>
                )}
              </div>

              <Button disabled={submitting} type="submit" className="w-full h-12 bg-white text-slate-900 hover:bg-gray-100 disabled:opacity-60 rounded-lg font-semibold button-hover-glow">
                {submitting ? 'Creating...' : 'Create password'}
              </Button>
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

export default ChangePasswordPage;
