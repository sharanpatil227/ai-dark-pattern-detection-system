import { useState, useEffect } from 'react';
import ReportList from '../components/reports/ReportList';
import LoadingSpinner from '../components/common/LoadingSpinner';
import { getReports } from '../api/client';

export default function ReportsPage() {
  const [reports, setReports] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);

  const fetchReports = async (currentPage, filterUrl) => {
    setLoading(true);
    try {
      const data = await getReports(currentPage, 15);
      let list = data?.reports || [];
      if (filterUrl.trim()) {
        list = list.filter((r) =>
          r.url.toLowerCase().includes(filterUrl.toLowerCase())
        );
      }
      setReports(list);
      setTotalPages(data?.total_pages || 1);
    } catch (err) {
      console.error('Failed to fetch reports:', err);
      setReports([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchReports(page, search);
  }, [page, search]);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900 tracking-tight">
          Audit Reports Directory
        </h1>
        <p className="text-sm text-slate-500 mt-1">
          Historical log of all scanned webpages with risk scores and detected deceptive patterns.
        </p>
      </div>

      {loading ? (
        <LoadingSpinner text="Retrieving historical reports..." />
      ) : (
        <ReportList
          reports={reports}
          searchQuery={search}
          onSearchChange={(q) => {
            setSearch(q);
            setPage(1);
          }}
          page={page}
          totalPages={totalPages}
          onPageChange={setPage}
        />
      )}
    </div>
  );
}

