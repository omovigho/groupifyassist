import { useEffect, useState } from 'react';
import Layout from '@/components/dashboard/Layout';
import { api } from '@/lib/api';

const Exports = () => {
  const [rows, setRows] = useState([]);
  const [q, setQ] = useState('');
  const [page, setPage] = useState(0);
  const [limit, setLimit] = useState(10);
  const [total, setTotal] = useState(0);
  const [downloading, setDownloading] = useState({}); // key: `${type}_${id}_${fmt}` => boolean

  useEffect(() => {
    const load = async () => {
      try {
        const params = new URLSearchParams({ session_type: 'all', limit: String(limit), offset: String(page*limit) });
        if (q) params.set('q', q);
        const { data } = await api.get(`/dashboard/sessions/history?${params.toString()}`);
        setRows(data?.sessions || []);
        setTotal(data?.total_count || 0);
      } catch {}
    };
    const id = setTimeout(load, 250);
    return () => clearTimeout(id);
  }, [q, page, limit]);

  const getExportPath = (row, fmt) => {
    const access = row.access_code;
    if (row.type === 'group') {
      return fmt === 'excel'
        ? `/export/group-session/${row.id}/excel?access_code=${encodeURIComponent(access)}`
        : `/export/group-session/${row.id}/pdf?access_code=${encodeURIComponent(access)}`;
    }
    return fmt === 'excel'
      ? `/export/selection-session/${row.id}/excel?access_code=${encodeURIComponent(access)}`
      : `/export/selection-session/${row.id}/pdf?access_code=${encodeURIComponent(access)}`;
  };

  const handleDownload = async (row, fmt) => {
    const key = `${row.type}_${row.id}_${fmt}`;
    try {
      setDownloading((m) => ({ ...m, [key]: true }));
      const url = getExportPath(row, fmt);
      const res = await api.get(url, { responseType: 'blob' });
      const blob = new Blob([res.data], { type: res.headers['content-type'] || (fmt === 'pdf' ? 'application/pdf' : 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet') });
      const contentDisp = res.headers['content-disposition'] || '';
      const match = /filename\s*=\s*([^;]+)/i.exec(contentDisp);
      const fallbackName = `${row.type}_session_${row.name?.replaceAll(' ', '_') || row.id}_${row.id}.${fmt === 'pdf' ? 'pdf' : 'xlsx'}`;
      const filename = match ? decodeURIComponent(match[1].replace(/"/g, '').trim()) : fallbackName;
      const link = document.createElement('a');
      const blobUrl = URL.createObjectURL(blob);
      link.href = blobUrl;
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      link.remove();
      URL.revokeObjectURL(blobUrl);
    } catch (e) {
      console.error('Download failed', e);
      alert('Failed to download. Please try again.');
    } finally {
      setDownloading((m) => ({ ...m, [key]: false }));
    }
  };

  return (
    <Layout>
      <div className="rounded-2xl bg-[#0A2540] text-white px-4 py-3 mb-4 flex items-center justify-between">
        <h1 className="text-xl font-semibold">Export Results</h1>
        <div className="flex items-center gap-2">
          <input
            value={q}
            onChange={(e)=>{ setPage(0); setQ(e.target.value); }}
            placeholder="Search by name..."
            className="h-9 rounded-md border border-transparent px-3 text-sm bg-white text-black placeholder:text-slate-500"
          />
        </div>
      </div>
      <div className="rounded-2xl bg-white dark:bg-slate-900 shadow-sm border border-slate-200 dark:border-slate-800 overflow-x-auto">
        <table className="min-w-full divide-y divide-slate-200 dark:divide-slate-800">
          <thead className="bg-slate-50 dark:bg-slate-900">
            <tr>
              <th className="px-4 py-3 text-left text-xs font-medium text-slate-500 dark:text-slate-400">Name</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-slate-500 dark:text-slate-400">Type</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-slate-500 dark:text-slate-400">Created At</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-slate-500 dark:text-slate-400">Download</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-200 dark:divide-slate-800 bg-white dark:bg-slate-900">
            {rows.length === 0 ? (
              <tr><td colSpan={4} className="px-4 py-6 text-sm text-slate-500 dark:text-slate-400">No sessions found.</td></tr>
            ) : rows.map((r)=> {
              const label = r.type === 'group' ? 'Groups' : 'Selections';
              return (
                <tr key={`x_${r.type}_${r.id}`}>
                  <td className="px-4 py-3 text-sm text-slate-700 dark:text-slate-200">{r.name}</td>
                  <td className="px-4 py-3 text-sm capitalize">{label}</td>
                  <td className="px-4 py-3 text-sm">{new Date(r.created_at).toLocaleString()}</td>
                  <td className="px-4 py-3 text-sm">
                    <div className="flex items-center gap-2">
                      {['excel','pdf'].map((fmt) => {
                        const key = `${r.type}_${r.id}_${fmt}`;
                        const isLoading = !!downloading[key];
                        const btnClass = fmt === 'excel' ? 'bg-[#0A2540]' : 'bg-[#00BFA6]';
                        const label = fmt === 'excel' ? 'Excel' : 'PDF';
                        return (
                          <button
                            key={fmt}
                            disabled={isLoading}
                            onClick={() => handleDownload(r, fmt)}
                            className={`inline-flex items-center gap-1 rounded-md ${btnClass} text-white text-xs px-3 py-2 disabled:opacity-60`}
                          >
                            {isLoading ? (
                              <span className="flex items-center gap-1">
                                <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z"></path>
                                </svg>
                                Downloading...
                              </span>
                            ) : (
                              <span>{label}</span>
                            )}
                          </button>
                        );
                      })}
                    </div>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
        <div className="flex items-center justify-between px-4 py-3 border-t border-slate-200 dark:border-slate-800">
          <span className="text-xs text-slate-600 dark:text-slate-400">Page {page+1} of {Math.max(1, Math.ceil(total/limit))}</span>
          <div className="flex items-center gap-2">
            <button className="px-3 py-1.5 rounded-md border text-sm disabled:opacity-50" disabled={page===0} onClick={()=>setPage(p=>Math.max(0,p-1))}>Previous</button>
            <button className="px-3 py-1.5 rounded-md border text-sm disabled:opacity-50" disabled={(page+1)*limit>=total} onClick={()=>setPage(p=>p+1)}>Next</button>
          </div>
        </div>
      </div>
    </Layout>
  );
};

export default Exports;
