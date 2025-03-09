"use client";
import Image from "next/image";
import React, { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle, CardFooter } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { PieChart, Pie, Cell, Legend, Tooltip, ResponsiveContainer } from "recharts";
import { Pacifico } from "next/font/google";

const pacifico = Pacifico({ subsets: ["latin"], weight: "400" });

// Custom Tabs components

const TabsList = ({ className, children, activeValue, onClick }) => (
  <div className={`flex rounded-lg bg-gray-100 dark:bg-gray-800 p-1 ${className}`}>
    {React.Children.map(children, (child) =>
      React.cloneElement(child, { activeValue, onClick })
    )}
  </div>
);

const TabsTrigger = ({ className, value, activeValue, onClick = () => {}, children }) => (
  <button
    className={`flex items-center justify-center gap-2 flex-1 py-2 px-3 text-sm rounded-md transition-colors ${
      value === activeValue
        ? "bg-white dark:bg-gray-700 text-black dark:text-white shadow"
        : "text-gray-600 dark:text-gray-200 hover:bg-gray-200 dark:hover:bg-gray-700"
    } ${className}`}
    onClick={() => onClick(value)}
  >
    {children}
  </button>
);

const TabsContent = ({ className, value, activeValue, children }) => (
  <div className={`${value === activeValue ? "block" : "hidden"} ${className}`}>
    {children}
  </div>
);

const Tabs = ({ defaultValue, value, onValueChange, className, children }) => {
  const [activeTab, setActiveTab] = useState(value || defaultValue);

  useEffect(() => {
    if (value !== undefined) {
      setActiveTab(value);
    }
  }, [value]);

  const handleTabChange = (tabValue) => {
    setActiveTab(tabValue);
    if (onValueChange) onValueChange(tabValue);
  };

  return (
    <div className={className}>
      {React.Children.map(children, (child) => {
        if (child.type === TabsList) {
          return React.cloneElement(child, { activeValue: activeTab, onClick: handleTabChange });
        }
        if (child.type === TabsContent) {
          return React.cloneElement(child, { activeValue: activeTab });
        }
        return React.cloneElement(child, { activeValue: activeTab, onClick: handleTabChange });
      })}
    </div>
  );
};

// Simple custom Alert components

const Alert = ({ className, children }) => (
  <div className={`rounded-lg border p-4 ${className}`}>{children}</div>
);

const AlertDescription = ({ children }) => <div className="text-sm">{children}</div>;

