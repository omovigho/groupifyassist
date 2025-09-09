import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import SimpleLandingPage from './components/SimpleLandingPage';
import SignupPage from './components/SignupPage';
import LoginPage from './components/LoginPage';
import EmailConfirmationPage from './components/EmailConfirmationPage';
import RegistrationSuccessPage from './components/RegistrationSuccessPage';
import ForgotPasswordPage from './components/ForgotPasswordPage';
import ForgotPasswordVerificationPage from './components/ForgotPasswordVerificationPage';
import ChangePasswordPage from './components/ChangePasswordPage';
import ChangePasswordSuccessPage from './components/ChangePasswordSuccessPage';
import JoinGroupPage from './components/JoinGroupPage';
import JoinSuccessPage from './components/JoinSuccessPage';
import JoinSelectionPage from './components/JoinSelectionPage';
import JoinSelectionSuccessPage from './components/JoinSelectionSuccessPage';
import './index.css';
import ProtectedRoute from './components/ProtectedRoute';
import Overview from './pages/dashboard/Overview';
import Groups from './pages/dashboard/Groups';
import Selections from './pages/dashboard/Selections';
import Exports from './pages/dashboard/Exports';
import Settings from './pages/dashboard/Settings';
import CreateGroup from './pages/dashboard/CreateGroup';
import CreateSelection from './pages/dashboard/CreateSelection';
import ProjectDetail from './pages/dashboard/ProjectDetail';
import CreateSuccess from './pages/dashboard/CreateSuccess';
import MakeSelection from './pages/dashboard/MakeSelection';
import ClearSelection from './pages/dashboard/ClearSelection';
import LogoutPage from './components/LogoutPage';

function App() {
  return (
    <Router>
      <div className="App">
        <Routes>
          <Route path="/" element={<SimpleLandingPage />} />
          <Route path="/signup" element={<SignupPage />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/verify-email" element={<EmailConfirmationPage />} />
          <Route path="/register-success" element={<RegistrationSuccessPage />} />
          <Route path="/forgot-password" element={<ForgotPasswordPage />} />
          <Route path="/forgot-password-verify" element={<ForgotPasswordVerificationPage />} />
          <Route path="/change-password" element={<ChangePasswordPage />} />
          <Route path="/change-password-success" element={<ChangePasswordSuccessPage />} />
          <Route path="/join" element={<JoinGroupPage />} />
          <Route path="/join/success" element={<JoinSuccessPage />} />
          <Route path="/selection/join" element={<JoinSelectionPage />} />
          <Route path="/selection/join/success" element={<JoinSelectionSuccessPage />} />
          {/* Dashboard routes (protected) */}
          <Route
            path="/dashboard"
            element={
              <ProtectedRoute>
                <Overview />
              </ProtectedRoute>
            }
          />
          <Route
            path="/dashboard/groups"
            element={
              <ProtectedRoute>
                <Groups />
              </ProtectedRoute>
            }
          />
          <Route
            path="/dashboard/groups/create"
            element={
              <ProtectedRoute>
                <CreateGroup />
              </ProtectedRoute>
            }
          />
          <Route
            path="/dashboard/groups/create/success"
            element={
              <ProtectedRoute>
                <CreateSuccess />
              </ProtectedRoute>
            }
          />
          <Route
            path="/dashboard/selections"
            element={
              <ProtectedRoute>
                <Selections />
              </ProtectedRoute>
            }
          />
          <Route
            path="/dashboard/selections/create"
            element={
              <ProtectedRoute>
                <CreateSelection />
              </ProtectedRoute>
            }
          />
          <Route
            path="/dashboard/selections/create/success"
            element={
              <ProtectedRoute>
                <CreateSuccess />
              </ProtectedRoute>
            }
          />
          <Route
            path="/dashboard/selections/make"
            element={
              <ProtectedRoute>
                <MakeSelection />
              </ProtectedRoute>
            }
          />
          <Route
            path="/dashboard/exports"
            element={
              <ProtectedRoute>
                <Exports />
              </ProtectedRoute>
            }
          />
          <Route
            path="/dashboard/selections/clear"
            element={
              <ProtectedRoute>
                <ClearSelection />
              </ProtectedRoute>
            }
          />
          <Route
            path="/dashboard/settings"
            element={
              <ProtectedRoute>
                <Settings />
              </ProtectedRoute>
            }
          />
          <Route
            path="/dashboard/projects/:type/:id"
            element={
              <ProtectedRoute>
                <ProjectDetail />
              </ProtectedRoute>
            }
          />
          <Route path="/logout" element={<LogoutPage />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
