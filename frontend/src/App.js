import React, { useState } from 'react';
import Chat from './components/Chat';
import { Moon, Sun, Sparkles } from 'lucide-react';
import logo from './logo.png';

function App() {
  const [darkMode, setDarkMode] = useState(false);

  const toggleDarkMode = () => {
    setDarkMode(!darkMode);
    document.documentElement.classList.toggle('dark');
  };

  return (
    <div className={`min-h-screen transition-colors duration-500 relative ${darkMode ? 'dark' : ''}`}>
      {/* Animated Background */}
      <div className="animated-bg">
        <div className="orb orb-1" />
        <div className="orb orb-2" />
        <div className="orb orb-3" />
      </div>

      {/* Header */}
      <header className={`sticky top-0 z-50 transition-all duration-300 ${
        darkMode ? 'bg-slate-900/60' : 'bg-white/60'
      } backdrop-blur-xl border-b ${darkMode ? 'border-slate-700/50' : 'border-indigo-100/50'}`}>
        <div className="max-w-5xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            {/* Logo */}
            <div className="flex items-center gap-3">
              <div className="relative">
                <img
                  src={logo}
                  alt="Logo"
                  className="w-11 h-11 rounded-2xl shadow-lg"
                />
                <div className="absolute -top-1 -right-1 w-4 h-4 bg-orange-400 rounded-full flex items-center justify-center">
                  <Sparkles className="w-2.5 h-2.5 text-white" />
                </div>
              </div>
              <div>
                <h1 className="font-display text-lg font-medium gradient-text">
                  文字的旅行，从这里开始
                </h1>
              </div>
            </div>

            {/* Actions */}
            <div className="flex items-center gap-3">
              {/* Status Badge */}
              <div className={`hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-medium ${
                darkMode
                  ? 'bg-emerald-500/20 text-emerald-400'
                  : 'bg-emerald-50 text-emerald-600'
              }`}>
                <span className="w-2 h-2 bg-emerald-500 rounded-full animate-pulse" />
                GPT-5.4 就绪
              </div>

              {/* Theme Toggle */}
              <button
                onClick={toggleDarkMode}
                className={`relative w-12 h-7 rounded-full transition-all duration-300 ${
                  darkMode
                    ? 'bg-indigo-600'
                    : 'bg-slate-200'
                }`}
              >
                <span className={`absolute top-1 w-5 h-5 rounded-full bg-white shadow-md transition-all duration-300 flex items-center justify-center ${
                  darkMode ? 'left-6' : 'left-1'
                }`}>
                  {darkMode ? (
                    <Moon className="w-3 h-3 text-indigo-600" />
                  ) : (
                    <Sun className="w-3 h-3 text-amber-500" />
                  )}
                </span>
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-4xl mx-auto px-4 py-8">
        <Chat darkMode={darkMode} />
      </main>

      {/* Footer */}
      <footer className={`text-center py-8 ${
        darkMode ? 'text-slate-500' : 'text-slate-400'
      }`}>
        <div className="flex items-center justify-center gap-6 text-sm">
          <span className="flex items-center gap-1">
            <span className="w-2 h-2 bg-indigo-500 rounded-full" />
            Batch 分片
          </span>
          <span className="flex items-center gap-1">
            <span className="w-2 h-2 bg-violet-500 rounded-full" />
            智能校验
          </span>
          <span className="flex items-center gap-1">
            <span className="w-2 h-2 bg-orange-500 rounded-full" />
            防幻觉
          </span>
        </div>
        <p className="mt-3 text-xs opacity-60">
          Powered by TranslateFlow Agent v1.0
        </p>
      </footer>
    </div>
  );
}

export default App;
