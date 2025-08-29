import { useEffect, useMemo, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { api } from '@/lib/api';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';

// Helper to read query string
const useQuery = () => new URLSearchParams(useLocation().search);

const JoinGroupPage = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const query = useQuery();
  const initialCode = query.get('code') || '';

  const [code, setCode] = useState(initialCode);
  const [loading, setLoading] = useState(false);
  const [fetching, setFetching] = useState(false);
  const [error, setError] = useState('');
  const [groupMeta, setGroupMeta] = useState(null); // { name, description, fields, identifier }
  const [memberData, setMemberData] = useState({});
  const [memberIdentifier, setMemberIdentifier] = useState('');

  const canSubmit = useMemo(() => {
    if (!groupMeta) return false;
    if (!code.trim()) return false;
    // Ensure all dynamic fields are filled
    const fieldsOk = (groupMeta.fields || []).every((f) => (memberData[f] || '').toString().trim().length > 0);
    const idOk = memberIdentifier.toString().trim().length > 0;
    return fieldsOk && idOk;
  }, [groupMeta, memberData, memberIdentifier, code]);

  // Fetch group fields when code changes (debounced on explicit action)
  const fetchFields = async (joinCode) => {
    if (!joinCode) return;
    setError('');
    setFetching(true);
    try {
      // Direct backend uses /api proxy; endpoint described as /api/groups/fields?code=...
      const res = await api.get(`/groups/fields`, { params: { code: joinCode } });
      setGroupMeta(res.data);
      // Initialize memberData keys to empty strings for controlled inputs
      const init = {};
      (res.data.fields || []).forEach((k) => (init[k] = ''));
      setMemberData(init);
      setMemberIdentifier('');
    } catch (e) {
      const msg = e?.response?.data?.detail || e?.response?.data?.message || e.message || 'Failed to fetch group details';
      setError(msg);
      setGroupMeta(null);
    } finally {
      setFetching(false);
    }
  };

  // Auto-fetch if code provided in URL
  useEffect(() => {
    if (initialCode) {
      fetchFields(initialCode);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const handleCheckCode = async (e) => {
    e.preventDefault();
    await fetchFields(code.trim());
    // Update URL for shareability
    const sp = new URLSearchParams(location.search);
    if (code.trim()) sp.set('code', code.trim()); else sp.delete('code');
    navigate({ pathname: '/join', search: sp.toString() ? `?${sp.toString()}` : '' }, { replace: true });
  };

  const handleChangeField = (key, value) => {
    setMemberData((prev) => ({ ...prev, [key]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!canSubmit) return;
    setLoading(true);
    setError('');
    try {
      const payload = {
        code: code.trim(),
        member_data: memberData,
        member_identifier: memberIdentifier.trim(),
      };
      const res = await api.post('/groups/join', payload);
      // On success navigate to success page with state
      navigate('/join/success', { state: res.data, replace: true });
    } catch (e) {
      const msg = e?.response?.data?.detail || e?.response?.data?.message || e.message || 'Failed to join group';
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen dark-navy-bg relative overflow-hidden">
      {/* Background accents */}
      <div className="pointer-events-none absolute inset-0">
        <div className="absolute w-[40rem] h-[40rem] -top-48 -left-48 rounded-full bg-blue-500/5 blur-3xl" />
        <div className="absolute w-[36rem] h-[36rem] bottom-0 -right-48 rounded-full bg-cyan-400/5 blur-3xl" />
      </div>

      <div className="relative z-10 max-w-3xl mx-auto px-6 py-12">
        <div className="mb-8 text-center">
          <h1 className="text-3xl md:text-4xl font-bold gradient-text">Join a Group</h1>
          <p className="text-gray-400 mt-2">Enter your access code to load the required details.</p>
        </div>

        {/* Access Code Card */}
        <div className="glass-morphism rounded-2xl p-6 md:p-8 mb-6">
          <form onSubmit={handleCheckCode} className="grid grid-cols-1 md:grid-cols-[1fr_auto] gap-3 items-end">
            <div>
              <label className="block text-sm text-gray-300 mb-2">Access Code</label>
              <Input
                value={code}
                onChange={(e) => setCode(e.target.value)}
                placeholder="Enter access code"
                className="h-12 bg-white/10 border-white/20 text-white placeholder:text-gray-400 input-focus-glow"
                maxLength={64}
                required
              />
            </div>
            <Button type="submit" className="h-12 px-6 button-hover-glow bg-white text-slate-900 rounded-lg font-semibold">
              {fetching ? 'Checking…' : 'Check Code'}
            </Button>
          </form>
          {error && (
            <div className="mt-3 text-red-400 text-sm">{error}</div>
          )}
        </div>

        {/* Group Details and Dynamic Fields */}
        {groupMeta && (
          <div className="glass-morphism rounded-2xl p-6 md:p-8 animate-[fadeIn_0.4s_ease]">
            <div className="mb-6">
              <h2 className="text-2xl font-semibold">{groupMeta.name}</h2>
              {groupMeta.description && (
                <p className="text-gray-300 mt-1">{groupMeta.description}</p>
              )}
            </div>
            <form onSubmit={handleSubmit} className="space-y-5">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {(groupMeta.fields || []).map((field) => (
                  <div key={field} className="">
                    <label className="block text-sm text-gray-300 mb-2 capitalize">{field}</label>
                    <Input
                      value={memberData[field] || ''}
                      onChange={(e) => handleChangeField(field, e.target.value)}
                      placeholder={`Enter ${field}`}
                      className="h-12 bg-white/10 border-white/20 text-white placeholder:text-gray-400 input-focus-glow"
                      required
                    />
                  </div>
                ))}
              </div>

              {/* Identifier */}
              <div>
                <label className="block text-sm text-gray-300 mb-2 capitalize">{groupMeta.identifier || 'identifier'}</label>
                <Input
                  value={memberIdentifier}
                  onChange={(e) => setMemberIdentifier(e.target.value)}
                  placeholder={`Enter your ${groupMeta.identifier || 'identifier'}`}
                  className="h-12 bg-white/10 border-white/20 text-white placeholder:text-gray-400 input-focus-glow"
                  required
                  type={groupMeta?.identifier === 'email' ? 'email' : 'text'}
                />
              </div>

              {/* Submit */}
              <div className="pt-2">
                <Button
                  type="submit"
                  disabled={!canSubmit || loading}
                  className="h-12 w-full md:w-auto px-8 bg-indigo-600 hover:bg-indigo-500 rounded-lg font-semibold button-hover-glow"
                >
                  {loading ? 'Joining…' : 'Join Group'}
                </Button>
              </div>
            </form>
          </div>
        )}
      </div>
    </div>
  );
};

export default JoinGroupPage;
