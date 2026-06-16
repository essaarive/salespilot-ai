import { X } from "lucide-react";
import type { ReactNode } from "react";

interface ModalProps {
  title: string;
  open: boolean;
  onClose: () => void;
  children: ReactNode;
}

export default function Modal({ title, open, onClose, children }: ModalProps) {
  if (!open) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/40 px-4">
      <div className="w-full max-w-2xl rounded-lg bg-white shadow-soft">
        <div className="flex items-center justify-between border-b border-slate-100 px-5 py-4">
          <h2 className="text-base font-semibold text-slate-900">{title}</h2>
          <button
            type="button"
            className="rounded-md p-1.5 text-slate-500 hover:bg-slate-100"
            onClick={onClose}
            aria-label="关闭"
            title="关闭"
          >
            <X size={18} />
          </button>
        </div>
        <div className="max-h-[72vh] overflow-y-auto p-5">{children}</div>
      </div>
    </div>
  );
}
