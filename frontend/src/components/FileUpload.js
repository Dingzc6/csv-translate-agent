import React, { useState, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Upload, FileText, Check, X, Sparkles } from 'lucide-react';

function FileUpload({ darkMode, onFileSelect, isUploading }) {
  const [dragActive, setDragActive] = useState(false);
  const [fileName, setFileName] = useState(null);

  const handleDrag = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  }, []);

  const handleDrop = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const file = e.dataTransfer.files[0];
      if (file.name.endsWith('.csv')) {
        setFileName(file.name);
        onFileSelect(file);
      }
    }
  }, [onFileSelect]);

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      setFileName(file.name);
      onFileSelect(file);
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="w-full"
    >
      <div
        className={`drop-zone relative rounded-3xl p-8 cursor-pointer transition-all duration-300 ${
          dragActive ? 'drag-over scale-[1.02]' : ''
        }`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
        onClick={() => document.getElementById('file-input').click()}
      >
        <input
          id="file-input"
          type="file"
          accept=".csv"
          className="hidden"
          onChange={handleFileChange}
        />

        <AnimatePresence mode="wait">
          {isUploading ? (
            <motion.div
              key="uploading"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="flex flex-col items-center py-4"
            >
              <div className="relative">
                <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-indigo-500 to-violet-600 flex items-center justify-center">
                  <Sparkles className="w-8 h-8 text-white animate-pulse" />
                </div>
                <div className="absolute inset-0 rounded-2xl bg-gradient-to-br from-indigo-500 to-violet-600 animate-ping opacity-20" />
              </div>
              <p className={`mt-4 font-medium ${darkMode ? 'text-slate-200' : 'text-slate-700'}`}>
                正在解析文件...
              </p>
            </motion.div>
          ) : fileName ? (
            <motion.div
              key="file-selected"
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              className="flex flex-col items-center py-4"
            >
              <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-emerald-400 to-emerald-600 flex items-center justify-center">
                <Check className="w-8 h-8 text-white" />
              </div>
              <p className={`mt-4 font-medium ${darkMode ? 'text-slate-200' : 'text-slate-700'}`}>
                {fileName}
              </p>
              <p className={`text-sm mt-1 ${darkMode ? 'text-slate-400' : 'text-slate-500'}`}>
                点击更换文件
              </p>
            </motion.div>
          ) : (
            <motion.div
              key="empty"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="flex flex-col items-center py-4"
            >
              <div className={`w-20 h-20 rounded-3xl flex items-center justify-center mb-4 transition-colors ${
                darkMode
                  ? 'bg-slate-700/50'
                  : 'bg-indigo-50'
              }`}>
                <Upload className={`w-9 h-9 transition-colors ${
                  dragActive
                    ? 'text-orange-500'
                    : darkMode
                      ? 'text-slate-400'
                      : 'text-indigo-500'
                }`} />
              </div>

              <h3 className={`text-lg font-semibold mb-2 ${
                darkMode ? 'text-slate-200' : 'text-slate-800'
              }`}>
                拖拽 CSV 文件到这里
              </h3>
              <p className={`text-sm mb-4 ${darkMode ? 'text-slate-400' : 'text-slate-500'}`}>
                或点击选择文件
              </p>

              <div className={`flex items-center gap-2 px-4 py-2 rounded-full text-xs ${
                darkMode
                  ? 'bg-slate-700/50 text-slate-400'
                  : 'bg-indigo-50 text-indigo-600'
              }`}>
                <FileText className="w-4 h-4" />
                支持 .csv 格式，最大 10000 行
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </motion.div>
  );
}

export default FileUpload;
