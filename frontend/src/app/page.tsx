"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

export default function Home() {
  const [prompt, setPrompt] = useState("");
  const router = useRouter();

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (prompt.trim()) {
      router.push(`/search?q=${encodeURIComponent(prompt.trim())}`);
    }
  };

  const examplePrompts = [
    "Reliable Japanese car under £5k, good on fuel",
    "Family SUV, automatic, less than 50k miles",
    "First car for a new driver, cheap insurance",
    "Fast coupe under £15k, petrol, manual",
    "Electric car with at least 200 mile range",
  ];

  return (
    <main className="min-h-screen bg-gradient-to-br from-gray-950 via-gray-900 to-gray-950 flex flex-col items-center justify-center px-4">
      {/* Hero */}
      <div className="text-center mb-12">
        <h1 className="text-6xl font-bold text-white mb-4">
          Car<span className="text-blue-500">Prompt</span>
        </h1>
        <p className="text-xl text-gray-400 max-w-xl">
          Describe your perfect car. Our AI finds it for you.
        </p>
      </div>

      {/* Search Bar */}
      <form onSubmit={handleSearch} className="w-full max-w-2xl mb-8">
        <div className="relative">
          <input
            type="text"
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            placeholder="Describe your ideal car..."
            className="w-full px-6 py-4 text-lg bg-gray-800 text-white rounded-2xl border border-gray-700 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 outline-none transition-all placeholder-gray-500"
          />
          <button
            type="submit"
            className="absolute right-2 top-1/2 -translate-y-1/2 bg-blue-600 hover:bg-blue-500 text-white px-6 py-2 rounded-xl font-semibold transition-colors"
          >
            Search
          </button>
        </div>
      </form>

      {/* Example Prompts */}
      <div className="flex flex-wrap gap-2 max-w-2xl justify-center">
        {examplePrompts.map((example) => (
          <button
            key={example}
            onClick={() => setPrompt(example)}
            className="px-4 py-2 bg-gray-800/50 text-gray-400 rounded-full text-sm hover:bg-gray-700 hover:text-white transition-all border border-gray-700/50"
          >
            {example}
          </button>
        ))}
      </div>

      {/* Stats / Trust bar */}
      <div className="mt-16 flex gap-8 text-gray-500 text-sm">
        <span>🚗 10,000+ listings</span>
        <span>🏪 500+ garages</span>
        <span>🤖 AI-powered search</span>
      </div>
    </main>
  );
}
