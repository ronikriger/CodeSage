import { useState, useCallback } from 'react';
import axios from 'axios';

interface AnalysisResult {
    suggestions: string[];
    explanation: string;
    quality_score: number;
    best_practices: string[];
}

export const useCodeAnalysis = () => {
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [result, setResult] = useState<AnalysisResult | null>(null);

    const analyzeCode = useCallback(async (code: string, language: string) => {
        try {
            setLoading(true);
            setError(null);

            const response = await axios.post('http://localhost:8000/api/review', {
                code,
                language,
            });

            setResult(response.data);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'An error occurred');
        } finally {
            setLoading(false);
        }
    }, []);

    return {
        loading,
        error,
        result,
        analyzeCode,
    };
}; 