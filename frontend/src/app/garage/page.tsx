"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";

export default function GaragePage() {
  const router = useRouter();

  useEffect(() => {
    // Redirect to login for now
    router.push("/garage/login");
  }, [router]);

  return (
    <div className="min-h-screen bg-gray-950 flex items-center justify-center">
      <div className="text-center">
        <div className="inline-block animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-blue-500 mb-4"></div>
        <p className="text-gray-400">Redirecting to garage portal...</p>
      </div>
    </div>
  );
}