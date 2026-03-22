import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Send,
  Sparkles,
  AlertCircle,
  FileText,
  RefreshCw
} from 'lucide-react';

import FileUpload from './FileUpload';
import LanguageSelector from './LanguageSelector';
import ProgressBar from './ProgressBar';
import ResultCard from './ResultCard';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// 阶段配置
const PHASES = {
  WELCOME: 'welcome',      // 欢迎态 - 上传文件
  ANALYZED: 'analyzed',    // 分析态 - 展示数据概览，选择语言
  TRANSLATING: 'translating', // 翻译态 - 进度展示
  RESULT: 'result'         // 结果态 - 完成展示
};

function Chat({ darkMode }) {
  // 状态
  const [phase, setPhase] = useState(PHASES.WELCOME);
  const [taskId, setTaskId] = useState(null);
  const [stats, setStats] = useState(null);
  const [selectedLanguages, setSelectedLanguages] = useState([]);
  const [isUploading, setIsUploading] = useState(false);
  const [isTranslating, setIsTranslating] = useState(false);
  const [progress, setProgress] = useState(null);
  const [error, setError] = useState(null);
  const [input, setInput] = useState('');

  const pollingRef = useRef(null);

  // 清理轮询
  useEffect(() => {
    return () => {
      if (pollingRef.current) {
        clearInterval(pollingRef.current);
      }
    };
  }, []);

  // 轮询进度
  useEffect(() => {
    if (isTranslating && taskId) {
      pollingRef.current = setInterval(async () => {
        try {
          const res = await axios.get(`${API_URL}/api/status/${taskId}`);
          setProgress(res.data);

          if (res.data.status === 'completed' || res.data.status === 'failed') {
            setIsTranslating(false);
            clearInterval(pollingRef.current);

            if (res.data.status === 'completed') {
              setPhase(PHASES.RESULT);
            } else {
              setError(res.data.errors.join(', ') || '翻译失败');
            }
          }
        } catch (err) {
          console.error('获取进度失败:', err);
        }
      }, 1500);
    }
  }, [isTranslating, taskId]);

  // 文件上传处理
  const handleFileUpload = async (file) => {
    if (!file || !file.name.endsWith('.csv')) {
      setError('请上传 CSV 文件');
      return;
    }

    setIsUploading(true);
    setError(null);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await axios.post(`${API_URL}/api/upload`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });

      setTaskId(res.data.task_id);
      setStats(res.data.stats);
      setPhase(PHASES.ANALYZED);
    } catch (err) {
      setError(err.response?.data?.detail || '上传失败');
    } finally {
      setIsUploading(false);
    }
  };

  // 语言选择切换
  const handleLanguageToggle = (code) => {
    setSelectedLanguages(prev =>
      prev.includes(code)
        ? prev.filter(l => l !== code)
        : [...prev, code]
    );
  };

  // 开始翻译
  const handleStartTranslation = async () => {
    if (selectedLanguages.length === 0) {
      setError('请选择至少一种目标语言');
      return;
    }

    setIsTranslating(true);
    setError(null);
    setPhase(PHASES.TRANSLATING);
    setProgress({ status: 'processing', progress_percent: 0, total_batches: Math.ceil(stats.total_rows / 20) });

    // 发送翻译请求
    const langMap = { en: '英语', ja: '日语', ko: '韩语', fr: '法语', de: '德语', es: '西班牙语', ru: '俄语', pt: '葡萄牙语', it: '意大利语', ar: '阿拉伯语', th: '泰语', vi: '越南语' };
    const message = `翻译成${selectedLanguages.map(code => langMap[code] || code).join('和')}`;

    try {
      await axios.post(`${API_URL}/api/chat`, null, {
        params: { message, task_id: taskId }
      });
    } catch (err) {
      setError(err.response?.data?.detail || '翻译启动失败');
      setIsTranslating(false);
      setPhase(PHASES.ANALYZED);
    }
  };

  // 重置
  const handleReset = () => {
    setPhase(PHASES.WELCOME);
    setTaskId(null);
    setStats(null);
    setSelectedLanguages([]);
    setProgress(null);
    setError(null);
    setInput('');
  };

  return (
    <div className="space-y-6">
      {/* Error Alert */}
      <AnimatePresence>
        {error && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className={`flex items-center gap-2 px-4 py-3 rounded-xl ${
              darkMode
                ? 'bg-red-500/20 text-red-300'
                : 'bg-red-50 text-red-600'
            }`}
          >
            <AlertCircle className="w-5 h-5" />
            <span>{error}</span>
            <button
              onClick={() => setError(null)}
              className="ml-auto opacity-60 hover:opacity-100"
            >
              ×
            </button>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Phase: Welcome - 文件上传 */}
      <AnimatePresence mode="wait">
        {(phase === PHASES.WELCOME || !stats) && (
          <motion.div
            key="welcome"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0, y: -20 }}
            className="glass-card rounded-3xl p-8"
          >
            {/* Welcome Header */}
            <div className="text-center mb-8">
              <motion.div
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                transition={{ type: 'spring', delay: 0.1 }}
                className="w-24 h-24 mx-auto mb-6 rounded-3xl bg-gradient-to-br from-indigo-500 via-violet-500 to-purple-600 flex items-center justify-center shadow-2xl shadow-indigo-500/30"
              >
                <Sparkles className="w-12 h-12 text-white" />
              </motion.div>
              <h2 className={`font-display text-3xl font-bold mb-3 ${
                darkMode ? 'text-white' : 'text-slate-800'
              }`}>
                开始你的翻译之旅
              </h2>
              <p className={`text-base ${darkMode ? 'text-slate-400' : 'text-slate-500'}`}>
                上传 CSV 文件，AI 将智能识别并翻译中文内容
              </p>
            </div>

            {/* File Upload */}
            <FileUpload
              darkMode={darkMode}
              onFileSelect={handleFileUpload}
              isUploading={isUploading}
            />
          </motion.div>
        )}
      </AnimatePresence>

      {/* Phase: Analyzed - 数据概览 & 语言选择 */}
      <AnimatePresence mode="wait">
        {phase === PHASES.ANALYZED && stats && (
          <motion.div
            key="analyzed"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}
            className="space-y-6"
          >
            {/* Stats Cards */}
            <div className="glass-card rounded-3xl p-6">
              <div className="flex items-center justify-between mb-6">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-emerald-400 to-emerald-600 flex items-center justify-center">
                    <FileText className="w-5 h-5 text-white" />
                  </div>
                  <div>
                    <h3 className={`font-semibold ${darkMode ? 'text-white' : 'text-slate-800'}`}>
                      数据解析完成
                    </h3>
                    <p className={`text-sm ${darkMode ? 'text-slate-400' : 'text-slate-500'}`}>
                      已识别可翻译字段
                    </p>
                  </div>
                </div>
                <button
                  onClick={handleReset}
                  className={`px-3 py-1.5 rounded-lg text-sm ${
                    darkMode
                      ? 'bg-slate-700 text-slate-300 hover:bg-slate-600'
                      : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                  }`}
                >
                  重新上传
                </button>
              </div>

              {/* Stats Grid */}
              <div className="grid grid-cols-4 gap-3 mb-6">
                <StatCard value={stats.total_rows} label="数据行" darkMode={darkMode} />
                <StatCard value={stats.total_columns} label="列总数" darkMode={darkMode} />
                <StatCard value={stats.chinese_columns.length} label="中文字段" darkMode={darkMode} highlight />
                <StatCard value={Math.ceil(stats.total_rows / 20)} label="批次数" darkMode={darkMode} />
              </div>

              {/* Detected Columns */}
              <div className={`p-4 rounded-2xl ${
                darkMode ? 'bg-slate-800/50' : 'bg-indigo-50'
              }`}>
                <p className={`text-sm mb-2 ${darkMode ? 'text-slate-400' : 'text-slate-500'}`}>
                  检测到的可翻译字段：
                </p>
                <div className="flex flex-wrap gap-2">
                  {stats.chinese_columns.map((col, i) => (
                    <motion.span
                      key={col}
                      initial={{ opacity: 0, scale: 0.8 }}
                      animate={{ opacity: 1, scale: 1 }}
                      transition={{ delay: i * 0.05 }}
                      className={`px-3 py-1.5 rounded-lg text-sm font-medium ${
                        darkMode
                          ? 'bg-indigo-500/20 text-indigo-300'
                          : 'bg-indigo-100 text-indigo-700'
                      }`}
                    >
                      {col}
                    </motion.span>
                  ))}
                </div>
              </div>
            </div>

            {/* Language Selector */}
            <div className="glass-card rounded-3xl p-6">
              <LanguageSelector
                darkMode={darkMode}
                selectedLanguages={selectedLanguages}
                onToggle={handleLanguageToggle}
              />
            </div>

            {/* Start Button */}
            <motion.button
              onClick={handleStartTranslation}
              disabled={selectedLanguages.length === 0}
              whileHover={{ scale: selectedLanguages.length > 0 ? 1.02 : 1 }}
              whileTap={{ scale: selectedLanguages.length > 0 ? 0.98 : 1 }}
              className={`w-full py-4 rounded-2xl font-semibold text-lg transition-all ${
                selectedLanguages.length > 0
                  ? 'btn-gradient'
                  : darkMode
                    ? 'bg-slate-700 text-slate-500 cursor-not-allowed'
                    : 'bg-slate-100 text-slate-400 cursor-not-allowed'
              }`}
            >
              {selectedLanguages.length > 0 ? (
                <span className="flex items-center justify-center gap-2">
                  <Send className="w-5 h-5" />
                  开始翻译 ({selectedLanguages.length} 种语言)
                </span>
              ) : (
                '请选择目标语言'
              )}
            </motion.button>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Phase: Translating - 进度展示 */}
      <AnimatePresence mode="wait">
        {phase === PHASES.TRANSLATING && (
          <motion.div
            key="translating"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}
            className="glass-card rounded-3xl p-8"
          >
            <div className="text-center mb-8">
              <motion.div
                animate={{ rotate: 360 }}
                transition={{ duration: 2, repeat: Infinity, ease: 'linear' }}
                className="w-16 h-16 mx-auto mb-4 rounded-full border-4 border-indigo-500 border-t-transparent"
              />
              <h3 className={`text-xl font-bold mb-2 ${darkMode ? 'text-white' : 'text-slate-800'}`}>
                正在翻译中...
              </h3>
              <p className={`text-sm ${darkMode ? 'text-slate-400' : 'text-slate-500'}`}>
                AI 正在处理你的数据，请稍候
              </p>
            </div>

            <ProgressBar
              darkMode={darkMode}
              progress={progress}
              totalBatches={Math.ceil(stats?.total_rows / 20) || 1}
              currentBatch={progress?.current_batch}
            />
          </motion.div>
        )}
      </AnimatePresence>

      {/* Phase: Result - 结果展示 */}
      <AnimatePresence mode="wait">
        {phase === PHASES.RESULT && progress && (
          <motion.div
            key="result"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}
            className="space-y-6"
          >
            <ResultCard
              darkMode={darkMode}
              taskId={taskId}
              progress={progress}
              apiBaseUrl={API_URL}
            />

            {/* Restart Button */}
            <div className="text-center">
              <button
                onClick={handleReset}
                className={`inline-flex items-center gap-2 px-6 py-3 rounded-xl font-medium transition-colors ${
                  darkMode
                    ? 'bg-slate-700 hover:bg-slate-600 text-slate-300'
                    : 'bg-slate-100 hover:bg-slate-200 text-slate-600'
                }`}
              >
                <RefreshCw className="w-4 h-4" />
                翻译新文件
              </button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

// 统计卡片组件
function StatCard({ value, label, darkMode, highlight }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className={`p-4 rounded-2xl text-center ${
        highlight
          ? darkMode
            ? 'bg-gradient-to-br from-indigo-500/20 to-violet-500/20'
            : 'bg-gradient-to-br from-indigo-50 to-violet-50'
          : darkMode
            ? 'bg-slate-800/50'
            : 'bg-slate-50'
      }`}
    >
      <div className={`font-display text-2xl font-bold ${
        highlight ? 'gradient-text' : darkMode ? 'text-white' : 'text-slate-800'
      }`}>
        {value}
      </div>
      <div className={`text-xs mt-1 ${darkMode ? 'text-slate-400' : 'text-slate-500'}`}>
        {label}
      </div>
    </motion.div>
  );
}

export default Chat;
