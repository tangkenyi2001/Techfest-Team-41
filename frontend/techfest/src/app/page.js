"use client";
import Image from "next/image";
import React, { useState } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Toggle } from '@/components/ui/toggle';
import { LoaderCircle, Share2, Info } from 'lucide-react';
// import NodeGraph from './components/NodeGraph'; // Placeholder for visualization

export default function Home() {
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [darkMode, setDarkMode] = useState(false);

  const handleCheckFact = async () => {
    setLoading(true);
    setResult(null);
    try {
      const response = await fetch('/api/factcheck', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: input }),
      });
      const data = await response.json();
      setResult(data);
    } catch (error) {
      setResult({ error: 'Unable to fetch results. Please try again later.' });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={`min-h-screen ${darkMode ? 'bg-gray-900 text-white' : 'bg-white text-gray-800'} transition-colors duration-300`}>
      <header className="p-4 flex justify-between items-center">
        <h1 className="text-3xl font-bold">Check First Leh</h1>
        <Toggle pressed={darkMode} onPressedChange={setDarkMode}>
          {darkMode ? 'Light Mode' : 'Dark Mode'}
        </Toggle>
      </header>

      <main className="flex flex-col items-center justify-center py-10 px-4">
        <div className="w-full max-w-3xl flex flex-col items-center gap-4">
          <Input
            placeholder="Enter URL, paste an article, or type a claim"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            className="text-base"
          />
          <Button onClick={handleCheckFact} disabled={loading || !input}>
            {loading ? <LoaderCircle className="animate-spin" /> : 'Check Fact'}
          </Button>
        </div>

        {result && (
          <Card className="w-full max-w-4xl mt-8 shadow-xl">
            <CardContent className="p-6">
              {result.error ? (
                <p className="text-red-500">{result.error}</p>
              ) : (
                <>
                  <div className="flex justify-between items-center mb-4">
                    <h2 className={`text-2xl font-semibold ${result.verdict === 'True' ? 'text-green-500' : result.verdict === 'False' ? 'text-red-500' : 'text-yellow-500'}`}>{result.verdict}</h2>
                    <Button variant="outline" size="icon"><Share2 /></Button>
                  </div>

                  <p className="mb-4">{result.explanation}</p>

                  {/* <NodeGraph data={result.nodeGraphData} /> */}

                  <section className="mt-6">
                    <h3 className="text-xl font-semibold mb-2">Supporting Sources</h3>
                    <ul className="list-disc pl-5">
                      {result.sources.map((source, idx) => (
                        <li key={idx}><a href={source.link} target="_blank" className="underline hover:text-blue-500">{source.title}</a></li>
                      ))}
                    </ul>
                  </section>
                </>
              )}
            </CardContent>
          </Card>
        )}
      </main>

      <footer className="p-4 text-center">
        <Button variant="ghost" className="gap-1"><Info /> How It Works</Button>
      </footer>
    </div>
  );
}
