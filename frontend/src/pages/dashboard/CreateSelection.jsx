import { useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Layout from '@/components/dashboard/Layout';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { api } from '@/lib/api';
import { X, Info } from 'lucide-react';

const CreateSelection = () => {
  const navigate = useNavigate();
  const [form, setForm] = useState({
    name: '', description: '', expires_in: 1440, fields: [], max: 4, identifier: '', preferential_rules: []
  });
  const [message, setMessage] = useState('');
  const [fieldInput, setFieldInput] = useState('');
  const [rulesEnabled, setRulesEnabled] = useState(false);
  const [ruleField, setRuleField] = useState('');
  const [ruleMax, setRuleMax] = useState('');
  const [expiresValue, setExpiresValue] = useState(24);
  const [expiresUnit, setExpiresUnit] = useState('hours'); // minutes | hours | days

  const identifierConflict = useMemo(() => {
    if (!form.identifier) return false;
    return form.fields.some(f => f.trim().toLowerCase() === form.identifier.trim().toLowerCase());
  }, [form.fields, form.identifier]);

  const onSubmit = async (e) => {
    e.preventDefault();
    setMessage('');
    if (identifierConflict) {
      setMessage('Identifier must not be the same as any collected field.');
      return;
    }
    if (form.fields.length === 0) {
      setMessage('Please add at least one field to collect.');
      return;
    }
    // convert expiration to minutes for backend
    const v = parseInt(String(expiresValue || '0'), 10);
    if (!v || v <= 0) {
      setMessage('Please set a valid expiration time.');
      return;
    }
    const expiresInMinutes = expiresUnit === 'minutes' ? v : expiresUnit === 'hours' ? v * 60 : v * 1440;
    if (expiresInMinutes > 10080) {
      setMessage('Expiration cannot exceed 7 days (10080 minutes). Please reduce the expiration time.');
      return;
    }
    try {
      const payload = { ...form, expires_in: expiresInMinutes };
      const { data } = await api.post('/selections/create', payload);
      navigate('/dashboard/selections/create/success', { state: { session: data } });
    } catch (e) {
      setMessage(e?.response?.data?.detail || 'Failed to create');
    }
  };

  const addField = () => {
    const v = fieldInput.trim();
    if (!v) return;
    const exists = form.fields.some(f => f.trim().toLowerCase() === v.toLowerCase());
    if (exists) return setFieldInput('');
    if (form.identifier && v.toLowerCase() === form.identifier.trim().toLowerCase()) {
      setMessage('Field cannot be the same as identifier.');
      return;
    }
    setForm({ ...form, fields: [...form.fields, v] });
    setFieldInput('');
  };

  const removeField = (idx) => {
    const next = [...form.fields];
    next.splice(idx, 1);
    setForm({ ...form, fields: next });
  };

  const addRule = () => {
    const fk = ruleField.trim();
    const max = parseInt(ruleMax || '0', 10);
    if (!fk || !max) return;
    const next = [...(form.preferential_rules || []), { field_key: fk, preference_max_selection: max }];
    setForm({ ...form, preferential_rules: next });
    setRuleField('');
    setRuleMax('');
  };

  const removeRule = (idx) => {
    const next = [...(form.preferential_rules || [])];
    next.splice(idx, 1);
    setForm({ ...form, preferential_rules: next });
  };

  return (
    <Layout>
      <h1 className="text-xl font-semibold mb-4">Create New Selection</h1>
      <form onSubmit={onSubmit} className="rounded-2xl bg-white dark:bg-slate-900 shadow-sm border border-slate-200 dark:border-slate-800 p-5 max-w-2xl space-y-4">
        {message && <div className="text-sm text-red-600 dark:text-red-400">{message}</div>}
        <div>
          <label className="block text-sm text-slate-600 mb-1">Name</label>
          <Input value={form.name} onChange={(e)=>setForm({...form,name:e.target.value})} required />
        </div>
        <div>
          <label className="block text-sm text-slate-600 mb-1">Description</label>
          <Input value={form.description} onChange={(e)=>setForm({...form,description:e.target.value})} />
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <div>
            <label className="block text-sm text-slate-600 mb-1">Target Selection Count</label>
            <Input type="number" value={form.max} onChange={(e)=>setForm({...form,max:parseInt(e.target.value||'0',10)})} required />
          </div>
          <div>
            <label className="block text-sm text-slate-600 mb-1">Expires In</label>
            <div className="flex gap-2">
              <Input type="number" value={expiresValue} onChange={(e)=>setExpiresValue(parseInt(e.target.value||'0',10))} />
              <select
                className="h-10 w-36 rounded-md border border-input bg-background px-3 text-sm"
                value={expiresUnit}
                onChange={(e)=>setExpiresUnit(e.target.value)}
              >
                <option value="minutes">minutes</option>
                <option value="hours">hours</option>
                <option value="days">days</option>
              </select>
            </div>
          </div>
        </div>
        <div>
          <label className="block text-sm text-slate-600 mb-1">Identifier</label>
          <Input value={form.identifier} onChange={(e)=>setForm({...form,identifier:e.target.value})} required />
          {identifierConflict && (
            <p className="text-xs text-red-600 mt-1">Identifier conflicts with one of the fields below.</p>
          )}
        </div>

        {/* Dynamic fields input */}
        <div>
          <label className="block text-sm text-slate-600 mb-1">Fields to collect from participants</label>
          <div className="flex gap-2">
            <Input placeholder="e.g. state" value={fieldInput} onChange={(e)=>setFieldInput(e.target.value)} />
            <Button type="button" onClick={addField} className="bg-[#00BFA6] text-white">Add more fields</Button>
          </div>
          {form.fields.length > 0 && (
            <div className="flex flex-wrap gap-2 mt-2">
              {form.fields.map((f, idx) => (
                <span key={f+idx} className="inline-flex items-center gap-2 rounded-full bg-slate-100 dark:bg-slate-800 px-3 py-1 text-xs text-slate-700 dark:text-slate-200">
                  {f}
                  <button type="button" className="text-slate-500 hover:text-slate-700 dark:hover:text-slate-300" onClick={()=>removeField(idx)} aria-label="Remove field"><X size={14} /></button>
                </span>
              ))}
            </div>
          )}
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-2">Tip: Don’t include the identifier (e.g. matric number) as a regular field. We’ll ask for it separately.</p>
        </div>

        {/* Preferential Rules */}
        <div className="rounded-lg border border-slate-200 dark:border-slate-800 p-3">
          <div className="flex items-start gap-2">
            <Info size={16} className="mt-0.5 text-slate-500" />
            <p className="text-xs text-slate-600 dark:text-slate-300">Preferential rules let you limit selections by a field value. Example: only 1 member with state = delta per selection batch.</p>
          </div>
          {!rulesEnabled ? (
            <div className="mt-3">
              <Button type="button" onClick={()=>setRulesEnabled(true)} className="bg-emerald-600 hover:bg-emerald-700 text-white">Enable Preferential Rules</Button>
            </div>
          ) : (
            <div className="mt-3 space-y-3">
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-2">
                <div className="sm:col-span-2">
                  <Input placeholder="Field key (e.g. delta)" value={ruleField} onChange={(e)=>setRuleField(e.target.value)} />
                </div>
                <div className="flex gap-2">
                  <Input type="number" placeholder="Preference max selection" value={ruleMax} onChange={(e)=>setRuleMax(e.target.value)} />
                  <Button type="button" onClick={addRule}>Add</Button>
                </div>
              </div>
              {(form.preferential_rules || []).length > 0 && (
                <div className="flex flex-wrap gap-2">
                  {form.preferential_rules.map((r, idx) => (
                    <span key={idx} className="inline-flex items-center gap-2 rounded-full bg-slate-100 dark:bg-slate-800 px-3 py-1 text-xs text-slate-700 dark:text-slate-200">
                      {r.field_key} • pref max {r.preference_max_selection}
                      <button type="button" onClick={()=>removeRule(idx)} aria-label="Remove rule" className="text-slate-500 hover:text-slate-700 dark:hover:text-slate-300"><X size={14} /></button>
                    </span>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>

        <Button type="submit" className="bg-[#00BFA6] text-white" disabled={identifierConflict}>Create Selection</Button>
      </form>
    </Layout>
  );
};

export default CreateSelection;
