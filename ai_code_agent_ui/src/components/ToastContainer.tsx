import React, { useEffect } from "react";
import { type Toast, type ToastType } from "../types/common.types";

interface ToastContainerProps {
  toasts: Toast[];
  removeToast: (id: string) => void;
}

export const ToastContainer: React.FC<ToastContainerProps> = ({
  toasts,
  removeToast,
}) => {
  return (
    <div className="fixed top-5 right-5 z-50 flex flex-col gap-3 max-w-sm w-full pointer-events-none">
      {toasts.map((toast) => (
        <ToastItem key={toast.id} toast={toast} onClose={removeToast} />
      ))}
    </div>
  );
};

interface ToastItemProps {
  toast: Toast;
  onClose: (id: string) => void;
}

const ToastItem: React.FC<ToastItemProps> = ({ toast, onClose }) => {
  const { id, type, message, duration = 4000 } = toast;

  // Auto-dismiss logic
  useEffect(() => {
    const timer = setTimeout(() => {
      onClose(id);
    }, duration);

    return () => clearTimeout(timer);
  }, [id, duration, onClose]);

  // Tailwind configuration mapping for types
  const styles: Record<
    ToastType,
    { bg: string; text: string; border: string; icon: string }
  > = {
    success: {
      bg: "bg-emerald-50",
      text: "text-emerald-800",
      border: "border-emerald-200",
      icon: "✓",
    },
    error: {
      bg: "bg-rose-50",
      text: "text-rose-800",
      border: "border-rose-200",
      icon: "✕",
    },
    warning: {
      bg: "bg-amber-50",
      text: "text-amber-800",
      border: "border-amber-200",
      icon: "! ",
    },
    info: {
      bg: "bg-blue-50",
      text: "text-blue-800",
      border: "border-blue-200",
      icon: "i",
    },
  };

  const currentStyle = styles[type];

  return (
    <div
      className={`pointer-events-auto flex items-center justify-between p-4 rounded-xl border shadow-lg transition-all duration-300 transform translate-y-0 animate-fade-in ${currentStyle.bg} ${currentStyle.text} ${currentStyle.border}`}
      role="alert"
    >
      <div className="flex items-center gap-3">
        <span className="font-bold text-lg rounded-full px-1.5">
          {currentStyle.icon}
        </span>
        <p className="text-sm font-medium">{message}</p>
      </div>
      <button
        onClick={() => onClose(id)}
        className="ml-4 text-sm font-semibold hover:opacity-70 focus:outline-none"
        aria-label="Close notification"
      >
        ✕
      </button>
    </div>
  );
};
