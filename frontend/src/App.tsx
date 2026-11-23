import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import { Sidebar } from './components/layout/Sidebar';
import { Navbar } from './components/layout/Navbar';

import { OverviewPage } from './pages/OverviewPage';
import { TransactionsPage } from './pages/TransactionsPage';
import { FraudPage } from './pages/FraudPage';
import { ReceiptScannerPage } from './pages/ReceiptScannerPage';
import { AIAssistantPage } from './pages/AIAssistantPage';
import { AnalyticsPage } from './pages/AnalyticsPage';
import { BudgetPage } from './pages/BudgetPage';
import { SubscriptionsPage } from './pages/SubscriptionsPage';
import { SimulatorPage } from './pages/SimulatorPage';
import { RootCausePage } from './pages/RootCausePage';
import { AuditLogsPage } from './pages/AuditLogsPage';
import { NotificationsPage } from './pages/NotificationsPage';
import { SettingsPage } from './pages/SettingsPage';
import { LoginPage } from './pages/LoginPage';

const ProtectedLayout: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div className="min-h-screen bg-slate-950 flex items-center justify-center">
        <div className="w-8 h-8 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin"></div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return (
    <div className="flex min-h-screen bg-slate-950 text-slate-100">
      <Sidebar />
      <div className="flex-1 flex flex-col min-w-0">
        <Navbar />
        <main className="flex-1 p-8 overflow-y-auto max-w-7xl w-full mx-auto">
          {children}
        </main>
      </div>
    </div>
  );
};

export function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route
            path="/"
            element={
              <ProtectedLayout>
                <OverviewPage />
              </ProtectedLayout>
            }
          />
          <Route
            path="/transactions"
            element={
              <ProtectedLayout>
                <TransactionsPage />
              </ProtectedLayout>
            }
          />
          <Route
            path="/fraud"
            element={
              <ProtectedLayout>
                <FraudPage />
              </ProtectedLayout>
            }
          />
          <Route
            path="/receipts"
            element={
              <ProtectedLayout>
                <ReceiptScannerPage />
              </ProtectedLayout>
            }
          />
          <Route
            path="/assistant"
            element={
              <ProtectedLayout>
                <AIAssistantPage />
              </ProtectedLayout>
            }
          />
          <Route
            path="/analytics"
            element={
              <ProtectedLayout>
                <AnalyticsPage />
              </ProtectedLayout>
            }
          />
          <Route
            path="/budgets"
            element={
              <ProtectedLayout>
                <BudgetPage />
              </ProtectedLayout>
            }
          />
          <Route
            path="/subscriptions"
            element={
              <ProtectedLayout>
                <SubscriptionsPage />
              </ProtectedLayout>
            }
          />
          <Route
            path="/simulator"
            element={
              <ProtectedLayout>
                <SimulatorPage />
              </ProtectedLayout>
            }
          />
          <Route
            path="/root-cause"
            element={
              <ProtectedLayout>
                <RootCausePage />
              </ProtectedLayout>
            }
          />
          <Route
            path="/audit"
            element={
              <ProtectedLayout>
                <AuditLogsPage />
              </ProtectedLayout>
            }
          />
          <Route
            path="/notifications"
            element={
              <ProtectedLayout>
                <NotificationsPage />
              </ProtectedLayout>
            }
          />
          <Route
            path="/settings"
            element={
              <ProtectedLayout>
                <SettingsPage />
              </ProtectedLayout>
            }
          />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;
