"use client";

import { useSearchParams } from "next/navigation";
import { useState, useEffect, Suspense } from "react";
import Link from "next/link";

interface CarResult {
  id: number;
  title: string;
  make: string;
  model: string;
  year: number;
  price: number;
  mileage: number | null;
  fuel_type: string | null;
  transmission: string | null;
  body_type: string | null;
  location: string | null;
  images: string | null;
}

interface SearchResponse {
  prompt: string;
  filters: Record<string, unknown>;
  results: CarResult[];
  count: number;
}

function SearchContent() {
  const searchParams = useSearchParams();
  const query = searchParams.get("q") || "";
  const [results, setResults] = useState<SearchResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [newPrompt, setNewPrompt] = useState(query);

  useEffect(() => {
    if (query) {
      setLoading(true);
      fetch(`${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/search/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt: query }),
      })
        .then((res) => res.json())
        .then((data) => {
          setResults(data);
          setLoading(false);
        })
        .catch(() => {
          setLoading(false);
        });
    }
  }, [query]);

  return (
    <main className="min-h-screen bg-gray-950 text-white">
      {/* Header */}
      <header className="border-b border-gray-800 px-6 py-4">
        <div className="max-w-6xl mx-auto flex items-center gap-4">
          <Link href="/" className="text-2xl font-bold">
            Car<span className="text-blue-500">Prompt</span>
          </Link>
          <form
            onSubmit={(e) => {
              e.preventDefault();
              if (newPrompt.trim()) {
                window.location.href = `/search?q=${encodeURIComponent(newPrompt.trim())}`;
              }
            }}
            className="flex-1"
          >
            <input
              type="text"
              value={newPrompt}
              onChange={(e) => setNewPrompt(e.target.value)}
              className="w-full px-4 py-2 bg-gray-800 rounded-xl border border-gray-700 focus:border-blue-500 outline-none text-sm"
              placeholder="Refine your search..."
            />
          </form>
        </div>
      </header>

      <div className="max-w-6xl mx-auto px-6 py-8">
        {/* What the AI understood */}
        {results?.filters && (
          <div className="mb-6 p-4 bg-gray-900 rounded-xl border border-gray-800">
            <p className="text-sm text-gray-400 mb-2">🤖 I understood:</p>
            <div className="flex flex-wrap gap-2">
              {Object.entries(results.filters).map(([key, value]) => (
                <span
                  key={key}
                  className="px-3 py-1 bg-blue-500/10 text-blue-400 rounded-full text-xs"
                >
                  {key}: {JSON.stringify(value)}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Results */}
        {loading ? (
          <div className="text-center py-20">
            <div className="animate-spin w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full mx-auto mb-4" />
            <p className="text-gray-400">Searching for your perfect car...</p>
          </div>
        ) : results?.results.length === 0 ? (
          <div className="text-center py-20">
            <p className="text-2xl mb-2">😢 No matches found</p>
            <p className="text-gray-400">Try adjusting your search</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {results?.results.map((car) => (
              <Link
                key={car.id}
                href={`/listing/${car.id}`}
                className="bg-gray-900 rounded-xl border border-gray-800 overflow-hidden hover:border-blue-500 transition-colors block"
              >
                {/* Placeholder image */}
                <div className="h-48 bg-gray-800 flex items-center justify-center text-4xl">
                  🚗
                </div>
                <div className="p-4">
                  <h3 className="font-semibold text-lg">{car.title}</h3>
                  <p className="text-2xl font-bold text-blue-400 mt-1">
                    £{car.price.toLocaleString()}
                  </p>
                  <div className="flex flex-wrap gap-2 mt-3 text-xs text-gray-400">
                    <span className="px-2 py-1 bg-gray-800 rounded">{car.year}</span>
                    {car.mileage && (
                      <span className="px-2 py-1 bg-gray-800 rounded">
                        {car.mileage.toLocaleString()} mi
                      </span>
                    )}
                    {car.fuel_type && (
                      <span className="px-2 py-1 bg-gray-800 rounded">{car.fuel_type}</span>
                    )}
                    {car.transmission && (
                      <span className="px-2 py-1 bg-gray-800 rounded">{car.transmission}</span>
                    )}
                  </div>
                  {car.location && (
                    <p className="text-xs text-gray-500 mt-2">📍 {car.location}</p>
                  )}
                </div>
              </Link>
            ))}
          </div>
        )}
      </div>
    </main>
  );
}

export default function SearchPage() {
  return (
    <Suspense fallback={<div className="min-h-screen bg-gray-950" />}>
      <SearchContent />
    </Suspense>
  );
}
