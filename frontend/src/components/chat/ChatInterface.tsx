import { useState, useEffect } from 'react';
import { Send, Clock } from 'lucide-react';
import { fetcher } from '../../lib/api';
import { supabase } from '../../lib/auth';
import Sidebar from '../sidebar/Sidebar';
import vectorIcon from '../../assets/Vector.png';

export default function ChatInterface() {
  const [user, setUser] = useState<any>(null);
  const [urlInput, setUrlInput] = useState('');
  const [ingesting, setIngesting] = useState(false);
  const [videoData, setVideoData] = useState<any>(null);
  const [chats, setChats] = useState<Array<{ id: string; title: string }>>([]);
  const [activeChatId, setActiveChatId] = useState<string | null>(null);
  const [messages, setMessages] = useState<Array<{ role: string; content: string; citations?: any[] }>>([]);
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    supabase.auth.getUser().then(({ data: { user } }) => {
      if (user) {
        setUser(user);
        fetchUserChats(user.id);
      }
    });
  }, []);

  const fetchUserChats = async (userId: string) => {
    try {
      const data = await fetcher(`/chats?user_id=${userId}`);
      setChats(data);
    } catch (err) {
      console.error('Failed to load chats', err);
    }
  };

  const handleIngest = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!urlInput || !user) return;
    setIngesting(true);
    try {
      const videoRes = await fetcher('/videos/ingest', {
        method: 'POST',
        body: JSON.stringify({ url: urlInput }),
      });
      setVideoData(videoRes);

      const chatRes = await fetcher('/chats', {
        method: 'POST',
        body: JSON.stringify({
          user_id: user.id,
          video_id: videoRes.id,
        }),
      });

      setActiveChatId(chatRes.id);
      setChats((prev) => [chatRes, ...prev]);
      setMessages([
        {
          role: 'assistant',
          content: `Successfully ingested **${videoRes.title || 'Video'}**. Ask me anything about it!`,
        },
      ]);
    } catch (err: any) {
      alert(`Ingestion failed: ${err.message}`);
    } finally {
      setIngesting(false);
    }
  };

  const handleSelectChat = async (chatId: string) => {
    setActiveChatId(chatId);
    setLoading(true);
    try {
      const msgs = await fetcher(`/messages/${chatId}?user_id=${user.id}`);
      setMessages(
        msgs.map((m: any) => ({
          role: m.role,
          content: m.content,
          citations: m.message_metadata?.citations || [],
        }))
      );
    } catch (err: any) {
      alert(`Failed to load messages: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleSendQuery = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query || !activeChatId || !user) return;

    const userMsg = query;
    setQuery('');
    setMessages((prev) => [...prev, { role: 'user', content: userMsg }]);
    setLoading(true);

    try {
      const res = await fetcher('/chats/query', {
        method: 'POST',
        body: JSON.stringify({
          chat_id: activeChatId,
          user_id: user.id,
          query: userMsg,
        }),
      });

      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: res.answer,
          citations: res.citations,
        },
      ]);
    } catch (err: any) {
      alert(`Query failed: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex h-screen bg-[#171717] text-[#ececec] flex-1 overflow-hidden">
      <Sidebar
        chats={chats}
        activeChatId={activeChatId}
        onSelectChat={handleSelectChat}
        onNewChat={() => {
          setActiveChatId(null);
          setVideoData(null);
          setMessages([]);
        }}
        onLogout={() => supabase.auth.signOut()}
      />

      <div className="flex flex-1 flex-col h-full">
        {/* Header (Text removed) */}
        <header className="flex h-14 items-center justify-between border-b border-[#2e2e2e] px-6">
          <div className="flex items-center space-x-2 text-sm font-semibold"></div>
        </header>

        <main className="flex-1 overflow-y-auto p-6">
          {!videoData && !activeChatId ? (
            <div className="flex h-full items-center justify-center">
              <div className="w-full max-w-md rounded-xl bg-[#212121] p-8 shadow-2xl border border-[#303030]">
                <div className="flex flex-col items-center text-center">
                  {/* Replaced Lucide Video icon with Vector.png */}
                  <div className="rounded-full bg-transparent p-3 mb-3">
                    <img src={vectorIcon} alt="Logo Icon" className="h-10 w-10 object-contain" />
                  </div>
                  <h3 className="text-xl font-bold text-white mb-2">Ingest a YouTube Video</h3>
                  <p className="text-xs text-neutral-400 mb-6">
                    Paste a YouTube link below to index its transcript, generate vector embeddings, and start chatting with timestamp grounding.
                  </p>
                </div>

                <form onSubmit={handleIngest} className="flex gap-2">
                  <input
                    type="url"
                    required
                    placeholder="https://www.youtube.com/watch?v=..."
                    value={urlInput}
                    onChange={(e) => setUrlInput(e.target.value)}
                    className="flex-1 rounded-md bg-[#171717] border border-[#383838] px-3 py-2 text-xs text-white focus:outline-none focus:border-white"
                  />
                  <button
                    type="submit"
                    disabled={ingesting}
                    className="rounded-md bg-white px-4 py-2 text-xs font-semibold text-black transition hover:bg-neutral-200 disabled:opacity-50"
                  >
                    {ingesting ? 'Processing...' : 'Ingest'}
                  </button>
                </form>
              </div>
            </div>
          ) : (
            <div className="mx-auto flex h-full max-w-3xl flex-col justify-between">
              <div className="space-y-6 overflow-y-auto pb-6">
                {messages.map((msg, index) => (
                  <div
                    key={index}
                    className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                  >
                    <div
                      className={`max-w-[85%] rounded-2xl px-4 py-3 text-sm ${
                        msg.role === 'user'
                          ? 'bg-[#2f2f2f] text-white'
                          : 'bg-[#212121] text-neutral-200 border border-[#303030]'
                      }`}
                    >
                      <p className="whitespace-pre-wrap leading-relaxed">{msg.content}</p>

                      {msg.citations && msg.citations.length > 0 && (
                        <div className="mt-4 border-t border-[#383838] pt-3">
                          <p className="text-xs font-semibold text-neutral-400 mb-2 flex items-center gap-1">
                            <Clock className="h-3 w-3" /> Timestamp Sources
                          </p>
                          <div className="flex flex-wrap gap-2">
                            {msg.citations.map((cite: any, idx: number) => (
                              <a
                                key={idx}
                                href={cite.url}
                                target="_blank"
                                rel="noreferrer"
                                className="inline-flex items-center rounded-md bg-[#171717] px-2.5 py-1 text-xs text-neutral-300 hover:text-white border border-[#383838] transition"
                              >
                                {cite.timestamp_formatted || `Source ${idx + 1}`}
                              </a>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                ))}

                {loading && (
                  <div className="flex justify-start">
                    <div className="rounded-2xl bg-[#212121] px-4 py-3 text-xs text-neutral-400 border border-[#303030] animate-pulse">
                      Loading conversation...
                    </div>
                  </div>
                )}
              </div>

              <form onSubmit={handleSendQuery} className="relative mt-2">
                <input
                  type="text"
                  placeholder="Ask anything about this video..."
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  className="w-full rounded-xl bg-[#212121] border border-[#383838] py-3.5 pl-4 pr-12 text-sm text-white placeholder-neutral-500 focus:outline-none focus:border-neutral-400"
                />
                <button
                  type="submit"
                  disabled={loading || !query}
                  className="absolute right-2.5 top-2.5 rounded-lg bg-white p-2 text-black transition hover:bg-neutral-200 disabled:opacity-30"
                >
                  <Send className="h-4 w-4" />
                </button>
              </form>
            </div>
          )}
        </main>
      </div>
    </div>
  );
}