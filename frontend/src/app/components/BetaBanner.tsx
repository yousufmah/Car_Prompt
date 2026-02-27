"use client";

import { useState } from "react";

export default function BetaBanner() {
  const [email, setEmail] = useState("");
  const [submitted, setSubmitted] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email.trim() || !email.includes("@")) return;

    setLoading(true);
    // In a real app, you'd send this to your backend
    // For now, just simulate a successful submission
    setTimeout(() => {
      setSubmitted(true);
      setLoading(false);
      setEmail("");
    }, 800);
  };

  return (
    <div className="fixed bottom-4 left-4 right-4 md:left-auto md:right-4 md:bottom-4 md:w-80 z-50">
      <div className="bg-gradient-to-r from-blue-900/90 to-purple-900/90 backdrop-blur-sm border border-blue-500/30 rounded-xl shadow-2xl p-4">
        <div className="flex items-start gap-3">
          <div className="flex-1">
            <div className="flex items-center gap-2 mb-2">
              <span className="px-2 py-1 bg-blue-500/20 text-blue-300 rounded text-xs font-semibold">
                BETA
              </span>
              <span className="text-sm text-gray-300">
                CarPrompt is in early access
              </span>
            </div>
            <p className="text-sm text-gray-400 mb-3">
              We're adding real car listings soon. Leave your email to get
              notified when we launch.
            </p>

            {submitted ? (
              <div className="p-3 bg-green-900/30 border border-green-700/50 rounded-lg">
                <p className="text-green-300 text-sm">
                  🎉 Thanks! We'll email you when we launch.
                </p>
              </div>
            ) : (
              <form onSubmit={handleSubmit} className="space-y-2">
                <input
                  type="email"
                  placeholder="your@email.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full px-3 py-2 bg-gray-900/70 border border-gray-700 rounded-lg text-sm text-white placeholder-gray-500 focus:border-blue-500 outline-none"
                  required
                />
                <button
                  type="submit"
                  disabled={loading}
                  className="w-full py-2 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 rounded-lg text-sm font-medium transition-colors"
                >
                  {loading ? "Sending..." : "Get notified"}
                </button>
              </form>
            )}
          </div>
          <button
            onClick={() => setSubmitted(true)}
            className="text-gray-500 hover:text-gray-300 text-lg"
            aria-label="Dismiss"
          >
            ×
          </button>
        </div>
      </div>
    </div>
  );
}