export default function Home() {
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [darkMode, setDarkMode] = useState(true);
  const [showInfo, setShowInfo] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const [analysis, setAnalysis] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [imagePreview, setImagePreview] = useState(null);
  const [activeTab, setActiveTab] = useState("text");
  const [showTips, setShowTips] = useState(false);

  const telegramBotUrl = "https://t.me/FakeOrNotBot";

  const fakeNewsData = [
    { name: "Social Media", value: 45 },
    { name: "Messaging Apps", value: 30 },
    { name: "Online Forums", value: 15 },
    { name: "Others", value: 10 },
  ];

  const COLORS = ["#ff6384", "#ffcd56", "#36a2eb", "#4bc0c0"];

  // Toggle dark/light mode
  const toggleTheme = () => {
    setDarkMode((prev) => !prev);
  };

  // Apply theme to body element
  useEffect(() => {
    document.body.className = darkMode ? "bg-gray-900" : "bg-gray-50";
  }, [darkMode]);

  const handleCheckFact = async () => {
    if (!input.trim()) return;
    setLoading(true);
    setResult(null);
    try {
      const response = await fetch("http://localhost:8000/rag", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: input }),
      });
      const data = await response.json();
      setResult(data);
    } catch (error) {
      setResult({ error: "Unable to fetch results. Please try again later." });
    } finally {
      setLoading(false);
    }
  };

  const handleFileChange = (event) => {
    const file = event.target.files[0];
    setSelectedFile(file);
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
    setAnalysis("");
    try {
      const formData = new FormData();
      formData.append("file", selectedFile);
      const response = await fetch("http://localhost:8000/image", {
        method: "POST",
        body: formData,
      });
      if (response.ok) {
        const data = await response.json();
        setAnalysis(data.type.ai_generated);
      } else {
        console.error("Error analyzing image");
      }
    } catch (error) {
      console.error("Error:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const getVerdictIcon = (verdict) => {
    if (verdict === "True")
      return (
        <svg className="h-6 w-6 text-green-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      );
    if (verdict === "False")
      return (
        <svg className="h-6 w-6 text-red-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      );
    return (
      <svg className="h-6 w-6 text-yellow-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
      </svg>
    );
  };

  const getVerdictColor = (verdict) => {
    if (verdict === "True") return "text-green-500";
    if (verdict === "False") return "text-red-500";
    return "text-yellow-500";
  };

  const Icons = {
    LoaderCircle: () => (
      <svg className="h-4 w-4 animate-spin" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
      </svg>
    ),
    Link: () => (
      <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
      </svg>
    ),
    Upload: () => (
      <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
      </svg>
    ),
    Share2: () => (
      <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.368 2.684 3 3 0 00-5.368-2.684z" />
      </svg>
    ),
    Info: () => (
      <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
    ),
    ExternalLink: () => (
      <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
      </svg>
    ),
    Sun: () => (
      <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
      </svg>
    ),
    MoonStar: () => (
      <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
      </svg>
    ),
    AlertTriangle: () => (
      <svg className="h-6 w-6 text-yellow-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
      </svg>
    ),
  };

  return (
    <div className={`min-h-screen ${darkMode ? "bg-gray-900 text-gray-100" : "bg-gray-50 text-gray-800"} transition-colors duration-300`}>
      {/* Singaporean-Themed Header */}
      <header
        className={`relative p-6 flex flex-col items-center shadow-md ${
          darkMode ? "bg-red-800 text-gray-100" : "bg-red-600 text-gray-50"
        }`}
      >
        <Button
          variant="ghost"
          onClick={toggleTheme}
          className="absolute right-4 top-4 text-gray-100 hover:bg-red-700 p-2 rounded-full"
        >
          {darkMode ? <Icons.Sun /> : <Icons.MoonStar />}
        </Button>
        {/* Using Pacifico font for a cursive, bubbly look */}
        <h1 className={`${pacifico.className} text-5xl tracking-wide animate-fade-in`}>
          CheckFirstLeh
        </h1>
        <p className="text-sm font-medium italic">Don't spread fake news!</p>
      </header>

      <main className="container mx-auto flex flex-col items-center justify-center py-10 px-4 max-w-5xl">
        <div className="w-full flex flex-col items-center justify-center animate-slide-up">
          <Image src="/giphy.gif" width={150} height={150} alt="Mascot" className="mb-4 mx-auto" priority />
          {/* Main Card with Tabs */}
          <Card className={`w-full max-w-3xl shadow-xl ${darkMode ? "bg-gray-800 border-gray-700" : "bg-white border-gray-200"}`}>
            <CardHeader className="text-center pb-2">
              <CardTitle className={darkMode ? "text-gray-100" : "text-gray-800"}>Fact Check Your Information</CardTitle>
            </CardHeader>
            <CardContent>
              <Tabs defaultValue="text" value={activeTab} onValueChange={setActiveTab} className="w-full">
                <TabsList className="grid w-full grid-cols-2 mb-6">
                  <TabsTrigger value="text" activeValue={activeTab}>
                    <Icons.Link /> Text/URL
                  </TabsTrigger>
                  <TabsTrigger value="image" activeValue={activeTab}>
                    <Icons.Upload /> Image
                  </TabsTrigger>
                </TabsList>
                <TabsContent value="text" activeValue={activeTab} className="mt-0">
                  <div className="flex flex-col gap-4">
                    <div className="relative">
                      <Input
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        placeholder="Paste URL, news article, or enter a claim"
                        className="w-full pr-24"
                      />
                      <Button
                        className="absolute right-0 top-0 h-full rounded-l-none"
                        onClick={handleCheckFact}
                        disabled={loading || !input.trim()}
                      >
                        {loading && <Icons.LoaderCircle />} Verify
                      </Button>
                    </div>
                    <div className="flex justify-between items-center">
                      <Button variant="outline" onClick={() => setShowTips(!showTips)} className="text-xs px-3 py-1">
                        <Icons.Info /> Tips
                      </Button>
                      <a
                        href={telegramBotUrl}
                        target="_blank"
                        rel="noopener noreferrer"
                        className={`${darkMode ? "text-gray-100" : "text-gray-800"} text-xs flex items-center`}
                      >
                        Use our Telegram bot <Icons.ExternalLink />
                      </a>
                    </div>
                    {showTips && (
                      <Alert className={`mt-2 ${darkMode ? "bg-gray-700" : "bg-gray-100"}`}>
                        <AlertDescription>
                          For best results, paste complete article text or provide a direct link to the news source.
                        </AlertDescription>
                      </Alert>
                    )}
                    
                    {/* Display Results Section - Added this section to display the verification results */}
                    {result && (
                      <div className={`mt-6 p-6 rounded-lg border ${darkMode ? "bg-gray-700 border-gray-600" : "bg-gray-50 border-gray-200"}`}>
                        <div className="flex items-center gap-3 mb-4">
                          {result.verdict && getVerdictIcon(result.verdict)}
                          <h3 className={`text-xl font-semibold ${result.verdict && getVerdictColor(result.verdict)}`}>
                            {result.verdict ? `Verdict: ${result.verdict}` : "Verification Results"}
                          </h3>
                        </div>
                        
                        {result.error ? (
                          <p className="text-red-500">{result.error}</p>
                        ) : (
                          <>
                            {result.summary && (
                              <div className="mb-4">
                                <h4 className="font-medium mb-2">Summary</h4>
                                <p className="text-sm">{result.summary}</p>
                              </div>
                            )}
                            
                            {result.evidence && (
                              <div className="mb-4">
                                <h4 className="font-medium mb-2">Evidence</h4>
                                <p className="text-sm">{result.evidence}</p>
                              </div>
                            )}
                            
                            {result.sources && result.sources.length > 0 && (
                              <div>
                                <h4 className="font-medium mb-2">Sources</h4>
                                <ul className="text-sm space-y-1">
                                  {result.sources.map((source, idx) => (
                                    <li key={idx} className="flex items-center gap-1">
                                      <Icons.ExternalLink />
                                      <a 
                                        href={source.url} 
                                        target="_blank" 
                                        rel="noopener noreferrer"
                                        className="hover:underline text-blue-400"
                                      >
                                        {source.title || source.url}
                                      </a>
                                    </li>
                                  ))}
                                </ul>
                              </div>
                            )}
                          </>
                        )}
                      </div>
                    )}
                  </div>
                </TabsContent>
                <TabsContent value="image" activeValue={activeTab} className="mt-0">
                  <form onSubmit={handleSubmit} className="flex flex-col gap-4">
                    <div className="border-2 border-dashed rounded-lg p-4 text-center cursor-pointer hover:bg-opacity-10 hover:bg-blue-500 transition-colors">
                      <input type="file" accept="image/*" onChange={handleFileChange} className="hidden" id="image-upload" />
                      <label htmlFor="image-upload" className="cursor-pointer block">
                        {imagePreview ? (
                          <div className="relative">
                            <img src={imagePreview} alt="Preview" className="max-h-[200px] mx-auto object-contain rounded" />
                            <p className="mt-2 text-sm">Click to change image</p>
                          </div>
                        ) : (
                          <div className="py-8">
                            <Icons.Upload />
                            <p>Click to upload an image</p>
                            <p className="text-xs mt-1 opacity-70">JPG, PNG, GIF up to 5MB</p>
                          </div>
                        )}
                      </label>
                    </div>
                    <Button type="submit" disabled={!selectedFile || isLoading} className="w-full">
                      {isLoading ? (
                        <>
                          <Icons.LoaderCircle /> Analyzing...
                        </>
                      ) : (
                        "Verify Image"
                      )}
                    </Button>
                    {analysis && (
                      <Alert className={`mt-2 ${darkMode ? "bg-gray-700" : "bg-gray-100"}`}>
                        <AlertDescription>
                          <strong>AI Detection Score:</strong> {analysis}
                        </AlertDescription>
                      </Alert>
                    )}
                  </form>
                </TabsContent>
              </Tabs>
            </CardContent>
          </Card>
        </div>

        {/* Statistics Section */}
        <section className="w-full max-w-3xl mt-12 animate-slide-up">
          <Card className={`${darkMode ? "bg-gray-800 border-gray-700" : "bg-white border-gray-200"}`}>
            <CardHeader>
              <CardTitle className={darkMode ? "text-gray-100" : "text-gray-800"}>
                Misinformation Distribution in Singapore
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className={`mb-6 opacity-80 ${darkMode ? "text-gray-100" : "text-gray-800"}`}>
                Fake news continues to significantly impact Singapore's public discourse, political stability, and societal harmony. The chart below illustrates the distribution of misinformation sources:
              </p>
              {/* Pie Chart */}
              <div className="w-full h-64 mb-4">
                <ResponsiveContainer>
                  <PieChart>
                    <Pie data={fakeNewsData} dataKey="value" cx="50%" cy="50%" outerRadius={80} label>
                      {fakeNewsData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip contentStyle={{ backgroundColor: darkMode ? "#374151" : "#ffffff", border: "none" }} />
                    <Legend verticalAlign="bottom" height={36} wrapperStyle={{ color: darkMode ? "#ffffff" : "#000000" }} />
                  </PieChart>
                </ResponsiveContainer>
              </div>
              {/* Fake News Sources Grid */}
              <div className="h-80">
                <div className="w-full h-full flex justify-center items-center">
                  <div className="text-center p-8 bg-gray-100 dark:bg-gray-700 rounded-lg">
                    <h4 className="text-lg font-medium mb-2">Fake News Sources</h4>
                    <div className="grid grid-cols-2 gap-4">
                      {fakeNewsData.map((item, index) => (
                        <div key={index} className="flex items-center gap-2">
                          <div className="w-4 h-4 rounded-full" style={{ backgroundColor: COLORS[index % COLORS.length] }}></div>
                          <span>{item.name}: {item.value}%</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </section>

        {/* About Section */}
        <section className="w-full max-w-3xl mt-8 mb-12 animate-slide-up">
          <Card className={`${darkMode ? "bg-gray-800 border-gray-700" : "bg-white border-gray-200"}`}>
            <CardHeader>
              <CardTitle className={darkMode ? "text-gray-100" : "text-gray-800"}>What We Do</CardTitle>
            </CardHeader>
            <CardContent>
              <p className={`leading-relaxed ${darkMode ? "text-gray-100" : "text-gray-800"}`}>
                At <strong>CheckFirstLeh</strong>, we collaborate closely with elderly community centers to combat misinformation effectively. Our service gathers and analyzes trending fake news flagged by our intelligent bots and extensive online research. Verified data and insights are then packaged and shared with NGO-operated community centers, which further relay this crucial information to local communities. Together, we empower citizens, particularly seniors, to make informed decisions and confidently navigate digital spaces.
              </p>
            </CardContent>
            <CardFooter className="flex justify-center border-t pt-4">
              <Button variant="outline" className="gap-2" onClick={() => setShowInfo(!showInfo)}>
                <Icons.Info /> How It Works
              </Button>
              {showInfo && (
                <div className={`absolute bottom-full mb-2 p-4 rounded-lg shadow-lg z-10 max-w-md ${
                  darkMode ? "bg-gray-700 border-gray-600" : "bg-white border-gray-200"
                } border animate-fade-in`}>
                  <p className="text-sm leading-relaxed">
                    <strong>CheckFirstLeh</strong> leverages advanced AI algorithms to analyze and validate your inputs by systematically scanning and cross-referencing information from trusted online sources. The summarized insights and visualizations clearly communicate the authenticity and context of claims to empower informed sharing.
                  </p>
                </div>
              )}
            </CardFooter>
          </Card>
        </section>
      </main>

      <footer className={`py-6 text-center ${darkMode ? "bg-gray-900 text-gray-300" : "bg-gray-50 text-gray-600"}`}>
        <div className="container mx-auto px-4">
          <p className="text-sm">© 2025 CheckFirstLeh. All rights reserved.</p>
          <a
            href={telegramBotUrl}
            target="_blank"
            rel="noopener noreferrer"
            className={`inline-flex items-center ${darkMode ? "text-gray-100" : "text-gray-800"} text-sm mt-2 hover:underline`}
          >
            <span>Add our bot to your chats</span>
            <Icons.ExternalLink />
          </a>
        </div>
      </footer>

      <style jsx global>{`
        .animate-fade-in {
          animation: fadeIn 0.5s ease-in-out;
        }
        .animate-slide-up {
          animation: slideUp 0.5s ease-in-out;
        }
        @keyframes fadeIn {
          from { opacity: 0; }
          to { opacity: 1; }
        }
        @keyframes slideUp {
          from { opacity: 0; transform: translateY(20px); }
          to { opacity: 1; transform: translateY(0); }
        }
      `}</style>
    </div>
  );
}