import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
// eslint-disable-next-line no-unused-vars
import { motion } from 'framer-motion';
import { Eye, EyeOff, Mail, Lock, User, Globe, UserPlus, Users, CheckCircle } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import LoadingSpinner from '../components/LoadingSpinner';

const SignupPage = () => {
  const [step, setStep] = useState(1); // 1: signup form, 2: email verification
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    confirm_password: '',
    country: ''
  });
  const [verificationCode, setVerificationCode] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const { signup, verifyEmail, resendVerification } = useAuth();
  const navigate = useNavigate();

  const countries = [
    'Nigeria', 'Ghana', 'Kenya', 'South Africa', 'Egypt', 'Morocco',
    'United States', 'United Kingdom', 'Canada', 'Australia',
    'Germany', 'France', 'Spain', 'Italy', 'Netherlands',
    'India', 'China', 'Japan', 'South Korea', 'Singapore',
    'Brazil', 'Argentina', 'Mexico', 'Other'
  ];

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
    if (error) setError('');
  };

  const handleSignup = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    // Validation
    if (formData.password !== formData.confirm_password) {
      setError('Passwords do not match');
      setLoading(false);
      return;
    }

    if (formData.password.length < 8) {
      setError('Password must be at least 8 characters long');
      setLoading(false);
      return;
    }

    const result = await signup(formData);
    
    if (result.success) {
      setSuccess(result.message);
      setStep(2);
    } else {
      setError(result.error);
    }
    
    setLoading(false);
  };

  const handleVerification = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    const result = await verifyEmail(formData.email, verificationCode);
    
    if (result.success) {
      setSuccess(result.message);
      setTimeout(() => navigate('/login'), 2000);
    } else {
      setError(result.error);
    }
    
    setLoading(false);
  };

  const handleResendCode = async () => {
    setLoading(true);
    const result = await resendVerification(formData.email);
    
    if (result.success) {
      setSuccess(result.message);
    } else {
      setError(result.error);
    }
    
    setLoading(false);
  };

  const containerVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: {
      opacity: 1,
      y: 0,
      transition: {
        duration: 0.6,
        staggerChildren: 0.1
      }
    }
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: { opacity: 1, y: 0 }
  };

  return (
    <div className="min-h-screen flex items-center justify-center px-4 py-12 bg-gradient-to-br from-blue-50 via-white to-purple-50">
      <motion.div
        className="w-full max-w-md"
        variants={containerVariants}
        initial="hidden"
        animate="visible"
        key={step} // Re-animate when step changes
      >
        {/* Logo and Header */}
        <motion.div variants={itemVariants} className="text-center mb-8">
          <div className="flex items-center justify-center mb-4">
            <div className="bg-primary-600 p-3 rounded-xl shadow-lg">
              <Users className="w-8 h-8 text-white" />
            </div>
          </div>
          <h2 className="text-3xl font-bold text-gray-900">
            {step === 1 ? 'Create Account' : 'Verify Email'}
          </h2>
          <p className="mt-2 text-gray-600">
            {step === 1 
              ? 'Join GroupifyAssist to organize your teams'
              : `Enter the verification code sent to ${formData.email}`
            }
          </p>
        </motion.div>

        {/* Form */}
        <motion.div 
          variants={itemVariants}
          className="card p-8"
        >
          {step === 1 ? (
            // Signup Form
            <form onSubmit={handleSignup} className="space-y-6">
              {/* Email Field */}
              <div>
                <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-2">
                  Email Address
                </label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <Mail className="h-5 w-5 text-gray-400" />
                  </div>
                  <input
                    id="email"
                    name="email"
                    type="email"
                    autoComplete="email"
                    required
                    value={formData.email}
                    onChange={handleChange}
                    className="input-field pl-10"
                    placeholder="Enter your email"
                  />
                </div>
              </div>

              {/* Country Field */}
              <div>
                <label htmlFor="country" className="block text-sm font-medium text-gray-700 mb-2">
                  Country
                </label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <Globe className="h-5 w-5 text-gray-400" />
                  </div>
                  <select
                    id="country"
                    name="country"
                    required
                    value={formData.country}
                    onChange={handleChange}
                    className="input-field pl-10"
                  >
                    <option value="">Select your country</option>
                    {countries.map((country) => (
                      <option key={country} value={country}>{country}</option>
                    ))}
                  </select>
                </div>
              </div>

              {/* Password Field */}
              <div>
                <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-2">
                  Password
                </label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <Lock className="h-5 w-5 text-gray-400" />
                  </div>
                  <input
                    id="password"
                    name="password"
                    type={showPassword ? 'text' : 'password'}
                    autoComplete="new-password"
                    required
                    value={formData.password}
                    onChange={handleChange}
                    className="input-field pl-10 pr-10"
                    placeholder="Create a password"
                  />
                  <button
                    type="button"
                    className="absolute inset-y-0 right-0 pr-3 flex items-center"
                    onClick={() => setShowPassword(!showPassword)}
                  >
                    {showPassword ? (
                      <EyeOff className="h-5 w-5 text-gray-400 hover:text-gray-600" />
                    ) : (
                      <Eye className="h-5 w-5 text-gray-400 hover:text-gray-600" />
                    )}
                  </button>
                </div>
              </div>

              {/* Confirm Password Field */}
              <div>
                <label htmlFor="confirm_password" className="block text-sm font-medium text-gray-700 mb-2">
                  Confirm Password
                </label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <Lock className="h-5 w-5 text-gray-400" />
                  </div>
                  <input
                    id="confirm_password"
                    name="confirm_password"
                    type={showConfirmPassword ? 'text' : 'password'}
                    autoComplete="new-password"
                    required
                    value={formData.confirm_password}
                    onChange={handleChange}
                    className="input-field pl-10 pr-10"
                    placeholder="Confirm your password"
                  />
                  <button
                    type="button"
                    className="absolute inset-y-0 right-0 pr-3 flex items-center"
                    onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                  >
                    {showConfirmPassword ? (
                      <EyeOff className="h-5 w-5 text-gray-400 hover:text-gray-600" />
                    ) : (
                      <Eye className="h-5 w-5 text-gray-400 hover:text-gray-600" />
                    )}
                  </button>
                </div>
              </div>

              {/* Error/Success Message */}
              {(error || success) && (
                <motion.div
                  initial={{ opacity: 0, scale: 0.95 }}
                  animate={{ opacity: 1, scale: 1 }}
                  className={`px-4 py-3 rounded-lg ${
                    error 
                      ? 'bg-red-50 border border-red-200 text-red-700'
                      : 'bg-green-50 border border-green-200 text-green-700'
                  }`}
                >
                  {error || success}
                </motion.div>
              )}

              {/* Submit Button */}
              <motion.button
                type="submit"
                disabled={loading}
                className="w-full btn-primary flex items-center justify-center"
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
              >
                {loading ? (
                  <LoadingSpinner size="sm" text="" fullScreen={false} />
                ) : (
                  <>
                    <UserPlus className="w-5 h-5 mr-2" />
                    Create Account
                  </>
                )}
              </motion.button>
            </form>
          ) : (
            // Email Verification Form
            <form onSubmit={handleVerification} className="space-y-6">
              <div className="text-center">
                <div className="bg-blue-50 p-4 rounded-lg mb-6">
                  <Mail className="w-12 h-12 text-blue-600 mx-auto mb-2" />
                  <p className="text-gray-600">
                    We've sent a verification code to your email address. 
                    Please check your inbox and enter the code below.
                  </p>
                </div>
              </div>

              {/* Verification Code Field */}
              <div>
                <label htmlFor="verificationCode" className="block text-sm font-medium text-gray-700 mb-2">
                  Verification Code
                </label>
                <input
                  id="verificationCode"
                  name="verificationCode"
                  type="text"
                  required
                  value={verificationCode}
                  onChange={(e) => setVerificationCode(e.target.value)}
                  className="input-field text-center text-lg font-mono"
                  placeholder="Enter 6-digit code"
                  maxLength={6}
                />
              </div>

              {/* Error/Success Message */}
              {(error || success) && (
                <motion.div
                  initial={{ opacity: 0, scale: 0.95 }}
                  animate={{ opacity: 1, scale: 1 }}
                  className={`px-4 py-3 rounded-lg ${
                    error 
                      ? 'bg-red-50 border border-red-200 text-red-700'
                      : 'bg-green-50 border border-green-200 text-green-700'
                  }`}
                >
                  {error || success}
                </motion.div>
              )}

              {/* Submit Button */}
              <motion.button
                type="submit"
                disabled={loading}
                className="w-full btn-primary flex items-center justify-center"
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
              >
                {loading ? (
                  <LoadingSpinner size="sm" text="" fullScreen={false} />
                ) : (
                  <>
                    <CheckCircle className="w-5 h-5 mr-2" />
                    Verify Email
                  </>
                )}
              </motion.button>

              {/* Resend Code */}
              <div className="text-center">
                <button
                  type="button"
                  onClick={handleResendCode}
                  disabled={loading}
                  className="text-sm text-primary-600 hover:text-primary-700 font-medium"
                >
                  Didn't receive the code? Resend
                </button>
              </div>
            </form>
          )}
        </motion.div>

        {/* Back to Login Link */}
        <motion.div 
          variants={itemVariants}
          className="mt-6 text-center"
        >
          <p className="text-gray-600">
            Already have an account?{' '}
            <Link
              to="/login"
              className="font-medium text-primary-600 hover:text-primary-700 transition-colors"
            >
              Sign in here
            </Link>
          </p>
        </motion.div>
      </motion.div>
    </div>
  );
};

export default SignupPage;
