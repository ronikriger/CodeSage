import React, { useState } from 'react';
import Editor from '@monaco-editor/react';
import axios from 'axios';

interface ReviewResponse {
    suggestions: string[];
    explanation: string;
    quality_score: number;
    best_practices: string[];
}

function App() {
    const [code, setCode] = useState<string>('// Write your code here...');
    const [language, setLanguage] = useState<string>('javascript');
    const [review, setReview] = useState<ReviewResponse | null>(null);
    const [loading, setLoading] = useState<boolean>(false);
    const [error, setError] = useState<string | null>(null);

    const handleEditorChange = (value: string | undefined) => {
        if (value !== undefined) {
            setCode(value);
        }
    };

    const handleReview = async () => {
        try {
            setLoading(true);
            setError(null);

            const response = await axios.post('http://localhost:8000/api/review', {
                code,
                language,
            });

            setReview(response.data);
        } catch (err) {
            setError('Failed to get code review. Please try again.');
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-gray-100">
            <nav className="bg-white shadow-lg">
                <div className="max-w-7xl mx-auto px-4 py-3">
                    <h1 className="text-2xl font-bold text-gray-800">CodeSage</h1>
                </div>
            </nav>

            <main className="max-w-7xl mx-auto px-4 py-8">
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                    {/* Code Editor Section */}
                    <div className="bg-white rounded-lg shadow-lg p-4">
                        <div className="mb-4">
                            <select
                                value={language}
                                onChange={(e) => setLanguage(e.target.value)}
                                className="px-4 py-2 border rounded-md"
                            >
                                <option value="javascript">JavaScript</option>
                                <option value="python">Python</option>
                                <option value="java">Java</option>
                                <option value="cpp">C++</option>
                            </select>
                        </div>

                        <div className="h-[600px] border rounded-lg overflow-hidden">
                            <Editor
                                height="100%"
                                defaultLanguage={language}
                                defaultValue={code}
                                onChange={handleEditorChange}
                                theme="vs-dark"
                                options={{
                                    minimap: { enabled: false },
                                    fontSize: 14,
                                }}
                            />
                        </div>

                        <button
                            onClick={handleReview}
                            disabled={loading}
                            className="mt-4 w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 transition-colors disabled:bg-blue-400"
                        >
                            {loading ? 'Analyzing...' : 'Review Code'}
                        </button>
                    </div>

                    {/* Review Results Section */}
                    <div className="bg-white rounded-lg shadow-lg p-4">
                        <h2 className="text-xl font-semibold mb-4">Code Review Results</h2>

                        {error && (
                            <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
                                {error}
                            </div>
                        )}

                        {review && (
                            <div className="space-y-6">
                                {/* Quality Score */}
                                <div className="bg-gray-50 p-4 rounded-lg">
                                    <h3 className="font-semibold mb-2">Quality Score</h3>
                                    <div className="text-3xl font-bold text-blue-600">
                                        {review.quality_score.toFixed(1)}/100
                                    </div>
                                </div>

                                {/* Explanation */}
                                <div>
                                    <h3 className="font-semibold mb-2">Code Explanation</h3>
                                    <p className="text-gray-700">{review.explanation}</p>
                                </div>

                                {/* Suggestions */}
                                <div>
                                    <h3 className="font-semibold mb-2">Suggestions</h3>
                                    <ul className="list-disc list-inside space-y-2">
                                        {review.suggestions.map((suggestion, index) => (
                                            <li key={index} className="text-gray-700">{suggestion}</li>
                                        ))}
                                    </ul>
                                </div>

                                {/* Best Practices */}
                                <div>
                                    <h3 className="font-semibold mb-2">Best Practices</h3>
                                    <ul className="list-disc list-inside space-y-2">
                                        {review.best_practices.map((practice, index) => (
                                            <li key={index} className="text-gray-700">{practice}</li>
                                        ))}
                                    </ul>
                                </div>
                            </div>
                        )}

                        {!review && !error && (
                            <div className="text-gray-500 text-center py-8">
                                Submit your code for review to see results here
                            </div>
                        )}
                    </div>
                </div>
            </main>
        </div>
    );
}

export default App; 