import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Plus, X } from 'lucide-react';

const PRESET_LANGUAGES = [
  { code: 'en', name: '英语', flag: '🇺🇸', native: 'English' },
  { code: 'ja', name: '日语', flag: '🇯🇵', native: '日本語' },
  { code: 'ko', name: '韩语', flag: '🇰🇷', native: '한국어' },
  { code: 'fr', name: '法语', flag: '🇫🇷', native: 'Français' },
  { code: 'de', name: '德语', flag: '🇩🇪', native: 'Deutsch' },
  { code: 'es', name: '西班牙语', flag: '🇪🇸', native: 'Español' },
  { code: 'ru', name: '俄语', flag: '🇷🇺', native: 'Русский' },
  { code: 'pt', name: '葡萄牙语', flag: '🇵🇹', native: 'Português' },
  { code: 'it', name: '意大利语', flag: '🇮🇹', native: 'Italiano' },
  { code: 'ar', name: '阿拉伯语', flag: '🇸🇦', native: 'العربية' },
  { code: 'th', name: '泰语', flag: '🇹🇭', native: 'ไทย' },
  { code: 'vi', name: '越南语', flag: '🇻🇳', native: 'Tiếng Việt' },
];

function LanguageSelector({ darkMode, selectedLanguages, onToggle }) {
  const [customInput, setCustomInput] = useState('');

  // 分离预设语言和自定义语言
  const presetCodes = new Set(PRESET_LANGUAGES.map(l => l.code));
  const selectedPresets = selectedLanguages.filter(code => presetCodes.has(code));
  const customLanguages = selectedLanguages.filter(code => !presetCodes.has(code));

  // 添加自定义语言
  const handleAddCustom = () => {
    const lang = customInput.trim();
    if (lang && !selectedLanguages.includes(lang)) {
      onToggle(lang);
      setCustomInput('');
    }
  };

  // 回车添加
  const handleKeyDown = (e) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      handleAddCustom();
    }
  };

  // 获取语言显示名称
  const getLanguageName = (code) => {
    const preset = PRESET_LANGUAGES.find(l => l.code === code);
    return preset ? preset.name : code;
  };

  return (
    <div className="w-full">
      <label className={`block text-sm font-medium mb-3 ${
        darkMode ? 'text-slate-300' : 'text-slate-600'
      }`}>
        选择目标语言
      </label>

      {/* 预设语言选择 */}
      <div className="flex flex-wrap gap-2 mb-3">
        {PRESET_LANGUAGES.map((lang, index) => {
          const isSelected = selectedLanguages.includes(lang.code);

          return (
            <motion.button
              key={lang.code}
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: index * 0.02 }}
              onClick={() => onToggle(lang.code)}
              className={`lang-chip flex items-center gap-2 ${
                isSelected ? 'selected' : ''
              }`}
            >
              <span className="text-base">{lang.flag}</span>
              <span>{lang.name}</span>
              {isSelected && (
                <motion.span
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  className="ml-1 text-xs opacity-80"
                >
                  ✓
                </motion.span>
              )}
            </motion.button>
          );
        })}
      </div>

      {/* 自定义语言输入 */}
      <div className={`p-4 rounded-2xl ${
        darkMode ? 'bg-slate-800/50' : 'bg-slate-50'
      }`}>
        <p className={`text-xs mb-2 ${darkMode ? 'text-slate-400' : 'text-slate-500'}`}>
          或输入其他语言（如：荷兰语、瑞典语、印地语等）
        </p>

        <div className="flex gap-2">
          <input
            type="text"
            value={customInput}
            onChange={(e) => setCustomInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="输入语言名称..."
            className={`flex-1 px-4 py-2.5 rounded-xl outline-none transition-all text-sm ${
              darkMode
                ? 'bg-slate-700 text-white placeholder-slate-400 focus:ring-2 focus:ring-indigo-500'
                : 'bg-white text-slate-800 placeholder-slate-400 focus:ring-2 focus:ring-indigo-500 border border-slate-200'
            }`}
          />
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={handleAddCustom}
            disabled={!customInput.trim()}
            className={`px-4 py-2.5 rounded-xl font-medium text-sm transition-all flex items-center gap-1 ${
              customInput.trim()
                ? 'bg-gradient-to-r from-indigo-500 to-violet-500 text-white'
                : darkMode
                  ? 'bg-slate-700 text-slate-500 cursor-not-allowed'
                  : 'bg-slate-200 text-slate-400 cursor-not-allowed'
            }`}
          >
            <Plus className="w-4 h-4" />
            添加
          </motion.button>
        </div>

        {/* 已添加的自定义语言 */}
        {customLanguages.length > 0 && (
          <div className="flex flex-wrap gap-2 mt-3">
            {customLanguages.map((lang) => (
              <motion.span
                key={lang}
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                className={`inline-flex items-center gap-2 px-3 py-1.5 rounded-lg text-sm font-medium ${
                  darkMode
                    ? 'bg-orange-500/20 text-orange-300'
                    : 'bg-orange-100 text-orange-700'
                }`}
              >
                <span>{lang}</span>
                <button
                  onClick={() => onToggle(lang)}
                  className="hover:opacity-70 transition-opacity"
                >
                  <X className="w-3.5 h-3.5" />
                </button>
              </motion.span>
            ))}
          </div>
        )}
      </div>

      {/* 已选择汇总 */}
      {selectedLanguages.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className={`mt-3 text-sm ${darkMode ? 'text-slate-400' : 'text-slate-500'}`}
        >
          已选择 {selectedLanguages.length} 种语言：
          <span className="font-medium ml-1">
            {selectedLanguages.map(code => getLanguageName(code)).join('、')}
          </span>
        </motion.div>
      )}
    </div>
  );
}

export default LanguageSelector;
