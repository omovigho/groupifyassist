# GroupifyAssist Frontend

A modern, professional React application for GroupifyAssist with smooth animations and intuitive UI.

## Features

- **Professional Authentication Flow**: Elegant login and signup pages with email verification
- **Smooth Animations**: Powered by Framer Motion for delightful user interactions
- **Responsive Design**: Mobile-first approach using Tailwind CSS
- **Dashboard Interface**: Comprehensive dashboard integrating with backend APIs
- **Protected Routes**: Secure routing with authentication checks
- **Modern Architecture**: Clean component structure with context-based state management

## Tech Stack

- **React 18** - Modern React with hooks
- **Vite** - Fast development and build tool
- **Tailwind CSS** - Utility-first CSS framework
- **Framer Motion** - Animation library
- **React Router** - Client-side routing
- **Lucide React** - Beautiful icon library

## Project Structure

```
src/
├── components/          # Reusable UI components
│   ├── LoadingSpinner.jsx
│   └── Button.jsx
├── contexts/           # React contexts
│   └── AuthContext.jsx
├── pages/              # Page components
│   ├── LoginPage.jsx
│   ├── SignupPage.jsx
│   └── DashboardPage.jsx
├── App.jsx             # Main app component
├── main.jsx            # Entry point
└── index.css           # Global styles
```

## Components

### Pages

- **LoginPage**: Professional login interface with form validation and error handling
- **SignupPage**: Two-step signup process with email verification
- **DashboardPage**: Comprehensive dashboard with analytics and session management

### Components

- **AuthContext**: Centralized authentication state management
- **LoadingSpinner**: Reusable loading component with customizable text
- **Button**: Flexible button component with multiple variants and loading states

### Features

- **Form Validation**: Client-side validation for all forms
- **Error Handling**: Comprehensive error display and management
- **Responsive Design**: Works seamlessly on desktop, tablet, and mobile
- **Accessibility**: ARIA labels and keyboard navigation support
- **Professional Styling**: Clean, modern interface with consistent design

## Getting Started

1. Install dependencies:
   ```bash
   npm install
   ```

2. Start development server:
   ```bash
   npm run dev
   ```

3. Build for production:
   ```bash
   npm run build
   ```

## API Integration

The frontend is designed to integrate with the FastAPI backend:

- Authentication endpoints for login, signup, and verification
- Dashboard endpoints for analytics and session data
- Notification system for real-time updates

## Styling

Custom Tailwind configuration includes:

- **Primary Colors**: Blue gradient (600-700)
- **Custom Classes**: `.btn-primary`, `.card`, `.input-field`
- **Animations**: Smooth transitions and hover effects
- **Responsive Breakpoints**: Mobile-first responsive design

## Authentication Flow

1. User visits app → redirected to login if not authenticated
2. Login form with email/password validation
3. Signup process with email verification step
4. Protected dashboard accessible after authentication
5. Automatic token management and refresh

## Development Notes

- All API calls use the `fetch` API with proper error handling
- Authentication state is managed through React Context
- Routes are protected using custom wrapper components
- Loading states are handled consistently across the app
- Error messages are user-friendly and actionable
