import React, { useState, useRef, useEffect } from 'react';
import api from '../lib/api';

interface Message {
    id: string;
    role: 'user' | 'assistant';
    content: string;
    sql?: string;
    context?: string[];
    steps?: {title: string, content: string, duration_ms?: number}[];
    total_duration_ms?: number;
}

export const CopilotPage: React.FC = () => {
    const [messages, setMessages] = useState<Message[]>([]);
    const [input, setInput] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [mode, setMode] = useState<'READ' | 'ACTION'>('READ');
    const endOfMessagesRef = useRef<HTMLDivElement>(null);

    const scrollToBottom = () => {
        endOfMessagesRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!input.trim() || isLoading) return;

        const userMessage: Message = {
            id: Date.now().toString(),
            role: 'user',
            content: input.trim()
        };

        setMessages(prev => [...prev, userMessage]);
        setInput('');
        setIsLoading(true);
        
        // Initialize an empty assistant message
        const assistantId = (Date.now() + 1).toString();
        setMessages(prev => [...prev, {
            id: assistantId,
            role: 'assistant',
            content: ''
        }]);

        try {
            const token = localStorage.getItem('token');
            const wsUrl = import.meta.env.VITE_API_URL 
                ? import.meta.env.VITE_API_URL.replace('http', 'ws') 
                : 'ws://localhost:8000';
                
            const ws = new WebSocket(`${wsUrl}/api/v1/copilot/ws/query`);
            
            ws.onopen = () => {
                // Map previous messages for history context
                const history = messages.map(m => ({
                    role: m.role,
                    content: m.content
                }));
                ws.send(JSON.stringify({ query: userMessage.content, token, history, mode }));
            };

            ws.onmessage = (event) => {
                const data = JSON.parse(event.data);
                
                setMessages(prev => prev.map(msg => {
                    if (msg.id !== assistantId) return msg;
                    
                    if (data.type === 'status') {
                        // We could display status updates in the UI
                        return msg;
                    } else if (data.type === 'step') {
                        const newSteps = [...(msg.steps || []), { title: data.title, content: data.content, duration_ms: data.duration_ms }];
                        return { ...msg, steps: newSteps };
                    } else if (data.type === 'sql') {
                        return { ...msg, sql: data.content };
                    } else if (data.type === 'content') {
                        return { ...msg, content: msg.content + data.content };
                    } else if (data.type === 'error') {
                        return { ...msg, content: msg.content + '\n\n**Error:** ' + data.content };
                    }
                    return msg;
                }));

                if (data.type === 'done' || data.type === 'error') {
                    if (data.type === 'done' && data.total_duration_ms) {
                        setMessages(prev => prev.map(msg => msg.id === assistantId ? { ...msg, total_duration_ms: data.total_duration_ms } : msg));
                    }
                    ws.close();
                    setIsLoading(false);
                }
            };

            ws.onerror = (error) => {
                console.error('WebSocket error:', error);
                setMessages(prev => prev.map(msg => 
                    msg.id === assistantId ? { ...msg, content: msg.content + '\n\n**Connection Error**' } : msg
                ));
                setIsLoading(false);
            };
            
            ws.onclose = () => {
                setIsLoading(false);
            };

        } catch (error: any) {
            console.error('Copilot error:', error);
            setMessages(prev => prev.map(msg => 
                msg.id === assistantId ? { ...msg, content: 'Sorry, I encountered an error.' } : msg
            ));
            setIsLoading(false);
        }
    };

    return (
        <div className="flex flex-col h-full bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-lg overflow-hidden shadow-sm">
            {/* Header */}
            <div className="bg-white dark:bg-gray-950 p-4 border-b border-gray-200 dark:border-gray-800 flex justify-between items-center">
                <div>
                    <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100 flex items-center gap-2">
                        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-primary"><path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg>
                        AI Data Copilot
                    </h2>
                    <p className="text-sm text-gray-500 dark:text-gray-400">Ask natural language questions about your organization, projects, and finances.</p>
                </div>
                {/* Mode Toggle */}
                <div className="flex items-center gap-2 bg-gray-200 dark:bg-gray-800 p-1 rounded-lg">
                    <button 
                        onClick={() => setMode('READ')}
                        className={`px-3 py-1 text-xs font-medium rounded-md transition-colors ${mode === 'READ' ? 'bg-white dark:bg-gray-700 shadow text-gray-900 dark:text-white' : 'text-gray-500 hover:text-gray-700 dark:hover:text-gray-300'}`}
                    >
                        Read Data
                    </button>
                    <button 
                        onClick={() => setMode('ACTION')}
                        className={`px-3 py-1 text-xs font-medium rounded-md transition-colors ${mode === 'ACTION' ? 'bg-white dark:bg-gray-700 shadow text-gray-900 dark:text-white' : 'text-gray-500 hover:text-gray-700 dark:hover:text-gray-300'}`}
                    >
                        Take Action
                    </button>
                </div>
            </div>

            {/* Chat Area */}
            <div className="flex-1 overflow-y-auto p-4 space-y-6">
                {messages.length === 0 ? (
                    <div className="flex flex-col items-center justify-center h-full text-center space-y-4">
                        <div className="w-16 h-16 bg-primary/10 rounded-full flex items-center justify-center">
                            <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-primary"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>
                        </div>
                        <div>
                            <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100">Welcome to AI Copilot</h3>
                            <p className="text-gray-500 dark:text-gray-400 max-w-sm mt-1">I can convert your questions into SQL, query the database, and summarize the results.</p>
                        </div>
                        <div className="flex flex-wrap justify-center gap-2 mt-4 max-w-md">
                            <button onClick={() => setInput("Show all departments")} className="px-3 py-1.5 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-full text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-750 transition-colors">"Show all departments"</button>
                            <button onClick={() => setInput("List all projects")} className="px-3 py-1.5 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-full text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-750 transition-colors">"List all vendors"</button>
                            <button onClick={() => setInput("How many employees do we have?")} className="px-3 py-1.5 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-full text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-750 transition-colors">"How many employees do we have?"</button>
                        </div>
                    </div>
                ) : (
                    messages.map((msg) => (
                        <div key={msg.id} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                            <div className={`max-w-[80%] rounded-2xl p-4 ${msg.role === 'user' ? 'bg-primary text-primary-foreground rounded-tr-sm' : 'bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 text-gray-800 dark:text-gray-200 rounded-tl-sm shadow-sm'}`}>
                                <div className="prose dark:prose-invert max-w-none text-sm whitespace-pre-wrap">
                                    {msg.content}
                                </div>
                                
                                {msg.steps && msg.steps.length > 0 && (
                                    <div className="mt-4 flex flex-col gap-2">
                                        <p className="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider">Agent Chain of Thought</p>
                                        {msg.steps.map((step, idx) => (
                                            <details key={idx} className="bg-gray-50 dark:bg-gray-900 border border-gray-100 dark:border-gray-800 rounded group">
                                                <summary className="text-xs font-medium text-gray-700 dark:text-gray-300 p-2 cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors select-none flex items-center justify-between">
                                                    <span>{step.title} {step.duration_ms !== undefined ? <span className="text-gray-400 ml-2 font-normal">({(step.duration_ms / 1000).toFixed(2)}s)</span> : ''}</span>
                                                    <svg className="w-4 h-4 transform group-open:rotate-180 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 9l-7 7-7-7"></path></svg>
                                                </summary>
                                                <div className="p-2 border-t border-gray-100 dark:border-gray-800 text-xs text-gray-600 dark:text-gray-400 overflow-x-auto whitespace-pre-wrap">
                                                    {step.content}
                                                </div>
                                            </details>
                                        ))}
                                    </div>
                                )}
                                {msg.sql && (
                                    <div className="mt-4 pt-3 border-t border-gray-200 dark:border-gray-700">
                                        <p className="text-xs font-semibold text-gray-500 dark:text-gray-400 mb-2 uppercase tracking-wider">Generated SQL</p>
                                        <pre className="bg-gray-50 dark:bg-gray-900 p-2 rounded text-xs text-gray-700 dark:text-gray-300 overflow-x-auto border border-gray-100 dark:border-gray-800">
                                            <code>{msg.sql}</code>
                                        </pre>
                                    </div>
                                )}
                                {msg.total_duration_ms !== undefined && (
                                    <div className="mt-3 pt-2 border-t border-gray-100 dark:border-gray-800 flex justify-end">
                                        <span className="text-[10px] text-gray-400 font-mono">
                                            Total processing time: {(msg.total_duration_ms / 1000).toFixed(2)}s
                                        </span>
                                    </div>
                                )}
                            </div>
                        </div>
                    ))
                )}
                {isLoading && (
                    <div className="flex justify-start">
                        <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-2xl rounded-tl-sm p-4 shadow-sm flex items-center gap-2">
                            <div className="w-2 h-2 bg-primary rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                            <div className="w-2 h-2 bg-primary rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                            <div className="w-2 h-2 bg-primary rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
                            <span className="text-sm text-gray-500 ml-2">Analyzing your query...</span>
                        </div>
                    </div>
                )}
                <div ref={endOfMessagesRef} />
            </div>

            {/* Input Area */}
            <div className="bg-white dark:bg-gray-950 p-4 border-t border-gray-200 dark:border-gray-800">
                <form onSubmit={handleSubmit} className="flex gap-2">
                    <input
                        type="text"
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        placeholder="Ask a question about your data..."
                        className="flex-1 bg-gray-50 dark:bg-gray-900 border border-gray-300 dark:border-gray-700 text-gray-900 dark:text-gray-100 rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent transition-all"
                        disabled={isLoading}
                    />
                    <button
                        type="submit"
                        disabled={!input.trim() || isLoading}
                        className="bg-primary hover:bg-primary/90 text-primary-foreground px-5 py-3 rounded-lg font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
                    >
                        <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="22" y1="2" x2="11" y2="13"></line><polygon points="22 2 15 22 11 13 2 9 22 2"></polygon></svg>
                        <span className="hidden sm:inline">Send</span>
                    </button>
                </form>
                <div className="text-center mt-2">
                    <span className="text-xs text-gray-400">AI can make mistakes. Verify important information.</span>
                </div>
            </div>
        </div>
    );
};
