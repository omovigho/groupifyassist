import { useEffect, useState } from 'react';
import { Navigate } from 'react-router-dom';
import { api } from '@/lib/api';

const ProtectedRoute = ({ children }) => {
  const [ok, setOk] = useState(null);

  useEffect(()=>{
    const check = async ()=>{
      const token = localStorage.getItem('access_token');
      if (!token) return setOk(false);
      try {
        await api.get('/user/verify-token');
        setOk(true);
      } catch {
        setOk(false);
      }
    };
    check();
  },[]);

  if (ok === null) return null;
  if (!ok) return <Navigate to="/login" replace />;
  return children;
};

export default ProtectedRoute;
