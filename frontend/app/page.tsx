'use client';

import { useState, useEffect } from 'react';
import { apiRequest } from '@/lib/api';

// Define the response type from the hello endpoint
interface HelloResponse {
  message: string;
  status: string;
}

export default function Home() {
  const [apiResponse, setApiResponse] = useState<HelloResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const data = await apiRequest<HelloResponse>('hello');
        setApiResponse(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'An unknown error occurred');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  return (
    <div className="grid grid-rows-[20px_1fr_20px] items-center justify-items-center min-h-screen p-8 pb-20 gap-16 sm:p-20 font-[family-name:var(--font-geist-sans)]">
      <main className="flex flex-col gap-8 row-start-2 items-center sm:items-start">
        <h1 className="text-2xl font-bold">API Test</h1>
        
        {loading && <p>Loading...</p>}
        
        {error && (
          <div className="p-4 bg-red-50 border border-red-200 rounded-md text-red-700">
            <p>Error: {error}</p>
            <p className="text-sm mt-2">
              Make sure your backend is running at {process.env.NEXT_PUBLIC_API_URL}
            </p>
          </div>
        )}
        
        {apiResponse && (
          <div className="p-6 bg-gray-50 border border-gray-200 rounded-md">
            <h2 className="text-xl mb-4">Response from API:</h2>
            <pre className="bg-gray-100 p-4 rounded font-mono">
              {JSON.stringify(apiResponse, null, 2)}
            </pre>
            <p className="mt-4 text-green-600">
              Status: {apiResponse.status}
            </p>
          </div>
        )}
      </main>
      <footer className="row-start-3 flex gap-6 flex-wrap items-center justify-center text-sm text-gray-500">
        Frontend ↔️ Backend Connection Test
      </footer>
    </div>
  );
}
