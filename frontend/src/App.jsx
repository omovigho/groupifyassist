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
import './index.css';

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
        </Routes>
      </div>
    </Router>
  );
}

export default App;
