import React, { useState } from 'react';
import { Upload, ArrowLeft, ArrowRight, Loader2, FileText, CheckCircle, Sparkles, BookOpen } from 'lucide-react';
import './App.css';

const App = () => {
  const [file, setFile] = useState(null);
  const [flashcards, setFlashcards] = useState([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isFlipped, setIsFlipped] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files.length > 0) {
      setFile(e.target.files[0]);
      setError('');
    }
  };

  const handleGenerate = async () => {
    if (!file) return;

    setIsLoading(true);
    setError('');
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch('http://localhost:3001/api/upload', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) throw new Error('Generation failed');

      const data = await response.json();
      if (data.flashcards && data.flashcards.length > 0) {
        setFlashcards(data.flashcards);
        setCurrentIndex(0);
        setIsFlipped(false);
      } else {
        setError("No flashcards could be generated from this content.");
      }
    } catch (err) {
      console.error(err);
      setError("Error connecting to server. Is the backend running?");
    } finally {
      setIsLoading(false);
    }
  };

  const handleNext = (e) => {
    e.stopPropagation();
    if (currentIndex < flashcards.length - 1) {
      setIsFlipped(false);
      setTimeout(() => setCurrentIndex(c => c + 1), 200);
    }
  };

  const handlePrev = (e) => {
    e.stopPropagation();
    if (currentIndex > 0) {
      setIsFlipped(false);
      setTimeout(() => setCurrentIndex(c => c - 1), 200);
    }
  };

  const resetApp = () => {
    if (window.confirm("Upload a new file? Current cards will be cleared.")) {
      setFlashcards([]);
      setFile(null);
      setIsFlipped(false);
      setCurrentIndex(0);
    }
  };

  return (
    <>
      {/* --- Website Navbar --- */}
      <nav className="navbar">
        <div className="nav-brand">
          <BookOpen size={28} color="#F16D34" />
          <div>Flashcards<span>Gen</span></div>
        </div>
        
        {flashcards.length > 0 && (
          <div className="file-status-badge">
            <FileText size={16} color="#161E54" />
            <span className="file-name" title={file?.name}>{file?.name}</span>
            <span style={{color:'#ccc'}}>|</span>
            <button onClick={resetApp} className="btn-reset-small">New File</button>
          </div>
        )}
      </nav>

      {/* --- Main Content Area --- */}
      <main className="main-content">
        
        {/* VIEW 1: LANDING / UPLOAD */}
        {flashcards.length === 0 && (
          <div className="landing-container">
            <div className="headline">Turn PDFs into <br/> <span style={{color: '#F16D34'}}>Knowledge</span> instantly.</div>
            <p className="subheadline">
              Upload your study notes, textbooks, or research papers and let our AI generate rigorous flashcards for you.
            </p>

            <div className="upload-card">
              <div className="drop-zone">
                <input 
                  type="file" 
                  accept=".pdf" 
                  onChange={handleFileChange} 
                  className="file-input"
                />
                {file ? (
                  <>
                    <CheckCircle size={40} color="#F16D34" style={{marginBottom: 10}} />
                    <p style={{fontWeight: 'bold', color: '#161E54'}}>{file.name}</p>
                    <p style={{fontSize: '0.8rem', color: '#64748b'}}>Ready to process</p>
                  </>
                ) : (
                  <>
                    <Upload size={40} color="#161E54" style={{marginBottom: 10, opacity: 0.5}} />
                    <p style={{fontWeight: 'bold', color: '#161E54'}}>Click to Browse PDF</p>
                    <p style={{fontSize: '0.8rem', color: '#64748b'}}>Max file size 10MB</p>
                  </>
                )}
              </div>

              {error && <div style={{color: '#dc2626', marginBottom: '1rem', fontSize: '0.9rem'}}>{error}</div>}

              <button 
                className="btn-primary" 
                onClick={handleGenerate}
                disabled={!file || isLoading}
              >
                {isLoading ? <><Loader2 className="animate-spin" /> Generating...</> : <><Sparkles size={18} /> Generate Flashcards</>}
              </button>
            </div>
          </div>
        )}

        {/* VIEW 2: FLASHCARDS WORKSPACE */}
        {flashcards.length > 0 && (
          <div className="workspace-container">
            
            {/* Progress Bar */}
            <div className="progress-bar">
              <div 
                className="progress-fill" 
                style={{width: `${((currentIndex + 1) / flashcards.length) * 100}%`}}
              ></div>
            </div>

            {/* 3D Card */}
            <div className="card-container">
              <div 
                className={`card-inner ${isFlipped ? 'flipped' : ''}`}
                onClick={() => setIsFlipped(!isFlipped)}
              >
                {/* Front */}
                <div className="card-face card-front">
                  <div>
                    <span className="card-label">Question {currentIndex + 1}</span>
                    <div className="card-content-scroll" style={{overflow: 'hidden'}}>
                      {/* Front content usually short, but just in case */}
                      {flashcards[currentIndex].question}
                    </div>
                  </div>
                </div>

                {/* Back */}
                <div className="card-face card-back">
                  <span className="card-label" style={{color: '#FF986A'}}>Answer</span>
                  {/* SCROLLABLE CONTENT AREA */}
                  <div className="card-content-scroll">
                    {flashcards[currentIndex].answer}
                  </div>
                </div>
              </div>
            </div>

            {/* Controls */}
            <div className="controls">
              <button 
                className="nav-btn" 
                onClick={handlePrev} 
                disabled={currentIndex === 0}
              >
                <ArrowLeft size={24} />
              </button>
              
              <span className="card-counter">
                {currentIndex + 1} / {flashcards.length}
              </span>
              
              <button 
                className="nav-btn primary" 
                onClick={handleNext} 
                disabled={currentIndex === flashcards.length - 1}
              >
                <ArrowRight size={24} />
              </button>
            </div>
            <p className="helper-text">Tap card to flip • Use arrows to navigate</p>

          </div>
        )}

      </main>

      {/* --- Footer --- */}
      <footer className="footer">
        © 2024 FlashcardsGen AI. Built for smarter learning.
      </footer>
    </>
  );
};

export default App;