import type { LucideIcon } from "lucide-react";

interface StatCardProps {
  label: string;
  value: number | string;
  icon: LucideIcon;
}

export default function StatCard({ label, value, icon: Icon }: StatCardProps) {
  return (
    <div className="rounded-lg border border-slate-200 bg-white p-5">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm text-slate-500">{label}</p>
          <p className="mt-2 text-2xl font-semibold text-slate-950">{value}</p>
        </div>
        <div className="flex h-11 w-11 items-center justify-center rounded-md bg-brand-50 text-brand-600">
          <Icon size={22} />
        </div>
      </div>
    </div>
  );
}
