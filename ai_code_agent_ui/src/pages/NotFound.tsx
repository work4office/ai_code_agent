import React from "react";

export default function NotFound() {
  return (
    <main className="grid min-h-screen place-items-center bg-slate-950 px-6 py-24 sm:py-32 lg:px-8">
      <div className="text-center">
        {/* Decorative elements */}
        <div className="relative mx-auto h-24 w-24">
          <div className="absolute inset-0 animate-ping rounded-full bg-indigo-500/20 opacity-75"></div>
          <div className="relative flex h-24 w-24 items-center justify-center rounded-full bg-indigo-950 border border-indigo-500/30">
            <span className="text-4xl font-extrabold text-indigo-400">404</span>
          </div>
        </div>

        {/* Error Messages */}
        <h1 className="mt-6 text-3xl font-bold tracking-tight text-slate-100 sm:text-5xl">
          Page not found
        </h1>
        <p className="mt-4 text-base leading-7 text-slate-400 max-w-md mx-auto">
          Sorry, we couldn’t find the page you’re looking for. It might have
          been moved, deleted, or never existed.
        </p>

        {/* CTA Actions */}
        <div className="mt-10 flex items-center justify-center gap-x-6">
          <a
            href="/"
            className="rounded-xl bg-indigo-600 px-4 py-2.5 text-sm font-semibold text-white shadow-md transition-all duration-200 hover:bg-indigo-500 hover:scale-105 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600"
          >
            Go back home
          </a>
          <a
            href="/support"
            className="text-sm font-semibold text-slate-300 hover:text-indigo-400 transition-colors duration-200"
          >
            Contact support <span aria-hidden="true">&rarr;</span>
          </a>
        </div>
      </div>
    </main>
  );
}
