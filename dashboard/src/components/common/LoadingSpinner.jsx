import { Loader2 } from 'lucide-react';

/**
 * Loading spinner indicator.
 * @param {{ size?: string, message?: string, className?: string }} props
 */
export default function LoadingSpinner({ size = 'md', message = '', className = '' }) {
  const sizeClasses = {
    sm: 'w-5 h-5',
    md: 'w-8 h-8',
    lg: 'w-12 h-12',
  };

  return (
    <div className={`flex flex-col items-center justify-center py-12 ${className}`}>
      <Loader2 className={`${sizeClasses[size] || sizeClasses.md} text-indigo-600 animate-spin`} />
      {message && (
        <p className="mt-3 text-sm text-slate-500">{message}</p>
      )}
    </div>
  );
}
