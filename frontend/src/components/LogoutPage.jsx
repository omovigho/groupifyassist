import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Layout from '@/components/dashboard/Layout';
import { api } from '@/lib/api';

const LogoutPage = () => {
  const navigate = useNavigate();
  useEffect(() => {
    const run = async () => {
      try {
        // Try backend logout if available
        await api.post('/user/logout');
      } catch {}
      try {
        localStorage.removeItem('access_token');
      } catch {}
      setTimeout(() => navigate('/login', { replace: true }), 600);
    };
    run();
  }, [navigate]);

  return (
    <Layout>
      <div className="max-w-md mx-auto mt-10 rounded-2xl bg-[#00BFA6] text-white shadow-sm p-6 text-center">
        <h1 className="text-lg font-semibold mb-2">Logging you out…</h1>
        <p className="text-sm opacity-90">Please wait while we securely sign you out.</p>
      </div>
    </Layout>
  );
};

export default LogoutPage;
