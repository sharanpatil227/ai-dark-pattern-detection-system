import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import ReportDetail from '../components/reports/ReportDetail';
import LoadingSpinner from '../components/common/LoadingSpinner';
import { getReport } from '../api/client';

export default function ReportDetailPage() {
  const { scanId } = useParams();
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function loadReport() {
      try {
        const data = await getReport(scanId);
        setReport(data);
      } catch (err) {
        console.error('Failed to load report:', err);
        setError('Report not found or server is unreachable.');
      } finally {
        setLoading(false);
      }
    }
    loadReport();
  }, [scanId]);

  if (loading) {
    return <LoadingSpinner text="Retrieving detailed audit report..." />;
  }

  if (error || !report) {
    return (
      <div className="bg-white rounded-xl p-8 border border-slate-200 text-center max-w-lg mx-auto mt-12">
        <h2 className="text-lg font-bold text-slate-800">Report Not Available</h2>
        <p className="text-sm text-slate-500 mt-2">{error || 'Could not find the requested scan report.'}</p>
        <Link
          to="/reports"
          className="mt-4 inline-block px-4 py-2 rounded-lg bg-indigo-600 text-white text-xs font-semibold"
        >
          &larr; Back to Reports List
        </Link>
      </div>
    );
  }

  return <ReportDetail report={report} />;
}

