import { Plus, MessageSquare, LogOut } from 'lucide-react';
import logoFull from '../../assets/Vector-2.png';

interface SidebarProps {
  chats: Array<{ id: string; title: string }>;
  activeChatId: string | null;
  onSelectChat: (id: string) => void;
  onNewChat: () => void;
  onLogout: () => void;
}

export default function Sidebar({ chats, activeChatId, onSelectChat, onNewChat, onLogout }: SidebarProps) {
  return (
    <aside className="flex flex-col h-screen w-64 bg-[#171717] border-r border-neutral-800 p-3 select-none shrink-0">
      {/* Full Logo Header */}
      <div className="flex items-center px-3 py-3 mb-2">
        <img src={logoFull} alt="CiteTube Logo" className="h-7 w-auto object-contain" />
      </div>

      <button
        onClick={onNewChat}
        className="flex items-center gap-3 w-full rounded-lg border border-neutral-700 bg-transparent px-3 py-2.5 text-sm font-medium text-white hover:bg-neutral-800 transition-colors mb-4"
      >
        <Plus className="h-4 w-4" />
        New video chat
      </button>

      <div className="flex-1 overflow-y-auto space-y-1">
        <div className="text-[11px] font-semibold text-neutral-500 px-3 py-2">Recent Chats</div>
        {chats.map((chat) => (
          <button
            key={chat.id}
            onClick={() => onSelectChat(chat.id)}
            className={`flex items-center gap-3 w-full rounded-lg px-3 py-2.5 text-sm text-left truncate transition-colors ${
              activeChatId === chat.id ? 'bg-[#212121] text-white font-medium' : 'text-neutral-400 hover:bg-[#212121]/50 hover:text-white'
            }`}
          >
            <MessageSquare className="h-4 w-4 shrink-0 text-neutral-500" />
            <span className="truncate">{chat.title}</span>
          </button>
        ))}
      </div>

      <div className="pt-3 border-t border-neutral-800">
        <button
          onClick={onLogout}
          className="flex items-center gap-3 w-full rounded-lg px-3 py-2 text-sm text-neutral-400 hover:bg-neutral-800 hover:text-white transition-colors"
        >
          <LogOut className="h-4 w-4" />
          Log out
        </button>
      </div>
    </aside>
  );
}