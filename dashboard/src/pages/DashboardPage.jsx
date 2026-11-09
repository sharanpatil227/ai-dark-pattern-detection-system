import { useState, useEffect } from 'react';
import StatsCards from '../components/dashboard/StatsCards';
import RiskDistribution from '../components/dashboard/RiskDistribution';
import PatternBreakdown from '../components/dashboard/PatternBreakdown';
import ScanTimeline from '../components/dashboard/ScanTimeline';
import RecentScans from '../components/dashboard/RecentScans';
import LoadingSpinner from '../components/common/LoadingSpinner';
import { getDashboardStats, getReports } from '../api/client';

export default function DashboardPage() {
  const [stats, setStats] = useState(null);
  const [reports, setReports] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      try {
        const [statsData, reportsData] = await Promise.all([
          getDashboardStats().catch(() => null),
          getReports(1, 5).catch(() => ({ reports: [] })),
        ]);
        setStats(statsData);
        setReports(reportsData?.reports || []);
      } catch (err) {
        console.error('Failed to load dashboard data:', err);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  if (loading) {
    return <LoadingSpinner text="Loading DarkGuard Intelligence Dashboard..." />;
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900 tracking-tight">
          Deceptive Design Overview
        </h1>
        <p className="text-sm text-slate-500 mt-1">
          Real-time metrics, risk classifications, and empirical pattern frequency across monitored domains.
        </p>
      </div>

      {/* Top 4 KPI Cards */}
      <StatsCards stats={stats} />

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <RiskDistribution distribution={stats?.risk_level_distribution} />
        <PatternBreakdown categories={stats?.category_distribution} />
        <ScanTimeline timeline={stats?.scans_over_time} />
      </div>

      {/* Recent Scans Table */}
      <RecentScans reports={reports} />
    </div>
  );
}

