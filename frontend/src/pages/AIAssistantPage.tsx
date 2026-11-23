import React, { useState } from 'react';
import { Bot, Send, Sparkles, User, Database, CheckCircle, AlertTriangle } from 'lucide-react';
import api from '../api/client';

interface Message {
  role: 'USER' | 'ASSISTANT';
  content: string;
  intent?: string;
  grounding_data?: any;
}

export const AIAssistantPage: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: 'ASSISTANT',
      content:
        'Hello! I am **FinFlow AI**, your enterprise financial intelligence copilot. I analyze your organization’s real persistent transaction records to explain variances, evaluate fraud risks, inspect 50/30/20 budgets, and forecast cash flow. What would you like to explore?',
    },
  ]);
  const [inputQuery, setInputQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [conversationId, setConversationId] = useState<string | null>(null);

  const sampleQuestions = [
    'How much did I spend this month and what is my top category?',
    'Why was a transaction flagged for high risk?',
    'Am I following the 50/30/20 budget rule?',
    'What subscriptions renew in the next 30 days?',
    'Explain my financial health score.',
    'What if I reduce shopping expenses by 15%?',
  ];

  const handleSend = async (queryText?: string) => {
    const q = queryText || inputQuery;
    if (!q.trim() || loading) return;

    const userMsg: Message = { role: 'USER', content: q };
    setMessages((prev) => [...prev, userMsg]);
    setInputQuery('');
    setLoading(true);

    try {
      const res = await api.post('/assistant/chat', {
        query: q,
        conversation_id: conversationId,
      });

      setConversationId(res.data.conversation_id);
      const aiMsg: Message = {
        role: 'ASSISTANT',
        content: res.data.answer,
        intent: res.data.intent,
        grounding_data: res.data.grounding_data,
      };
      setMessages((prev) => [...prev, aiMsg]);
    } catch (err: any) {
      setMessages((prev) => [
        ...prev,
        {
          role: 'ASSISTANT',
          content: 'Sorry, I encountered an issue analyzing your financial records. Please ensure your backend is reachable.',
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="h-[calc(100vh-8rem)] flex flex-col space-y-4">
      {/* Header */}
      <div>
        <div className="flex items-center gap-2">
          <Bot className="w-6 h-6 text-indigo-400" />
          <h1 className="text-2xl font-bold text-white tracking-tight">AI Financial Assistant</h1>
        </div>
        <p className="text-sm text-slate-400 mt-1">
          Zero-hallucination conversational copilot grounded directly in PostgreSQL database records.
        </p>
      </div>

      {/* Quick Prompts */}
      <div className="flex items-center gap-2 overflow-x-auto pb-1 text-xs">
        {sampleQuestions.map((q, idx) => (
          <button
            key={idx}
            onClick={() => handleSend(q)}
            className="px-3 py-1.5 rounded-full bg-slate-900 hover:bg-slate-800 text-slate-300 border border-slate-800 hover:border-slate-700 whitespace-nowrap transition"
          >
            {q}
          </button>
        ))}
      </div>

      {/* Chat Messages Container */}
      <div className="flex-1 bg-slate-900 border border-slate-800 rounded-xl p-6 overflow-y-auto space-y-5">
        {messages.map((msg, idx) => (
          <div
            key={idx}
            className={`flex items-start gap-3.5 max-w-3xl ${
              msg.role === 'USER' ? 'ml-auto flex-row-reverse' : ''
            }`}
          >
            <div
              className={`w-8 h-8 rounded-lg flex items-center justify-center shrink-0 shadow-md ${
                msg.role === 'USER'
                  ? 'bg-indigo-600 text-white'
                  : 'bg-gradient-to-tr from-cyan-600 to-indigo-600 text-white'
              }`}
            >
              {msg.role === 'USER' ? <User className="w-4 h-4" /> : <Bot className="w-4 h-4" />}
            </div>

            <div
              className={`p-4 rounded-xl text-sm leading-relaxed ${
                msg.role === 'USER'
                  ? 'bg-indigo-600 text-white rounded-tr-none'
                  : 'bg-slate-950/80 border border-slate-800 text-slate-200 rounded-tl-none space-y-3'
              }`}
            >
              {/* Intent / Grounding Badge */}
              {msg.intent && (
                <div className="flex items-center gap-1.5 text-[11px] font-mono font-medium text-cyan-400 pb-1 border-b border-slate-800">
                  <Database className="w-3.5 h-3.5" />
                  <span>Grounding Intent: {msg.intent}</span>
                </div>
              )}

              <div className="whitespace-pre-line">{msg.content}</div>
            </div>
          </div>
        ))}

        {loading && (
          <div className="flex items-center gap-3 text-slate-400 text-xs italic">
            <Bot className="w-4 h-4 animate-spin text-indigo-400" />
            <span>Querying verified relational tables and synthesizing explanation...</span>
          </div>
        )}
      </div>

      {/* Input Bar */}
      <form
        onSubmit={(e) => {
          e.preventDefault();
          handleSend();
        }}
        className="flex items-center gap-3 bg-slate-900 border border-slate-800 p-2.5 rounded-xl"
      >
        <input
          type="text"
          placeholder="Ask anything about your spending, fraud alerts, 50/30/20 budgets, or forecasts..."
          value={inputQuery}
          onChange={(e) => setInputQuery(e.target.value)}
          className="flex-1 bg-transparent px-3 text-sm text-white placeholder-slate-500 focus:outline-none"
        />
        <button
          type="submit"
          disabled={loading || !inputQuery.trim()}
          className="p-2.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white disabled:opacity-50 transition"
        >
          <Send className="w-4 h-4" />
        </button>
      </form>
    </div>
  );
};
