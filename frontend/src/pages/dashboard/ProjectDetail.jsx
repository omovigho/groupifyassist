import { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import Layout from '@/components/dashboard/Layout';
import { api } from '@/lib/api';

const TabButton = ({label,active,onClick}) => (
  <button onClick={onClick} className={`px-3 py-2 text-sm rounded-md border ${active?'bg-white':'bg-slate-50'} border-slate-200`}>{label}</button>
);

const ProjectDetail = ({ type }) => {
  const { id } = useParams();
  const [tab, setTab] = useState('Overview');
  const [info, setInfo] = useState(null);

  useEffect(()=>{
    const load = async ()=>{
      try {
        const { data } = await api.get(`/dashboard/sessions/history?session_type=${type}&limit=1&offset=0`);
        const found = (data?.sessions||[]).find(s=>String(s.id)===String(id));
        setInfo(found || null);
      } catch {}
    };
    load();
  },[id,type]);

  return (
    <Layout>
      <div className="flex items-center justify-between mb-4">
        <div>
          <h1 className="text-xl font-semibold">{info?.name || `${type} session`} (ID: {id})</h1>
          <p className="text-slate-600 text-sm">Status: <span className="font-medium capitalize">{info?.status}</span></p>
        </div>
      </div>

      <div className="flex items-center gap-2 mb-4">
        {['Overview','Members','Group Rules','Preferential Rules','Selection Rules','Results'].map(l=> (
          <TabButton key={l} label={l} active={tab===l} onClick={()=>setTab(l)} />
        ))}
      </div>

  <div className="rounded-2xl bg-white dark:bg-slate-800 shadow-sm border border-slate-200 dark:border-slate-800 p-5">
        {tab === 'Overview' && (
          <div className="space-y-2 text-sm text-slate-700">
            <p><span className="font-medium">Description:</span> {info?.description || '-'}</p>
            <p><span className="font-medium">Created:</span> {info?.created_at ? new Date(info.created_at).toLocaleString() : '-'}</p>
            <p><span className="font-medium">Participants:</span> {info?.participant_count ?? 0}</p>
          </div>
        )}
        {tab === 'Members' && (
          <MemberList id={id} type={type} />
        )}
        {tab === 'Results' && (
          <ResultsActions id={id} type={type} />
        )}
        {tab !== 'Overview' && tab !== 'Members' && tab !== 'Results' && (
          <div className="text-sm text-slate-500">This section will be enabled when the corresponding API endpoints are available.</div>
        )}
      </div>
    </Layout>
  );
};

const MemberList = ({ id, type }) => {
  const [rows, setRows] = useState([]);
  useEffect(()=>{
    const load = async ()=>{
      try {
        const { data } = await api.get(`/dashboard/sessions/${id}/participants?session_type=${type}&limit=100&offset=0`);
        setRows(data?.participants || []);
      } catch {}
    };
    load();
  },[id,type]);

  return (
    <div className="overflow-x-auto -mx-5 mt-2">
      <table className="min-w-full divide-y divide-slate-200">
        <thead className="bg-slate-50">
          <tr>
            <th className="px-4 py-3 text-left text-xs font-medium text-slate-500">Identifier</th>
            <th className="px-4 py-3 text-left text-xs font-medium text-slate-500">Joined</th>
            <th className="px-4 py-3 text-left text-xs font-medium text-slate-500">Data</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-200 bg-white">
          {rows.length === 0 ? (
            <tr><td colSpan={3} className="px-4 py-6 text-sm text-slate-500">No members yet.</td></tr>
          ) : rows.map((r)=> (
            <tr key={r.id}>
              <td className="px-4 py-3 text-sm">{r.identifier}</td>
              <td className="px-4 py-3 text-sm">{r.joined_at ? new Date(r.joined_at).toLocaleString() : '-'}</td>
              <td className="px-4 py-3 text-sm">{r.data ? JSON.stringify(r.data) : '-'}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default ProjectDetail;

const ResultsActions = ({ id, type }) => {
  const [code, setCode] = useState('');
  const [msg, setMsg] = useState('');

  const download = async (format) => {
    try {
      if (!code.trim()) return setMsg('Provide access code');
      const base = (import.meta?.env?.VITE_API_BASE_URL) || 'https://groupifyassist.onrender.com';
      const url = type === 'group'
        ? `${base}/export/group-session/${id}/${format}?access_code=${encodeURIComponent(code.trim())}`
        : `${base}/export/selection-session/${id}/${format}?access_code=${encodeURIComponent(code.trim())}`;
      window.open(url, '_blank');
      setMsg('');
    } catch (e) {
      setMsg('Failed to start download');
    }
  };

  return (
    <div className="space-y-3">
      <div className="text-sm text-slate-600">Enter the active access code for this session to export results.</div>
      <div className="flex items-center gap-2">
        <input value={code} onChange={(e)=>setCode(e.target.value)} placeholder="Access code" className="h-9 rounded-md border border-slate-300 px-3 text-sm" />
        <button onClick={()=>download('excel')} className="rounded-md bg-[#0A2540] text-white text-sm px-3 py-2">Export Excel</button>
        <button onClick={()=>download('pdf')} className="rounded-md bg-[#00BFA6] text-white text-sm px-3 py-2">Export PDF</button>
      </div>
      {msg && <div className="text-sm text-red-600">{msg}</div>}
    </div>
  );
};
