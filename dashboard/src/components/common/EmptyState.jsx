import { Inbox } from 'lucide-react';

/**
 * Empty state placeholder component.
 * @param {{ title?: string, message?: string, icon?: React.ElementType, action?: React.ReactNode }} props
 */
export default function EmptyState({
  title = 'No data yet',
  message = 'There is nothing to display at this time.',
  icon: Icon = Inbox,
  action,
}) {
  return (
    <div className="flex flex-col items-center justify-center py-16 px-4 text-center">
      <div className="w-16 h-16 rounded-full bg-slate-100 flex items-center justify-center mb-4">
        <Icon className="w-8 h-8 text-slate-400" />
      </div>
      <h3 className="text-lg font-semibold text-slate-700 mb-1">{title}</h3>
      <p className="text-sm text-slate-500 max-w-sm mb-4">{message}</p>
      {action && <div>{action}</div>}
    </div>
  );
}
