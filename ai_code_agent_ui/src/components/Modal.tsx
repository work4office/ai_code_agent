import React, { useEffect } from "react";
import useApi from "../hooks/useApi";
import { useCommonContext } from "../context/CommonContext";

interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  children: React.ReactNode;
}

export const Modal: React.FC<ModalProps> = ({
  isOpen,
  onClose,
  title,
  children,
}) => {
  const { confirm_changes, get_file_tree } = useApi();
  const { activeProject } = useCommonContext();
  // Close modal on Escape key press
  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        onClose();
      }
    };

    if (isOpen) {
      window.addEventListener("keydown", handleKeyDown);
      // Lock background scrolling when modal is open
      document.body.style.overflow = "hidden";
    }

    return () => {
      window.removeEventListener("keydown", handleKeyDown);
      document.body.style.overflow = "unset";
    };
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  const onConfirm = async (isConfirmed: boolean) => {
    onClose();
    const res = await confirm_changes(isConfirmed, activeProject);
    if (res?.approved && res.applied_files?.length > 0) {
      await get_file_tree(activeProject, true);
    }
  };

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center sm:p-4"
      role="dialog"
      aria-modal="true"
    >
      {/* Backdrop overlay */}
      <div
        className="fixed inset-0 bg-slate-900/40 backdrop-blur-sm transition-opacity hidden sm:block"
        onClick={() => onConfirm(false)}
        aria-hidden="true"
      />

      {/* Modal Content Box */}
      <div className="relative transform overflow-hidden bg-white text-left shadow-xl transition-all w-full h-full sm:rounded-2xl sm:border sm:border-slate-100 flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-6 pb-2 pt-2 border-b border-slate-100 flex-shrink-0">
          <h3 className="text-lg font-semibold text-slate-900">{title}</h3>
          <button
            onClick={() => onConfirm(false)}
            className="cursor-pointer rounded-lg p-1.5 text-slate-400 hover:bg-slate-50 hover:text-slate-600 transition-colors"
            aria-label="Close modal"
          >
            <svg
              className="h-5 w-5"
              fill="none"
              viewBox="0 0 24 24"
              strokeWidth="2"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M6 18L18 6M6 6l12 12"
              />
            </svg>
          </button>
        </div>

        {/* Body Content */}
        <div className="p-6 pt-2 pb-2 text-sm text-slate-600 leading-relaxed overflow-y-auto flex-grow">
          {children}
        </div>

        {/* Footer Actions */}
        <div className="pr-6 pt-2 pb-2 border-t border-slate-100 flex flex-col-reverse gap-2 sm:flex-row sm:justify-end sm:gap-3 flex-shrink-0">
          <button
            type="button"
            onClick={() => onConfirm(true)}
            className="cursor-pointer w-full sm:w-auto inline-flex justify-center rounded-xl bg-white px-4 py-2.5 text-sm font-semibold text-slate-700 shadow-sm ring-1 ring-inset ring-slate-300 hover:bg-slate-50 transition-colors"
          >
            Approve
          </button>
          <button
            type="button"
            onClick={() => onConfirm(false)}
            className="cursor-pointer w-full sm:w-auto inline-flex justify-center rounded-xl bg-white px-4 py-2.5 text-sm font-semibold text-slate-700 shadow-sm ring-1 ring-inset ring-slate-300 hover:bg-slate-50 transition-colors"
          >
            Reject
          </button>
        </div>
      </div>
    </div>
  );
};
