"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";

interface CarListing {
  id: number;
  title: string;
  description: string | null;
  make: string;
  model: string;
  variant: string | null;
  year: number;
  price: number;
  mileage: number | null;
  fuel_type: string | null;
  transmission: string | null;
  body_type: string | null;
  doors: number | null;
  colour: string | null;
  engine_size: number | null;
  location: string | null;
  postcode: string | null;
  images: string | null;
  garage_id: number | null;
  created_at: string;
}

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function ListingPage() {
  const { id } = useParams();
  const [car, setCar] = useState<CarListing | null>(null);
  const [loading, setLoading] = useState(true);
  const [notFound, setNotFound] = useState(false);

  useEffect(() => {
    fetch(`${API_URL}/api/listings/${id}`)
      .then((res) => {
        if (res.status === 404) {
          setNotFound(true);
          setLoading(false);
          return null;
        }
        return res.json();
      })
      .then((data) => {
        if (data) {
          setCar(data);
          setLoading(false);
        }
      })
      .catch(() => {
        setLoading(false);
      });
  }, [id]);

  const specs = car
    ? [
        { label: "Year", value: car.year },
        { label: "Mileage", value: car.mileage ? `${car.mileage.toLocaleString()} miles` : null },
        { label: "Fuel Type", value: car.fuel_type },
        { label: "Transmission", value: car.transmission },
        { label: "Body Type", value: car.body_type },
        { label: "Doors", value: car.doors },
        { label: "Colour", value: car.colour },
        { label: "Engine Size", value: car.engine_size ? `${car.engine_size}L` : null },
      ].filter((s) => s.value !== null && s.value !== undefined)
    : [];

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-950 flex items-center justify-center">
        <div className="animate-spin w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full" />
      </div>
    );
  }

  if (notFound || !car) {
    return (
      <div className="min-h-screen bg-gray-950 text-white flex flex-col items-center justify-center gap-4">
        <p className="text-2xl">🚗 Listing not found</p>
        <Link href="/" className="text-blue-400 hover:underline">
          Back to search
        </Link>
      </div>
    );
  }

  return (
    <main className="min-h-screen bg-gray-950 text-white">
      {/* Header */}
      <header className="border-b border-gray-800 px-6 py-4">
        <div className="max-w-5xl mx-auto flex items-center gap-4">
          <Link href="/" className="text-2xl font-bold">
            Car<span className="text-blue-500">Prompt</span>
          </Link>
        </div>
      </header>

      <div className="max-w-5xl mx-auto px-6 py-8">
        {/* Back */}
        <button
          onClick={() => window.history.back()}
          className="text-gray-400 hover:text-white text-sm mb-6 flex items-center gap-1 transition-colors"
        >
          ← Back to results
        </button>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Left: Image */}
          <div>
            <div className="bg-gray-900 rounded-2xl h-72 flex items-center justify-center text-7xl border border-gray-800">
              🚗
            </div>
          </div>

          {/* Right: Details */}
          <div>
            <h1 className="text-3xl font-bold mb-2">{car.title}</h1>
            <p className="text-4xl font-bold text-blue-400 mb-4">
              £{car.price.toLocaleString()}
            </p>

            {car.location && (
              <p className="text-gray-400 text-sm mb-6">📍 {car.location}</p>
            )}

            {/* Specs grid */}
            <div className="grid grid-cols-2 gap-3 mb-6">
              {specs.map((spec) => (
                <div
                  key={spec.label}
                  className="bg-gray-900 rounded-xl p-3 border border-gray-800"
                >
                  <p className="text-xs text-gray-500 mb-1">{spec.label}</p>
                  <p className="font-semibold capitalize">{String(spec.value)}</p>
                </div>
              ))}
            </div>

            {/* Contact button */}
            <button className="w-full bg-blue-600 hover:bg-blue-500 text-white py-3 rounded-xl font-semibold text-lg transition-colors">
              Contact Seller
            </button>
          </div>
        </div>

        {/* Description */}
        {car.description && (
          <div className="mt-8 bg-gray-900 rounded-2xl p-6 border border-gray-800">
            <h2 className="text-lg font-semibold mb-3">Description</h2>
            <p className="text-gray-300 leading-relaxed whitespace-pre-wrap">{car.description}</p>
          </div>
        )}
      </div>
    </main>
  );
}
