import React from "react";

interface LoaderProps {
  isLoading: boolean;
}

export const Loader: React.FC<LoaderProps> = ({ isLoading }) => {
  if (!isLoading) return null;

  return (
    <div className="fixed inset-0 z-[9999] flex items-center justify-center bg-black/20 backdrop-blur-none">
      <div className="flex flex-col items-center gap-4 rounded-xl">
        {/* Animated Spinner */}
        <div className="h-12 w-12 animate-spin rounded-full border-4 border-zinc-200 border-t-black dark:border-zinc-700 dark:border-t-white" />

        {/* Loading Text */}
        <p className="text-sm font-medium tracking-wide text-[#0d0e12]">
          Loading...
        </p>
      </div>
    </div>
  );
};
