import React from 'react';
import { motion } from 'framer-motion';
import { Download, ExternalLink, CheckCircle, Clock, FileText, Globe } from 'lucide-react';

function ResultCard({ darkMode, taskId, progress, apiBaseUrl }) {
  const duration = calculateDuration(progress.started_at, progress.completed_at);
  const totalTranslations = progress.total_rows * progress.target_languages.length * progress.columns_to_translate.length;

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95, y: 20 }}
      animate={{ opacity: 1, scale: 1, y: 0 }}
      className={`glass-card rounded-3xl p-6 space-y-6`}
    >
      {/* Success Header */}
      <div className="flex items-center gap-3">
        <motion.div
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          transition={{ type: 'spring', delay: 0.2 }}
          className="w-14 h-14 rounded-2xl bg-gradient-to-br from-emerald-400 to-emerald-600 flex items-center justify-center shadow-lg shadow-emerald-500/30"
        >
          <CheckCircle className="w-7 h-7 text-white" />
        </motion.div>
        <div>
          <h3 className={`text-xl font-bold ${darkMode ? 'text-white' : 'text-slate-800'}`}>
            翻译完成！
          </h3>
          <p className={`text-sm ${darkMode ? 'text-slate-400' : 'text-slate-500'}`}>
            所有批次已成功处理
          </p>
        </div>
      </div>

      {/* Statistics Grid */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        <StatItem
          icon={<FileText className="w-4 h-4" />}
          value={progress.total_rows}
          label="总行数"
          darkMode={darkMode}
        />
        <StatItem
          icon={<Globe className="w-4 h-4" />}
          value={progress.target_languages.length}
          label="目标语言"
          darkMode={darkMode}
        />
        <StatItem
          icon={<CheckCircle className="w-4 h-4" />}
          value={totalTranslations}
          label="翻译条目"
          darkMode={darkMode}
        />
        <StatItem
          icon={<Clock className="w-4 h-4" />}
          value={duration}
          label="耗时"
          darkMode={darkMode}
        />
      </div>

      {/* Translation Summary */}
      <div className={`p-4 rounded-2xl ${
        darkMode ? 'bg-slate-800/50' : 'bg-slate-50'
      }`}>
        <div className="flex flex-wrap gap-2">
          {progress.columns_to_translate.map((col, i) => (
            <span
              key={i}
              className={`px-3 py-1 rounded-lg text-xs font-medium ${
                darkMode ? 'bg-slate-700 text-slate-300' : 'bg-white text-slate-600'
              }`}
            >
              {col}
            </span>
          ))}
          <span className={`text-sm ${darkMode ? 'text-slate-500' : 'text-slate-400'}`}>
            →
          </span>
          {progress.target_languages.map((lang, i) => (
            <span
              key={i}
              className={`px-3 py-1 rounded-lg text-xs font-medium ${
                darkMode
                  ? 'bg-indigo-500/20 text-indigo-300'
                  : 'bg-indigo-50 text-indigo-600'
              }`}
            >
              {getLanguageName(lang)}
            </span>
          ))}
        </div>
      </div>

      {/* Action Buttons */}
      <div className="grid grid-cols-2 gap-3">
        <motion.a
          href={`${apiBaseUrl}/result/${taskId}`}
          target="_blank"
          rel="noopener noreferrer"
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          className={`flex items-center justify-center gap-2 px-6 py-3.5 rounded-xl font-medium transition-colors ${
            darkMode
              ? 'bg-slate-700 hover:bg-slate-600 text-white'
              : 'bg-slate-100 hover:bg-slate-200 text-slate-700'
          }`}
        >
          <ExternalLink className="w-5 h-5" />
          预览结果
        </motion.a>

        <motion.a
          href={`${apiBaseUrl}/download/${taskId}`}
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          className="btn-gradient flex items-center justify-center gap-2 px-6 py-3.5 rounded-xl font-medium"
        >
          <Download className="w-5 h-5" />
          下载 CSV
        </motion.a>
      </div>
    </motion.div>
  );
}

function StatItem({ icon, value, label, darkMode }) {
  return (
    <div className={`stat-card ${darkMode ? 'dark' : ''}`}>
      <div className={`flex items-center justify-center gap-1 mb-1 ${
        darkMode ? 'text-slate-400' : 'text-slate-500'
      }`}>
        {icon}
      </div>
      <div className="stat-value">{value}</div>
      <div className="stat-label">{label}</div>
    </div>
  );
}

function calculateDuration(start, end) {
  if (!start || !end) return '-';
  try {
    const startTime = new Date(start);
    const endTime = new Date(end);
    const seconds = Math.round((endTime - startTime) / 1000);
    if (seconds < 60) return `${seconds}秒`;
    const minutes = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${minutes}分${secs}秒`;
  } catch {
    return '-';
  }
}

function getLanguageName(code) {
  const map = {
    en: '英语', ja: '日语', ko: '韩语',
    fr: '法语', de: '德语', es: '西班牙语', ru: '俄语'
  };
  return map[code] || code;
}

export default ResultCard;
