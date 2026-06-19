import React, { useState, useRef, useEffect } from 'react';

interface Step {
    title: string;
    content: string;
    duration_ms?: number;
}

interface ConfirmAction {
    action_description: string;
    method: string;
    endpoint: string;
    payload: Record<string, any>;
}

interface Message {
    id: string;
    role: 'user' | 'assistant';
    content: string;
    sql?: string;
    steps?: Step[];
    total_duration_ms?: number;
    confirmAction?: ConfirmAction;
    confirmResolved?: boolean;
}

export const CopilotPage: React.FC = () => {
    const [messages, setMessages] = useState<Message[]>([]);
    const [input, setInput] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [mode, setMode] = useState<'READ' | 'ACTION'>('READ');
    const [currentStatus, setCurrentStatus] = useState('');
    const [streamingId, setStreamingId] = useState<string | null>(null);
    const endOfMessagesRef = useRef<HTMLDivElement>(null);
    const wsRef = useRef<WebSocket | null>(null);

    const scrollToBottom = () => {
        endOfMessagesRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const handleConfirm = (msgId: string, approved: boolean) => {
        if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
            wsRef.current.send(JSON.stringify({ approved }));
        }
        setMessages(prev => prev.map(msg =>
            msg.id === msgId ? { ...msg, confirmResolved: true } : msg
        ));
    };

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

        const assistantId = (Date.now() + 1).toString();
        setStreamingId(assistantId);
        setCurrentStatus('');
        setMessages(prev => [...prev, { id: assistantId, role: 'assistant', content: '' }]);

        try {
            const token = localStorage.getItem('token');
            const wsUrl = import.meta.env.VITE_API_URL
                ? import.meta.env.VITE_API_URL.replace('http', 'ws')
                : 'ws://localhost:8000';

            const ws = new WebSocket(`${wsUrl}/api/v1/copilot/ws/query`);
            wsRef.current = ws;

            ws.onopen = () => {
                const history = messages.map(m => ({ role: m.role, content: m.content }));
                ws.send(JSON.stringify({ query: userMessage.content, token, history, mode }));
            };

            ws.onmessage = (event) => {
                const data = JSON.parse(event.data);

                setMessages(prev => prev.map(msg => {
                    if (msg.id !== assistantId) return msg;

                    if (data.type === 'status') {
                        setCurrentStatus(data.content);
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
                    } else if (data.type === 'confirm') {
                        return {
                            ...msg,
                            confirmAction: {
                                action_description: data.action_description,
                                method: data.method,
                                endpoint: data.endpoint,
                                payload: data.payload,
                            },
                            confirmResolved: false,
                        };
                    }
                    return msg;
                }));

                if (data.type === 'done' || data.type === 'error') {
                    if (data.type === 'done' && data.total_duration_ms !== undefined) {
                        setMessages(prev => prev.map(msg =>
                            msg.id === assistantId ? { ...msg, total_duration_ms: data.total_duration_ms } : msg
                        ));
                    }
                    ws.close();
                    wsRef.current = null;
                    setIsLoading(false);
                    setStreamingId(null);
                    setCurrentStatus('');
                }
            };

            ws.onerror = () => {
                setMessages(prev => prev.map(msg =>
                    msg.id === assistantId ? { ...msg, content: msg.content + '\n\n**Connection Error**' } : msg
                ));
                setIsLoading(false);
            };

            ws.onclose = () => { setIsLoading(false); };

        } catch (error: any) {
            console.error('Copilot error:', error);
            setMessages(prev => prev.map(msg =>
                msg.id === assistantId ? { ...msg, content: 'Sorry, I encountered an error.' } : msg
            ));
            setIsLoading(false);
        }
    };

    const methodColors: Record<string, string> = {
        GET:    'bg-blue-100 text-blue-700 dark:bg-blue-900/40 dark:text-blue-300',
        POST:   'bg-green-100 text-green-700 dark:bg-green-900/40 dark:text-green-300',
        PATCH:  'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/40 dark:text-yellow-300',
        DELETE: 'bg-red-100 text-red-700 dark:bg-red-900/40 dark:text-red-300',
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
                    <p className="text-sm text-gray-500 dark:text-gray-400">
                        {mode === 'READ' ? 'Ask natural language questions about your data.' : '⚡ Action Mode — I can create, update and delete records.'}
                    </p>
                </div>
                <div className="flex items-center gap-2 bg-gray-200 dark:bg-gray-800 p-1 rounded-lg">
                    <button
                        onClick={() => setMode('READ')}
                        className={`px-3 py-1 text-xs font-medium rounded-md transition-colors ${mode === 'READ' ? 'bg-white dark:bg-gray-700 shadow text-gray-900 dark:text-white' : 'text-gray-500 hover:text-gray-700 dark:hover:text-gray-300'}`}
                    >
                        Read Data
                    </button>
                    <button
                        onClick={() => setMode('ACTION')}
                        className={`px-3 py-1 text-xs font-medium rounded-md transition-colors ${mode === 'ACTION' ? 'bg-orange-500 shadow text-white' : 'text-gray-500 hover:text-gray-700 dark:hover:text-gray-300'}`}
                    >
                        ⚡ Take Action
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
                            <p className="text-gray-500 dark:text-gray-400 max-w-sm mt-1">
                                {mode === 'READ' ? 'Ask questions about your data in plain English.' : 'Tell me what to create, update or delete.'}
                            </p>
                        </div>
                        <div className="flex flex-wrap justify-center gap-2 mt-4 max-w-md">
                            {mode === 'READ' ? (
                                <>
                                    <button onClick={() => setInput("Show all departments")} className="px-3 py-1.5 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-full text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-50 transition-colors">"Show all departments"</button>
                                    <button onClick={() => setInput("List all projects")} className="px-3 py-1.5 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-full text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-50 transition-colors">"List all projects"</button>
                                    <button onClick={() => setInput("How many employees do we have?")} className="px-3 py-1.5 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-full text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-50 transition-colors">"How many employees?"</button>
                                </>
                            ) : (
                                <>
                                    <button onClick={() => setInput("Update Jason Carter's name to John Carter")} className="px-3 py-1.5 bg-orange-50 dark:bg-orange-900/20 border border-orange-200 dark:border-orange-800 rounded-full text-sm text-orange-700 dark:text-orange-300 hover:bg-orange-100 transition-colors">"Update employee name"</button>
                                    <button onClick={() => setInput("Create a new department called Marketing")} className="px-3 py-1.5 bg-orange-50 dark:bg-orange-900/20 border border-orange-200 dark:border-orange-800 rounded-full text-sm text-orange-700 dark:text-orange-300 hover:bg-orange-100 transition-colors">"Create department"</button>
                                    <button onClick={() => setInput("Delete Project Beta")} className="px-3 py-1.5 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-full text-sm text-red-700 dark:text-red-300 hover:bg-red-100 transition-colors">"Delete a project"</button>
                                </>
                            )}
                        </div>
                    </div>
                ) : (
                    messages.map((msg) => (
                        <div key={msg.id} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                            <div className={`max-w-[85%] rounded-2xl p-4 ${msg.role === 'user' ? 'bg-primary text-primary-foreground rounded-tr-sm' : 'bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 text-gray-800 dark:text-gray-200 rounded-tl-sm shadow-sm'}`}>

                                {/* Live status pill — shown only while this msg is streaming */}
                                {msg.id === streamingId && currentStatus && !msg.content && (
                                    <div className="flex items-center gap-2 mb-3">
                                        <span className="inline-flex items-center gap-1.5 px-2.5 py-1 bg-primary/10 text-primary rounded-full text-xs font-medium">
                                            <span className="w-1.5 h-1.5 bg-primary rounded-full animate-pulse" />
                                            {currentStatus}
                                        </span>
                                    </div>
                                )}


                                {/* ── Agent Steps (collapsed by default) ── */}
                                {msg.steps && msg.steps.length > 0 && (
                                    <details className="mt-3 group/outer">
                                        <summary className="text-xs font-semibold text-gray-400 dark:text-gray-500 uppercase tracking-wider flex items-center gap-1.5 cursor-pointer select-none list-none hover:text-gray-600 dark:hover:text-gray-300 transition-colors">
                                            {msg.id === streamingId
                                                ? <span className="w-1.5 h-1.5 bg-blue-400 rounded-full animate-pulse flex-shrink-0" />
                                                : <span className="text-base leading-none">🔗</span>
                                            }
                                            Agent Steps
                                            <span className="ml-1 text-gray-300 dark:text-gray-600 font-normal normal-case">({msg.steps.length})</span>
                                            <svg className="w-3 h-3 ml-auto transform group-open/outer:rotate-180 transition-transform flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 9l-7 7-7-7" /></svg>
                                        </summary>
                                        <div className="mt-1.5 flex flex-col gap-1">
                                            {msg.steps.map((step, idx) => {
                                                const isLatest = msg.id === streamingId && idx === (msg.steps?.length ?? 0) - 1;
                                                return (
                                                    <details key={idx} className="bg-gray-50 dark:bg-gray-900 border border-gray-100 dark:border-gray-800 rounded group">
                                                        <summary className={`text-xs font-medium p-2 cursor-pointer transition-colors select-none flex items-center justify-between ${
                                                            isLatest
                                                                ? 'text-blue-600 dark:text-blue-400 bg-blue-50 dark:bg-blue-900/20'
                                                                : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800'
                                                        }`}>
                                                            <span className="flex items-center gap-1.5">
                                                                {isLatest && <span className="w-1.5 h-1.5 bg-blue-400 rounded-full animate-pulse" />}
                                                                {step.title}
                                                                {step.duration_ms !== undefined
                                                                    ? <span className="text-gray-400 ml-1 font-normal">({(step.duration_ms / 1000).toFixed(2)}s)</span>
                                                                    : isLatest ? <span className="text-gray-400 ml-1 font-normal">running...</span> : null
                                                                }
                                                            </span>
                                                            <svg className="w-3.5 h-3.5 transform group-open:rotate-180 transition-transform flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 9l-7 7-7-7" /></svg>
                                                        </summary>
                                                        <div className="p-2 border-t border-gray-100 dark:border-gray-800 text-xs text-gray-600 dark:text-gray-400 overflow-x-auto whitespace-pre-wrap font-mono">
                                                            {step.content}
                                                        </div>
                                                    </details>
                                                );
                                            })}
                                            {msg.sql && (
                                                <details className="bg-gray-50 dark:bg-gray-900 border border-gray-100 dark:border-gray-800 rounded group mt-1">
                                                    <summary className="text-xs font-medium p-2 cursor-pointer transition-colors select-none flex items-center justify-between text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800">
                                                        <span className="flex items-center gap-1.5">
                                                            <span className="text-base leading-none">🗄️</span>
                                                            Generated SQL
                                                        </span>
                                                        <svg className="w-3.5 h-3.5 transform group-open:rotate-180 transition-transform flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 9l-7 7-7-7" /></svg>
                                                    </summary>
                                                    <div className="p-2 border-t border-gray-100 dark:border-gray-800 text-xs text-gray-700 dark:text-gray-300 overflow-x-auto whitespace-pre-wrap font-mono">
                                                        {msg.sql}
                                                    </div>
                                                </details>
                                            )}
                                        </div>
                                    </details>
                                )}

                                {/* Main streamed content */}
                                {msg.content && (
                                    <div className="mt-3 pt-3 border-t border-gray-100 dark:border-gray-800 prose dark:prose-invert max-w-none text-sm font-medium text-gray-800 dark:text-gray-100 whitespace-pre-wrap leading-relaxed">
                                        {msg.content}
                                        {msg.id === streamingId && (
                                            <span className="inline-block w-0.5 h-5 bg-gray-500 animate-pulse ml-0.5 align-middle" />
                                        )}
                                    </div>
                                )}

                                {/* ── Confirmation Card ── */}
                                {msg.confirmAction && !msg.confirmResolved && (
                                    <div className="mt-3 border border-orange-300 dark:border-orange-700 bg-orange-50 dark:bg-orange-900/20 rounded-xl p-4 space-y-3">
                                        <div className="flex items-center gap-2">
                                            <span className="text-orange-500 text-lg">⚠️</span>
                                            <p className="text-sm font-semibold text-orange-800 dark:text-orange-200">Confirm Action</p>
                                        </div>
                                        <p className="text-sm text-gray-700 dark:text-gray-300">{msg.confirmAction.action_description}</p>
                                        <div className="flex items-center gap-2 flex-wrap">
                                            <span className={`px-2 py-0.5 text-xs font-bold rounded font-mono ${methodColors[msg.confirmAction.method] ?? 'bg-gray-100 text-gray-700'}`}>
                                                {msg.confirmAction.method}
                                            </span>
                                            <code className="text-xs text-gray-600 dark:text-gray-400 bg-gray-100 dark:bg-gray-900 px-2 py-0.5 rounded">{msg.confirmAction.endpoint}</code>
                                        </div>
                                        {Object.keys(msg.confirmAction.payload).length > 0 && (
                                            <div className="bg-gray-100 dark:bg-gray-900 rounded-lg p-2">
                                                <p className="text-xs font-medium text-gray-500 mb-1">Payload</p>
                                                <table className="text-xs w-full">
                                                    <tbody>
                                                        {Object.entries(msg.confirmAction.payload).map(([k, v]) => (
                                                            <tr key={k}>
                                                                <td className="text-gray-500 pr-3 py-0.5 font-mono">{k}</td>
                                                                <td className="text-gray-800 dark:text-gray-200 font-medium">{String(v)}</td>
                                                            </tr>
                                                        ))}
                                                    </tbody>
                                                </table>
                                            </div>
                                        )}
                                        <div className="flex gap-2 pt-1">
                                            <button
                                                onClick={() => handleConfirm(msg.id, true)}
                                                className="flex-1 px-4 py-2 bg-green-600 hover:bg-green-700 text-white text-sm font-medium rounded-lg transition-colors"
                                            >
                                                ✅ Confirm
                                            </button>
                                            <button
                                                onClick={() => handleConfirm(msg.id, false)}
                                                className="flex-1 px-4 py-2 bg-gray-200 hover:bg-gray-300 dark:bg-gray-700 dark:hover:bg-gray-600 text-gray-800 dark:text-gray-200 text-sm font-medium rounded-lg transition-colors"
                                            >
                                                ❌ Cancel
                                            </button>
                                        </div>
                                    </div>
                                )}

                                {msg.confirmAction && msg.confirmResolved && (
                                    <div className="mt-3 border border-gray-200 dark:border-gray-700 rounded-xl p-3 text-xs text-gray-400 flex items-center gap-2">
                                        <span>🔒</span> Confirmation resolved
                                    </div>
                                )}



                                {msg.total_duration_ms !== undefined && (
                                    <div className="mt-3 pt-2 border-t border-gray-100 dark:border-gray-800 flex justify-end">
                                        <span className="text-[10px] text-gray-400 font-mono">
                                            Total: {(msg.total_duration_ms / 1000).toFixed(2)}s
                                        </span>
                                    </div>
                                )}
                            </div>
                        </div>
                    ))
                )}
                {/* Loading bubble — shows live status text */}
                {isLoading && !messages.find(m => m.id === streamingId && (m.steps?.length ?? 0) > 0) && (
                    <div className="flex justify-start">
                        <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-2xl rounded-tl-sm px-4 py-3 shadow-sm flex items-center gap-2 max-w-xs">
                            <div className="flex gap-1">
                                <div className="w-2 h-2 bg-primary rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                                <div className="w-2 h-2 bg-primary rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                                <div className="w-2 h-2 bg-primary rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                            </div>
                            <span className="text-sm text-gray-500 truncate">
                                {currentStatus || (mode === 'ACTION' ? 'Planning action...' : 'Analyzing...')}
                            </span>
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
                        placeholder={mode === 'ACTION' ? "e.g. \"Update Jason Carter's name to John Carter\"" : 'Ask a question about your data...'}
                        className="flex-1 bg-gray-50 dark:bg-gray-900 border border-gray-300 dark:border-gray-700 text-gray-900 dark:text-gray-100 rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent transition-all"
                        disabled={isLoading}
                    />
                    <button
                        type="submit"
                        disabled={!input.trim() || isLoading}
                        className={`px-5 py-3 rounded-lg font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 ${mode === 'ACTION' ? 'bg-orange-500 hover:bg-orange-600 text-white' : 'bg-primary hover:bg-primary/90 text-primary-foreground'}`}
                    >
                        <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="22" y1="2" x2="11" y2="13"></line><polygon points="22 2 15 22 11 13 2 9 22 2"></polygon></svg>
                        <span className="hidden sm:inline">{mode === 'ACTION' ? 'Execute' : 'Send'}</span>
                    </button>
                </form>
                <div className="text-center mt-2">
                    <span className="text-xs text-gray-400">
                        {mode === 'ACTION' ? '⚠️ Action Mode: All changes require your manual confirmation before execution.' : 'AI can make mistakes. Verify important information.'}
                    </span>
                </div>
            </div>
        </div>
    );
};
