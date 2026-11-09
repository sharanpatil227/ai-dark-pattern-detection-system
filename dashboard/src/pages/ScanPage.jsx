import { useState } from 'react';
import ScanForm from '../components/scan/ScanForm';
import ScanProgress from '../components/scan/ScanProgress';
import ScanResults from '../components/scan/ScanResults';
import { scanUrl } from '../api/client';

export default function ScanPage() {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const handleScan = async (scanData) => {
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const data = await scanUrl(scanData);
      setResult(data);
    } catch (err) {
      console.error('Scan failed:', err);
      setError(
        err.response?.data?.detail ||
          'Failed to connect to the backend detection engine. Please check if the API is running at localhost:8000.'
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      <div>
        <h1 className="text-2xl font-bold text-slate-900 tracking-tight">
          Website Dark Pattern Audit
        </h1>
        <p className="text-sm text-slate-500 mt-1">
          Evaluate any landing page, checkout flow, or signup dialog for manipulative design tactics.
        </p>
      </div>

      <ScanForm onScan={handleScan} loading={loading} />

      {error && (
        <div className="p-4 rounded-xl bg-red-50 border border-red-200 text-sm text-red-700">
          <strong>Scan Error:</strong> {error}
        </div>
      )}

      {loading && <ScanProgress />}

      {result && <ScanResults result={result} />}
    </div>
  );
}

