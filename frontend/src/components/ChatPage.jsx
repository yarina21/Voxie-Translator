import { useState, useRef, useEffect } from 'react'
import robotAnimation from '../assets/robot.json'

// --- Componentă Custom pentru Selecția Limbii ---
function LanguageDropdown({ selectedCode, onSelect, languages, textColor, align = 'left', isDark }) {
  const [isOpen, setIsOpen] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')
  const dropdownRef = useRef(null)

  useEffect(() => {
    function handleClickOutside(event) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setIsOpen(false); setSearchQuery('') 
      }
    }
    document.addEventListener("mousedown", handleClickOutside)
    return () => document.removeEventListener("mousedown", handleClickOutside)
  }, [])

  const selectedName = languages.find(l => l.code === selectedCode)?.name || 'Auto'
  const filteredLanguages = languages.filter(l => l.name.toLowerCase().includes(searchQuery.toLowerCase()))

  return (
    <div className="relative" ref={dropdownRef}>
      <button 
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2 px-4 py-2 rounded-xl transition-colors bg-transparent border-none text-sm font-bold uppercase tracking-wider cursor-pointer"
        style={{ color: textColor, backgroundColor: isDark ? 'rgba(255,255,255,0.05)' : 'rgba(253,242,248,0.5)' }}
      >
        {selectedName}
        <span className="text-[10px] opacity-70">{isOpen ? '▲' : '▼'}</span>
      </button>

      {isOpen && (
        <div 
          className={`absolute top-full ${align === 'right' ? 'right-0' : 'left-0'} mt-2 w-64 p-3 rounded-2xl shadow-2xl z-50 transition-all`}
          style={{ background: isDark ? 'rgba(30, 41, 59, 0.95)' : 'rgba(255, 255, 255, 0.95)', backdropFilter: 'blur(20px)', border: `1px solid ${isDark ? 'rgba(255,255,255,0.1)' : 'rgba(211, 154, 197, 0.3)'}` }}
        >
          <div className="mb-2 relative">
            <input 
              type="text" autoFocus placeholder="Caută limba..." value={searchQuery} onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full px-4 py-2 rounded-xl text-sm focus:outline-none transition-colors"
              style={{ background: isDark ? 'rgba(0,0,0,0.2)' : '#f9fafb', color: isDark ? '#f1f5f9' : '#2c2c2c', border: `1px solid ${isDark ? 'rgba(255,255,255,0.1)' : '#f3f4f6'}` }}
            />
          </div>
          <div className="max-h-56 overflow-y-auto custom-scrollbar pr-1">
            {filteredLanguages.map(lang => (
              <button
                key={lang.code} onClick={() => { onSelect(lang.code); setIsOpen(false); setSearchQuery('') }}
                className="w-full text-left px-4 py-2 rounded-lg text-sm font-medium transition-colors mb-1"
                style={{ color: selectedCode === lang.code ? textColor : (isDark ? '#94a3b8' : '#5a7a8f'), backgroundColor: selectedCode === lang.code ? (isDark ? 'rgba(236,72,153,0.1)' : '#fce7f3') : 'transparent' }}
              >
                {lang.name}
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

// --- Componenta Principală ChatPage ---
export default function ChatPage({ onBackToLanding }) {
  // Stări aplicație
  const [appState, setAppState] = useState('idle') 
  const [inputText, setInputText] = useState('') 
  const [transcribedText, setTranscribedText] = useState('')
  const [translatedText, setTranslatedText] = useState('')
  const [messages, setMessages] = useState([])
  const [backendAudioUrl, setBackendAudioUrl] = useState(null)
  const [dynamicFact, setDynamicFact] = useState('Sunt conectat la server. Apasă microfonul sau scrie textul! 🚀')
  
  // Stări UI Premium
  const [isSidebarOpen, setIsSidebarOpen] = useState(false)
  const [isDark, setIsDark] = useState(false) 
  const [playbackSpeed, setPlaybackSpeed] = useState(1) 
  
  const [sourceLang, setSourceLang] = useState('auto')
  const [targetLang, setTargetLang] = useState('en')
  
  const lottieContainerRef = useRef(null)
  const messagesEndRef = useRef(null)
  const mediaRecorderRef = useRef(null)
  const audioChunksRef = useRef([])

  const [dictionaryData, setDictionaryData] = useState(null);
  const [phoneticText, setPhoneticText] = useState(null);
  
  const isTextMode = inputText.trim().length > 0
  const isSingleWord = translatedText && !translatedText.trim().includes(' ')
  const charLimit = 5000

  const sourceLanguages = [
    { code: 'auto', name: 'Auto-Detectare' },
    { code: 'ro', name: 'Română' }, { code: 'en', name: 'Engleză' },
    { code: 'fr', name: 'Franceză' }, { code: 'de', name: 'Germană' },
    { code: 'es', name: 'Spaniolă' }, { code: 'it', name: 'Italiană' }
  ]
  
  const targetLanguages = [
    { code: 'en', name: 'Engleză' }, { code: 'ro', name: 'Română' },
    { code: 'fr', name: 'Franceză' }, { code: 'de', name: 'Germană' },
    { code: 'es', name: 'Spaniolă' }, { code: 'it', name: 'Italiană' },
    { code: 'ja', name: 'Japoneză' }, { code: 'zh', name: 'Chineză' }
  ]

  // --- Efect: Caută informații reale pe Wikipedia la schimbarea limbii ---
  useEffect(() => {
    const fetchWikiFact = async () => {
      setDynamicFact('Caut informații pe internet... 🔍')
      const tgtName = targetLanguages.find(l => l.code === targetLang)?.name || 'Engleză'
      
      try {
        const pageTitle = `Limba_${tgtName.toLowerCase()}`
        const response = await fetch(`https://ro.wikipedia.org/api/rest_v1/page/summary/${pageTitle}`)
        
        if (response.ok) {
          const data = await response.json()
          const extract = data.extract || ''
          const scurt = extract.split('.')[0] + '.'
          setDynamicFact(scurt)
        } else {
          setDynamicFact('Știai că există peste 7.000 de limbi vorbite în prezent în întreaga lume? 🌍')
        }
      } catch (error) {
        setDynamicFact('Există mii de limbi pe glob. Păstrează-ți curiozitatea! 🌍')
      }
    }
    
    if (appState === 'idle') {
      fetchWikiFact()
    }
  }, [targetLang, appState])

  // --- Funcție Redare Audio (Robotul vorbește) ---
  const autoPlayAudio = (url) => {
    if (url) {
      const audio = new Audio(url)
      audio.playbackRate = playbackSpeed
      audio.play()
    }
  }

  // --- FIX: handleResponse este acum funcția centrală care procesează orice răspuns de la backend ---
  const handleResponse = (data, input = "") => {
    setTranslatedText(data.translated_text);
    setBackendAudioUrl(data.audio_url);
    setDictionaryData(data.dictionary || null);
    setPhoneticText(data.phonetics || null);
    
    if (data.audio_url) {
      const audio = new Audio(data.audio_url);
      audio.playbackRate = playbackSpeed;
      audio.play();
    }
    setMessages(prev => [{ 
      id: Date.now(), 
      original: data.original_text || input, 
      translated: data.translated_text, 
      from: data.detected_language || sourceLang, 
      to: targetLang 
    }, ...prev]);
  };

  // --- Trimitere TEXT către Backend ---
  const handleTextAction = async () => {
    if (appState === 'processing' || !isTextMode) return
    setAppState('processing')

    const formData = new FormData()
    formData.append('text', inputText)
    formData.append('target_lang', targetLang)

    try {
      const response = await fetch('http://127.0.0.1:8000/process-text', { method: 'POST', body: formData })
      const data = await response.json()
      
      // FIX: folosim handleResponse în loc de setări manuale
      if (data.status === 'success') {
        handleResponse(data, inputText)
        setInputText('')
      }
    } catch (error) {
      console.error("Eroare Text Backend:", error)
      setTranslatedText("Eroare de conexiune cu serverul.")
    } finally {
      setAppState('idle')
    }
  }

  // --- Trimitere VOCE către Backend ---
  const toggleRecording = async () => {
    if (appState === 'idle') {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
        mediaRecorderRef.current = new MediaRecorder(stream)
        audioChunksRef.current = []

        mediaRecorderRef.current.ondataavailable = (event) => {
          if (event.data.size > 0) audioChunksRef.current.push(event.data)
        }

        mediaRecorderRef.current.onstop = async () => {
          setAppState('processing')
          
          const audioBlob = new Blob(audioChunksRef.current, { type: mediaRecorderRef.current.mimeType })
          const formData = new FormData()
          formData.append('file', audioBlob, 'recording.ogg') 
          formData.append('source_lang', sourceLang)
          formData.append('target_lang', targetLang)

          try {
            const response = await fetch('http://127.0.0.1:8000/process-audio', { method: 'POST', body: formData })
            const data = await response.json()
            
            // FIX: folosim handleResponse în loc de setări manuale
            if (data.status === 'success') {
              setTranscribedText(data.original_text)
              handleResponse(data)
            }
          } catch (error) {
            console.error("Eroare Audio Backend:", error)
          } finally {
            setAppState('idle')
            stream.getTracks().forEach(track => track.stop())
          }
        }
        mediaRecorderRef.current.start()
        setAppState('listening')
      } catch (err) {
        console.error("Eroare microfon:", err)
      }
    } else if (appState === 'listening') {
      mediaRecorderRef.current?.stop()
    }
  }

  // Redare manuală
  const handleManualSpeak = () => {
    if (backendAudioUrl) autoPlayAudio(backendAudioUrl)
  }

  // Tasta Enter pentru Text
  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      if (isTextMode) handleTextAction()
    }
  }

  useEffect(() => {
    if (window.lottie && lottieContainerRef.current) {
      const animation = window.lottie.loadAnimation({ container: lottieContainerRef.current, renderer: 'svg', loop: true, autoplay: true, animationData: robotAnimation })
      return () => animation.destroy()
    }
  }, [])

  useEffect(() => { messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' }) }, [messages])

  // Logica Mesaj Robot
  const getRobotMessage = () => {
    if (appState === 'listening') return <span className="text-3xl animate-pulse">Te ascult...</span>
    if (appState === 'processing') return 'Analizez la backend... ⏳'
    if (isTextMode) return 'Apasă trimite pentru a traduce! ✨'
    return (
      <span className="flex flex-col items-center gap-1">
        <span className="text-xs font-bold uppercase tracking-widest text-pink-500 mb-1">💡 Știai că:</span>
        <span className="text-[14px] leading-snug">{dynamicFact}</span>
      </span>
    )
  }

  // Teme Vizuale
  const theme = {
    bg: isDark ? '#0f172a' : '#fff0f5', 
    textMain: isDark ? '#f8fafc' : '#2c2c2c',
    textMuted: isDark ? '#94a3b8' : '#5a7a8f',
    cardBg: isDark ? 'rgba(30, 41, 59, 0.7)' : 'rgba(255, 255, 255, 0.85)',
    cardBorder: isDark ? 'rgba(255, 255, 255, 0.1)' : 'rgba(255, 255, 255, 1)',
    inputBg: appState === 'listening' ? (isDark ? 'rgba(236,72,153,0.1)' : 'rgba(211, 154, 197, 0.1)') : (isDark ? 'rgba(15, 23, 42, 0.6)' : 'rgba(255, 255, 255, 0.6)'),
    accent: isDark ? '#f472b6' : '#D4A5C4'
  }
  

  return (
    <div className={`w-full min-h-screen flex flex-col relative overflow-hidden transition-colors duration-500 ${isDark ? 'dark-mode-active' : ''}`} style={{ background: theme.bg }}>
      
      {/* HEADER */}
      <div className="w-full px-10 py-6 flex justify-between items-center z-20">
        <h1 className="font-bold tracking-wider" style={{ fontSize: '28px', color: theme.textMuted }}>VOXIE AI</h1>
        <div className="flex gap-4">
          <button onClick={() => setIsDark(!isDark)} className="w-10 h-10 flex items-center justify-center rounded-full transition-all shadow-sm" style={{ background: isDark ? 'rgba(255,255,255,0.1)' : 'white', border: `1px solid ${theme.cardBorder}` }}>{isDark ? '☀️' : '🌙'}</button>
          <button onClick={() => setIsSidebarOpen(!isSidebarOpen)} className="px-6 py-2.5 rounded-full text-sm font-bold shadow-sm" style={{ border: `1px solid ${theme.accent}`, color: theme.textMuted }}>Istoric</button>
          <button onClick={onBackToLanding} className="px-6 py-2.5 rounded-full text-sm font-bold shadow-sm" style={{ background: isDark ? 'rgba(255,255,255,0.1)' : 'white', color: theme.textMuted }}>← Înapoi</button>
        </div>
      </div>

      {/* MAIN CONTENT */}
      <div className={`flex-1 flex flex-col lg:flex-row px-10 pb-10 gap-12 max-w-[1600px] mx-auto w-full justify-center transition-all duration-300 ${isSidebarOpen ? 'pr-[380px]' : ''}`}>
        
        {/* Robot */}
        <div className="flex-1 flex flex-col items-center justify-center relative">
          <div className={`speech-bubble mb-8 transition-all duration-300 ${isDark ? 'dark-bubble' : ''}`}>
            <p className="speech-text min-h-[60px] flex items-center justify-center text-center" style={{ color: theme.textMain }}>
              {getRobotMessage()}
            </p>
          </div>
          <div ref={lottieContainerRef} id="lottie-container" style={{ transform: 'scale(1.1)' }}></div>
        </div>

        {/* Translation Box */}
        <div className="flex-[1.5] flex flex-col justify-center w-full relative">
          <div className="w-full rounded-[32px] p-8 relative flex flex-col shadow-2xl" style={{ background: theme.cardBg, backdropFilter: 'blur(20px)', border: `1px solid ${theme.cardBorder}` }}>
            
            {/* Limbile */}
            <div className="flex items-center justify-between mb-6 p-2 rounded-2xl shadow-sm" style={{ background: isDark ? 'rgba(0,0,0,0.2)' : 'rgba(255,255,255,0.5)', border: `1px solid ${theme.cardBorder}` }}>
              <LanguageDropdown selectedCode={sourceLang} onSelect={setSourceLang} languages={sourceLanguages} textColor={theme.textMuted} isDark={isDark} />
              <button 
                onClick={() => { if(sourceLang !== 'auto') { const t = sourceLang; setSourceLang(targetLang); setTargetLang(t) } }}
                disabled={sourceLang === 'auto'}
                className="p-3 rounded-full transition-all shadow-sm disabled:opacity-50"
                style={{ background: isDark ? 'rgba(255,255,255,0.1)' : 'white', color: theme.accent, cursor: sourceLang === 'auto' ? 'not-allowed' : 'pointer' }}
              >⇄</button>
              <LanguageDropdown selectedCode={targetLang} onSelect={setTargetLang} languages={targetLanguages} textColor={theme.accent} align="right" isDark={isDark} />
            </div>

            {/* Text Original */}
            <div className="w-full min-h-[140px] p-5 rounded-2xl mb-4 relative flex flex-col" style={{ background: theme.inputBg, border: appState === 'listening' ? `1px dashed ${theme.accent}` : `1px solid ${theme.cardBorder}` }}>
              {appState === 'listening' ? (
                <div className="flex-1 flex items-center justify-center"><div className="audio-visualizer"><div className="bar"></div><div className="bar"></div><div className="bar"></div><div className="bar"></div></div></div>
              ) : (
                <textarea
                  value={appState === 'processing' && !isTextMode ? transcribedText : inputText}
                  onChange={(e) => setInputText(e.target.value)} onKeyDown={handleKeyDown} disabled={appState !== 'idle'}
                  placeholder="Înregistrează sau scrie textul..."
                  className="w-full flex-1 bg-transparent border-none resize-none text-2xl font-medium focus:outline-none custom-scrollbar" style={{ color: theme.textMain }}
                />
              )}
            </div>

            <div className="w-full h-px my-1" style={{ background: `linear-gradient(90deg, transparent, ${theme.cardBorder}, transparent)` }}></div>

            {/* Text Tradus */}
            <div className="w-full min-h-[140px] p-5 rounded-2xl mt-4 relative flex flex-col justify-between">
              <p className="text-3xl font-bold leading-relaxed" style={{ color: theme.accent }}>
                {appState === 'processing' ? <span className="opacity-50 text-xl">Backend-ul procesează...</span> : (translatedText || <span className="opacity-30 text-xl font-normal" style={{ color: theme.textMuted }}>Traducerea va apărea aici</span>)}
              </p>

              {/* FIX: Fonetică și Dicționar afișate în interiorul cardului, sub textul tradus */}
              {phoneticText && (
                <p className="text-sm mt-2 font-mono" style={{ color: theme.textMuted }}>
                  🔤 {phoneticText}
                </p>
              )}

              {dictionaryData && (
                <div className="mt-4 p-4 border rounded-xl" style={{ borderColor: theme.cardBorder }}>
                    <h3 className="text-xs font-bold opacity-50">DICȚIONAR ({dictionaryData.partOfSpeech})</h3>
    
                <div className="mt-2">
                  <p className="text-sm font-semibold">Sinonime găsite:</p>
                {dictionaryData.synonyms && dictionaryData.synonyms.length > 0 ? (
                    <div className="flex gap-2 mt-1 flex-wrap">
                        {dictionaryData.synonyms.map((s, index) => (
                            <span key={index} className="px-3 py-1 rounded-full bg-black/10 text-sm">
                                {s}
                            </span>
                        ))}
                    </div>
      ) : (
        <p className="text-sm italic opacity-60">Nu există sinonime în baza de date.</p>
      )}
    </div>
  </div>
)}
              
              {/* Toolbar Audio */}
              {translatedText && appState === 'idle' && (
                <div className="flex justify-end mt-4">
                  {backendAudioUrl && (
                    <div className="flex items-center gap-1 bg-black/5 rounded-full pr-2 p-1" style={{ border: `1px solid ${theme.cardBorder}`}}>
                      <button onClick={handleManualSpeak} className="p-1 hover:text-pink-500 transition-colors" title="Ascultă din Backend (Azure)">
                        <svg className="w-5 h-5" fill="none" stroke={theme.accent} viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15.536 8.464a5 5 0 010 7.072m2.828-9.9a9 9 0 010 12.728M5.586 15H4a1 1 0 01-1-1v-4a1 1 0 011-1h1.586l4.707-4.707C10.923 3.663 12 4.109 12 5v14c0 .891-1.077 1.337-1.707.707L5.586 15z"></path></svg>
                      </button>
                      <button onClick={() => setPlaybackSpeed(s => s === 1 ? 0.5 : s === 0.5 ? 1.5 : 1)} className="text-xs font-bold transition-colors w-7 text-center" style={{ color: theme.textMuted }}>{playbackSpeed}x</button>
                    </div>
                  )}
                </div>
              )}
            </div>

            {/* Buton Trimitere Principal */}
            <div className="absolute -bottom-10 left-1/2 transform -translate-x-1/2 z-40">
              <button
                onClick={isTextMode ? handleTextAction : toggleRecording} disabled={appState === 'processing'}
                className="group flex items-center justify-center shadow-xl disabled:opacity-50"
                style={{
                  width: '80px', height: '80px', borderRadius: '50%',
                  background: isTextMode && appState === 'idle' ? 'linear-gradient(135deg, #a855f7 0%, #c084fc 100%)' : appState === 'listening' ? 'linear-gradient(135deg, #ec4899 0%, #f472b6 100%)' : 'linear-gradient(135deg, #D4A5C4 0%, #E8C4D9 100%)',
                  border: `4px solid ${theme.bg}`, cursor: appState === 'processing' ? 'wait' : 'pointer',
                  animation: appState === 'listening' ? 'pulse-pro 2s infinite' : 'none',
                }}
              >
                <span className="transform transition-transform group-hover:scale-110 text-white flex items-center justify-center">
                  {appState === 'processing' ? <span className="text-2xl">⏳</span> : isTextMode ? <svg className="w-8 h-8 ml-1" viewBox="0 0 24 24" fill="currentColor"><path d="M3.478 2.404a.75.75 0 00-.926.941l2.432 7.905H13.5a.75.75 0 010 1.5H4.984l-2.432 7.905a.75.75 0 00.926.94 60.519 60.519 0 0018.445-8.986.75.75 0 000-1.218z" /></svg> : appState === 'listening' ? <span className="text-3xl">⏹️</span> : <span className="text-3xl">🎤</span>}
                </span>
              </button>
            </div>
          </div>
        </div>
      </div>
      
      {/* SIDEBAR ISTORIC */}
      <div className={`fixed top-0 right-0 h-full w-[360px] shadow-2xl z-50 transform transition-all duration-500 ${isSidebarOpen ? 'translate-x-0' : 'translate-x-full'}`} style={{ background: isDark ? 'rgba(15, 23, 42, 0.98)' : 'rgba(255, 255, 255, 0.98)', borderLeft: `1px solid ${theme.cardBorder}` }}>
        <div className="p-6 h-full flex flex-col">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-xl font-bold" style={{ color: theme.textMain }}>Activitate</h2>
            <button onClick={() => setIsSidebarOpen(false)} className="hover:text-pink-500" style={{ color: theme.textMuted }}>X</button>
          </div>
          <div className="flex-1 overflow-y-auto custom-scrollbar pr-2 flex flex-col gap-4">
             {messages.map((msg) => (
                <div key={msg.id} className="p-4 rounded-xl border relative" style={{ background: isDark ? 'rgba(255,255,255,0.03)' : '#f9fafb', borderColor: theme.cardBorder }}>
                  <span className="text-[10px] font-bold uppercase tracking-widest opacity-60" style={{ color: theme.textMuted }}>{msg.from} → {msg.to}</span>
                  <p className="text-sm font-medium mt-1" style={{ color: theme.textMain }}>{msg.original}</p>
                  <p className="text-md font-bold mt-1" style={{ color: theme.accent }}>{msg.translated}</p>
                </div>
              ))}
          </div>
        </div>
      </div>

      <style>{`
        .dark-bubble { background: linear-gradient(135deg, rgba(30,41,59,0.95) 0%, rgba(15,23,42,0.9) 100%) !important; border-color: rgba(255,255,255,0.1) !important; }
        .dark-bubble::after { background: linear-gradient(135deg, rgba(30,41,59,0.95) 0%, rgba(15,23,42,0.9) 100%) !important; border-color: rgba(255,255,255,0.1) !important; }
        @keyframes pulse-pro { 0% { box-shadow: 0 0 0 0 rgba(236, 72, 153, 0.4); } 70% { box-shadow: 0 0 0 20px rgba(236, 72, 153, 0); } 100% { box-shadow: 0 0 0 0 rgba(236, 72, 153, 0); } }
        .audio-visualizer { display: flex; align-items: center; justify-content: center; gap: 6px; height: 40px; }
        .bar { width: 6px; background: #D4A5C4; border-radius: 4px; animation: soundwave 1s ease-in-out infinite; }
        .bar:nth-child(1) { animation-delay: 0.1s; } .bar:nth-child(2) { animation-delay: 0.3s; } .bar:nth-child(3) { animation-delay: 0.0s; } .bar:nth-child(4) { animation-delay: 0.2s; }
        @keyframes soundwave { 0%, 100% { height: 8px; } 50% { height: 32px; } }
        .custom-scrollbar::-webkit-scrollbar { width: 6px; } .custom-scrollbar::-webkit-scrollbar-track { background: transparent; } .custom-scrollbar::-webkit-scrollbar-thumb { background: rgba(211, 154, 197, 0.3); border-radius: 10px; }
      `}</style>
    </div>
  )
}