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
  const [darkMode, setDarkMode] = useState(true);
  const [showInfo, setShowInfo] = useState(false);

  const handleCheckFact = async () => {
    setLoading(true);
    setResult(null);
    try {
      const response = await fetch('/api/factcheck', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: input, url: ["https://example.com"] }), // Replace with actual sources
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
        <Toggle pressed={darkMode} onPressedChange={setDarkMode}>
          {darkMode ? 'Light Mode' : 'Dark Mode'}
        </Toggle>
      </header>

      <main className="flex flex-col items-center justify-center py-10 px-4">
        <div className="w-full max-w-3xl flex flex-col items-center justify-center py-10 px-4">
          <Image
            src="/giphy.gif"
            width={150}
            height={150}
            alt="Mascot"
            className="mb-4 mx-auto"
          />
          
          <div className="w-full flex flex-col items-center gap-4">
            <Input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Paste URL, news article, or enter a claim"
              className="max-w-3xl"
            />
            <Button onClick={handleCheckFact} disabled={loading || !input}>
              {loading ? <LoaderCircle className="animate-spin" /> : 'Check Fact'}
            </Button>
          </div>
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

      <footer className="p-4 text-center relative">
      <div
        onMouseEnter={() => setShowInfo(true)}
        onMouseLeave={() => setShowInfo(false)}
        className="inline-block relative"
      >
        <Button variant="ghost" className="gap-1">
          <Info /> How It Works
        </Button>

        {showInfo && (
          <Card className="absolute top-full left-1/2 transform -translate-x-1/2 mt-2 w-80 shadow-lg">
            <CardContent className="text-sm p-4">
              <p>
                <strong>CheckFirstLeh</strong> leverages advanced AI algorithms by crawling the web to validate your input, cross-referencing findings against multiple reputable and trustworthy sources. It then clearly summarizes and visualizes the results to help you understand the reliability and context of the claim.
              </p>
            </CardContent>
          </Card>
        )}
      </div>
    </footer>
    </div>
  );
}
