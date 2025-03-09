"use client";
import Image from "next/image";
import React, { useState } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Toggle } from '@/components/ui/toggle';
import { LoaderCircle, Share2, Info } from 'lucide-react';
import { PieChart, Pie, Cell, Legend, Tooltip, ResponsiveContainer } from 'recharts';

// import NodeGraph from './components/NodeGraph'; // Placeholder for visualization

export default function Home() {
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [darkMode, setDarkMode] = useState(true);
  const [showInfo, setShowInfo] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const [analysis, setAnalysis] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [imagePreview, setImagePreview] = useState(null);

  const fakeNewsData = [
    { name: 'Social Media', value: 45 },
    { name: 'Messaging Apps', value: 30 },
    { name: 'Online Forums', value: 15 },
    { name: 'Others', value: 10 },
  ];
  
  const COLORS = ['#ff6384', '#ffcd56', '#36a2eb', '#4bc0c0'];

  const handleCheckFact = async () => {
    setLoading(true);
    setResult(null);
    try {
      const response = await fetch('http://localhost:8000/rag', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({"message":input}), // Replace with actual sources
      });
      const data = await response.json();
      setResult(data);
      console.log(data)
    } catch (error) {
      setResult({ error: 'Unable to fetch results. Please try again later.' });
    } finally {
      setLoading(false);
    }
  };
  const handleFileChange = (event) => {
    const file = event.target.files[0];
    setSelectedFile(file);
    
    // Create a preview URL for the selected image
    if (file) {
      const reader = new FileReader();
      reader.onloadend = () => {
        setImagePreview(reader.result);
      };
      reader.readAsDataURL(file);
    } else {
      setImagePreview(null);
    }
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    if (!selectedFile) return;
    
    setIsLoading(true);
    
    try {
      // Create FormData for your Python backend
      const formData = new FormData();
      formData.append('file', selectedFile);
      
      // Send to Python backend
      const response = await fetch('http://localhost:8000/image', {
        method: 'POST',
        body: formData,
      });
      
      if (response.ok) {
        const data = await response.json();
        setAnalysis(data.type.ai_generated);
      } else {
        console.error('Error analyzing image');
      }
    } catch (error) {
      console.error('Error:', error);
    } finally {
      setIsLoading(false);
    }
  };
  return (
    <div className={`min-h-screen ${darkMode ? 'bg-gray-900 text-white' : 'bg-white text-gray-800'} transition-colors duration-300`}>
      <header className="p-4 flex justify-between items-center">

      </header>

      <main className="flex flex-col items-center justify-center py-10 px-4">
      <div className="w-full max-w-4xl flex flex-col items-center justify-center py-10 px-4">
  <Image
    src="/giphy.gif"
    width={150}
    height={150}
    alt="Mascot"
    className="mb-4 mx-auto"
  />
  
  {/* Side by side container */}
  <div className="w-full flex flex-col md:flex-row items-center gap-4">
    {/* Left side - URL/Text input */}
    <div className="w-full md:w-1/2">
      <div className="flex flex-col gap-2">
        <Input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Paste URL, news article, enter a claim"
          className="w-full"
        />
        <Button onClick={handleCheckFact} disabled={loading || !input} className="w-full">
          {loading ? <LoaderCircle className="animate-spin" /> : 'Check Fact'}
        </Button>
      </div>
    </div>
    
    {/* Right side - File upload */}
    <div className="w-full md:w-1/2">
      <form 
        onSubmit={handleSubmit} 
        className="flex flex-col gap-2"
      >
        <div className="flex items-center w-full">
          <input 
            type="file" 
            accept="image/*" 
            onChange={handleFileChange}
            className="w-full p-1.5 text-sm file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:bg-blue-500 file:text-white hover:file:bg-blue-600"
          />
        </div>
        <Button 
          type="submit" 
          disabled={!selectedFile || isLoading}
          className="w-full"
        >
          {isLoading ? 'Analyzing...' : 'Analyze Image'}
        </Button>
      </form>
    </div>
  </div>
</div>

{/* Image preview and analysis section - kept below */}
<div className="w-full max-w-4xl mt-4">
  <div className="flex flex-col md:flex-row gap-6">
    {imagePreview && (
      <div className="w-full md:w-1/2 text-center">
        <h3 className="text-lg font-medium mb-2">Image Preview:</h3>
        <img 
          src={imagePreview} 
          alt="Preview" 
          className="max-w-full max-h-[300px] object-contain border border-gray-300 dark:border-gray-700 rounded-md p-1 mx-auto" 
        />
      </div>
    )}
    
    {analysis && (
      <div className="w-full md:w-1/2 text-center">
        <h3 className="text-lg font-medium mb-2">AI Detection Score:</h3>
        <p>{analysis}</p>
      </div>
    )}
  </div>
</div>
        {result && (
        <Card className="w-full max-w-4xl mt-8 shadow-xl bg-gray-800 border border-gray-700 text-white mx-auto">
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
              </>
            )}
          </CardContent>
        </Card>
      )}

      {result && !result.error && result.sources && (
        <section className="mt-12 max-w-4xl mx-auto">
          <h3 className="text-2xl font-bold mb-4 text-white">Supporting Sources</h3>
          <div className="flex flex-wrap justify-center gap-4">
            {result.sources.map((source, idx) => (
              <a
                key={idx}
                href={source}
                target="_blank"
                rel="noopener noreferrer"
                className="w-56 bg-gray-800 shadow-lg rounded-lg border border-gray-700 p-4 hover:bg-gray-700 transition transform hover:scale-105"
              >
                <h4 className="text-lg font-semibold text-white">Source {idx + 1}</h4>
                <p className="text-sm text-gray-400 mt-2 break-words">{source}</p>
              </a>
            ))}
          </div>
        </section>
      )}
    <footer className="p-6 text-center relative bg-gray-900">
      <div
        onMouseEnter={() => setShowInfo(true)}
        onMouseLeave={() => setShowInfo(false)}
        className="inline-block relative"
      >
        <Button variant="outline" className="gap-2 shadow-md hover:bg-gray-800 border-gray-700 text-black transition">
          <Info /> How It Works
        </Button>

        {showInfo && (
          <Card className="absolute top-full left-1/2 transform -translate-x-1/2 mt-3 w-96 shadow-xl border border-gray-700 bg-gray-800 text-white">
            <CardContent className="text-sm p-5">
              <p className="leading-relaxed">
                <strong>CheckFirstLeh</strong> leverages advanced AI algorithms to analyze and validate your inputs by systematically scanning and cross-referencing information from trusted online sources. The summarized insights and visualizations clearly communicate the authenticity and context of claims to empower informed sharing.
              </p>
            </CardContent>
          </Card>
        )}
      </div>

      <section className="mt-12 max-w-4xl mx-auto bg-gray-800 shadow-xl rounded-xl p-8">
        <h3 className="text-2xl font-bold mb-3 text-white">Severity of Fake News in Singapore</h3>
        <p className="mb-6 text-gray-300 font-medium leading-relaxed">
          Fake news continues to significantly impact Singapore's public discourse, political stability, and societal harmony. The pie chart below illustrates the distribution of misinformation sources affecting Singaporeans:
        </p>
        <ResponsiveContainer width="100%" height={320}>
          <PieChart>
            <Pie
              data={fakeNewsData}
              cx="50%"
              cy="50%"
              labelLine={false}
              label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
              outerRadius={110}
              innerRadius={60}
              dataKey="value"
            >
              {fakeNewsData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
              ))}
            </Pie>
            <Tooltip contentStyle={{ backgroundColor: '#374151', border: 'none' }} />
            <Legend verticalAlign="bottom" height={36} wrapperStyle={{ color: '#fff' }} />
          </PieChart>
        </ResponsiveContainer>
      </section>
    </footer>
    <section className="mt-12 max-w-4xl mx-auto bg-gray-800 shadow-lg rounded-xl p-8">
        <h3 className="text-2xl font-bold mb-3 text-white">What We Do</h3>
        <p className="text-gray-300 font-medium leading-relaxed">
          At <strong>CheckFirstLeh</strong>, we collaborate closely with elderly community centers to combat misinformation effectively. Our service gathers and analyzes trending fake news flagged by our intelligent bots and extensive online research. Verified data and insights are then packaged and shared with NGO-operated community centers, which further relay this crucial information to local communities. Together, we empower citizens, particularly seniors, to make informed decisions and confidently navigate digital spaces.
        </p>
      </section>
      </main>
    </div>
  );
}