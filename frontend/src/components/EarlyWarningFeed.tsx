import React, { useEffect, useState } from 'react';
import { fetchNews, type NewsArticle } from '../lib/api';
import { AlertCircle, ExternalLink, Newspaper, Zap } from 'lucide-react';

interface EarlyWarningFeedProps {
    disease?: string;
}

const EarlyWarningFeed: React.FC<EarlyWarningFeedProps> = ({ disease }) => {
    const [articles, setArticles] = useState<NewsArticle[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const loadNews = async () => {
            try {
                setLoading(true);
                const response = await fetchNews(disease);
                setArticles(response.articles);
                setError(null);
            } catch (err) {
                console.error('Failed to fetch news:', err);
                setError('Failed to load early warning signals.');
            } finally {
                setLoading(false);
            }
        };

        loadNews();
    }, [disease]);

    if (loading) {
        return (
            <div className="bg-[#1e293b] rounded-xl p-6 border border-slate-700 animate-pulse">
                <div className="h-6 w-48 bg-slate-700 rounded mb-4"></div>
                <div className="space-y-4">
                    {[1, 2, 3].map((i) => (
                        <div key={i} className="h-20 bg-slate-800 rounded"></div>
                    ))}
                </div>
            </div>
        );
    }

    return (
        <div className="bg-[#1e293b] rounded-xl border border-slate-700 overflow-hidden flex flex-col h-full">
            <div className="p-4 border-b border-slate-700 bg-slate-800/50 flex justify-between items-center">
                <div className="flex items-center gap-2">
                    <Zap className="w-5 h-5 text-yellow-400" />
                    <h2 className="text-lg font-semibold text-white">Early Warning Feed</h2>
                </div>
                <span className="text-xs font-medium px-2 py-1 bg-blue-500/10 text-blue-400 rounded-full border border-blue-500/20">
                    PROACTIVE SIGNALS
                </span>
            </div>

            <div className="flex-1 overflow-y-auto p-4 space-y-4 max-h-[500px]">
                {error && (
                    <div className="p-3 bg-red-500/10 border border-red-500/20 rounded-lg flex items-center gap-3 text-red-400 text-sm">
                        <AlertCircle className="w-4 h-4" />
                        {error}
                    </div>
                )}

                {articles.length === 0 && !error && (
                    <div className="flex flex-col items-center justify-center py-12 text-slate-500 space-y-3">
                        <Newspaper className="w-12 h-12 opacity-20" />
                        <p className="text-sm">No recent signals for this disease.</p>
                    </div>
                )}

                {articles.map((article) => (
                    <div
                        key={article.id || article.title}
                        className="group p-4 bg-slate-800/30 border border-slate-700/50 rounded-xl hover:border-blue-500/50 hover:bg-slate-800/50 transition-all duration-200"
                    >
                        <div className="flex justify-between items-start mb-2">
                            <span className="text-[10px] font-bold tracking-wider uppercase text-blue-400">
                                {article.source}
                            </span>
                            <span className="text-[10px] text-slate-500">
                                {new Date(article.published_at).toLocaleDateString()}
                            </span>
                        </div>
                        <h3 className="text-sm font-medium text-slate-200 mb-2 leading-snug group-hover:text-white transition-colors">
                            {article.title}
                        </h3>
                        <p className="text-xs text-slate-400 line-clamp-2 mb-3">
                            {article.content}
                        </p>
                        <div className="flex items-center justify-between">
                            <div className="flex gap-1">
                                {article.extracted_diseases.map(d => (
                                    <span key={d} className="text-[9px] px-1.5 py-0.5 bg-slate-700 text-slate-300 rounded border border-slate-600">
                                        {d}
                                    </span>
                                ))}
                            </div>
                            {article.url && (
                                <a
                                    href={article.url}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="p-1.5 text-slate-500 hover:text-blue-400 hover:bg-blue-400/10 rounded-lg transition-all"
                                >
                                    <ExternalLink className="w-3.5 h-3.5" />
                                </a>
                            )}
                        </div>
                    </div>
                ))}
            </div>

            <div className="p-3 bg-slate-800/30 border-t border-slate-700 flex justify-center">
                <button
                    className="text-[11px] font-medium text-slate-400 hover:text-white transition-colors"
                    onClick={async () => {
                        // This is for demo purposes in the frontend
                        try {
                            const res = await fetch('/api/news/ingest-simulated', { method: 'POST' });
                            if (res.ok) window.location.reload();
                        } catch (e) {
                            console.error(e);
                        }
                    }}
                >
                    FORCE SIGNAL REFRESH
                </button>
            </div>
        </div>
    );
};

export default EarlyWarningFeed;
