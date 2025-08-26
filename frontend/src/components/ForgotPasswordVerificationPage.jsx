import { useEffect, useMemo, useRef, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { api } from '@/lib/api';

const OTP_LENGTH = 6;

const ForgotPasswordVerificationPage = () => {
  const navigate = useNavigate();
  const [maskedEmail, setMaskedEmail] = useState('');
  const [otp, setOtp] = useState(Array(OTP_LENGTH).fill(''));
  const [error, setError] = useState('');
  const [secondsLeft, setSecondsLeft] = useState(180);
  const inputRefs = useRef([]);
  useEffect(() => {
    let mounted = true;
    (async () => {
      try {
        const { data } = await api.get('/user/verification/session');
        if (!mounted) return;
        setMaskedEmail(data?.email_masked || '');
      } catch (e) {
        setError('Session expired. Please restart.');
      }
    })();
    return () => { mounted = false; };
  }, []);

  useEffect(() => {
    if (secondsLeft <= 0) return;
    const id = setInterval(() => setSecondsLeft((s) => s - 1), 1000);
    return () => clearInterval(id);
  }, [secondsLeft]);

  const formattedTime = useMemo(() => {
    const m = Math.floor(secondsLeft / 60).toString().padStart(1, '0');
    const s = (secondsLeft % 60).toString().padStart(2, '0');
    return `${m}:${s}`;
  }, [secondsLeft]);

  const handleChange = (idx, val) => {
    if (val === '' || /^[0-9]$/.test(val)) {
      const next = [...otp];
      next[idx] = val;
      setOtp(next);
      setError('');
      if (val && idx < OTP_LENGTH - 1) inputRefs.current[idx + 1]?.focus();
    }
  };

  const handleKeyDown = (idx, e) => {
    if (e.key === 'Backspace' && !otp[idx] && idx > 0) inputRefs.current[idx - 1]?.focus();
    if (e.key === 'ArrowLeft' && idx > 0) inputRefs.current[idx - 1]?.focus();
    if (e.key === 'ArrowRight' && idx < OTP_LENGTH - 1) inputRefs.current[idx + 1]?.focus();
  };

  const handlePaste = (e) => {
    e.preventDefault();
    const text = (e.clipboardData.getData('text') || '').replace(/\D/g, '').slice(0, OTP_LENGTH);
    if (!text) return;
    const next = Array(OTP_LENGTH).fill('');
    for (let i = 0; i < text.length; i++) next[i] = text[i];
    setOtp(next);
    const last = Math.min(text.length, OTP_LENGTH) - 1;
    inputRefs.current[last]?.focus();
  };

  const code = otp.join('');

  const onSubmit = async (e) => {
    e.preventDefault();
    setError('');
    if (code.length !== OTP_LENGTH) {
      setError('Please enter the 6-digit code.');
      return;
    }
    try {
      await api.post('/user/forgot-password/verify', { code });
      navigate('/change-password');
    } catch (err) {
      const msg = err?.response?.data?.detail || 'Verification failed. Please try again.';
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
        <h1 className="text-4xl md:text-5xl font-extrabold tracking-tight text-white">Verify your email</h1>
        <p className="mt-3 text-gray-300 max-w-2xl mx-auto">
          A 6-digit code has been sent to your email. Enter the code below.{' '}
          <span className="font-semibold text-white">Code expires in <span className="tabular-nums">{formattedTime}</span>.</span>
        </p>
      </header>

      <main className="relative z-10 px-6 pb-24 mt-10 flex justify-center">
        <div className="w-full max-w-xl">
          <div className="glass-morphism rounded-2xl p-6 md:p-8">
            <form onSubmit={onSubmit} className="space-y-6">
              {error && (
                <div className="rounded-lg border border-red-500/40 bg-red-500/10 text-red-300 px-4 py-3">
                  {error}
                </div>
              )}

              {maskedEmail && (
                <div className="text-sm text-gray-300">Verifying: <span className="font-medium text-white">{maskedEmail}</span></div>
              )}

              <div>
                <label className="block text-sm font-medium text-gray-200 mb-3">Verification code</label>
                <div className="flex items-center gap-2" onPaste={handlePaste}>
                  {otp.map((val, idx) => (
                    <input
                      key={idx}
                      ref={(el) => (inputRefs.current[idx] = el)}
                      type="text"
                      inputMode="numeric"
                      maxLength={1}
                      value={val}
                      onChange={(e) => handleChange(idx, e.target.value.replace(/\D/g, ''))}
                      onKeyDown={(e) => handleKeyDown(idx, e)}
                      className="w-12 h-12 text-center text-lg rounded-md bg-white/5 border border-white/15 text-white input-focus-glow"
                      aria-label={`Digit ${idx + 1}`}
                    />
                  ))}
                </div>
                <p className="mt-2 text-xs text-gray-400">Didn’t get the code? <button type="button" className="text-blue-400 hover:text-blue-300 underline underline-offset-4" onClick={async ()=>{
                  try { await api.post('/user/forgot-password/resend'); setSecondsLeft(180);} catch(e){ setError(e?.response?.data?.detail || 'Could not resend.');}
                }}>Resend</button></p>
              </div>

              <Button type="submit" className="w-full h-12 bg-white text-slate-900 hover:bg-gray-100 rounded-lg font-semibold button-hover-glow">
                Verify Email
              </Button>

              <div className="text-center text-sm text-gray-400">
                Entered the wrong email? <Link to="/forgot-password" className="text-blue-400 hover:text-blue-300 underline underline-offset-4">Go back</Link>
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

export default ForgotPasswordVerificationPage;
