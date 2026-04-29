import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import { useDropzone } from 'react-dropzone';
import './App.css';

function App() {
  const [selectedImage, setSelectedImage] = useState(null);
  const [preview, setPreview] = useState(null);
  const [detections, setDetections] = useState([]);
  const [topDetections, setTopDetections] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [showResult, setShowResult] = useState(false);
  const [darkMode, setDarkMode] = useState(true);
  const canvasRef = useRef(null);
  const [imageDimensions, setImageDimensions] = useState({ width: 0, height: 0 });

  // Toggle theme
  useEffect(() => {
    if (darkMode) {
      document.body.setAttribute('data-theme', 'dark');
    } else {
      document.body.setAttribute('data-theme', 'light');
    }
  }, [darkMode]);

  const onDrop = (acceptedFiles) => {
    const file = acceptedFiles[0];
    if (file) {
      setSelectedImage(file);
      const reader = new FileReader();
      reader.onloadend = () => {
        setPreview(reader.result);
        setDetections([]);
        setTopDetections([]);
        setError(null);
        setShowResult(false);
        setImageDimensions({ width: 0, height: 0 });
      };
      reader.readAsDataURL(file);
    }
  };

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/*': ['.jpeg', '.jpg', '.png', '.bmp', '.tiff']
    },
    maxFiles: 1
  });

  const drawBoundingBoxes = (imageSrc, detectionsData) => {
    const img = new Image();
    img.onload = () => {
      const canvas = canvasRef.current;
      const ctx = canvas.getContext('2d');
      
      canvas.width = img.width;
      canvas.height = img.height;
      setImageDimensions({ width: img.width, height: img.height });
      
      ctx.drawImage(img, 0, 0);
      
      // Gambar semua deteksi (bukan hanya top 3 untuk visualisasi)
      detectionsData.forEach((detection, index) => {
        const className = detection.class_name;
        const [x1, y1, x2, y2] = detection.bbox;
        const color = className === 'Organik' ? '#00c853' : '#ff6d00';
        const confidencePercent = (detection.confidence * 100).toFixed(1);
        
        // Tambahkan nomor urut pada label
        const labelText = `${index + 1}. ${className === 'Organik' ? '🌿' : '🗑️'} ${className} (${confidencePercent}%)`;
        
        // Ukuran label
        ctx.font = 'bold 15px "Space Grotesk", "Sora", sans-serif';
        const textWidth = ctx.measureText(labelText).width;
        const textHeight = 28;
        
        // Posisi label di ATAS kotak
        let labelX = x1;
        let labelY = y1 - 5;
        
        // Jika label keluar dari canvas bagian atas, taruh di dalam kotak bagian atas
        if (labelY - textHeight < 0) {
          labelY = y1 + 5;
        }
        
        // Background label dengan efek glow
        ctx.shadowBlur = 0;
        ctx.fillStyle = color;
        ctx.globalAlpha = 0.9;
        
        // Draw rounded rectangle untuk background label
        ctx.beginPath();
        ctx.roundRect(labelX, labelY - textHeight, textWidth + 16, textHeight, 8);
        ctx.fill();
        
        // Draw text
        ctx.globalAlpha = 1;
        ctx.fillStyle = '#ffffff';
        ctx.font = 'bold 13px "Space Grotesk", "Sora", sans-serif';
        ctx.fillText(labelText, labelX + 8, labelY - 8);
        
        // Draw bounding box dengan garis tebal
        ctx.strokeStyle = color;
        ctx.lineWidth = 3;
        ctx.strokeRect(x1, y1, x2 - x1, y2 - y1);
        
        // Draw corner accents (retro style)
        ctx.strokeStyle = color;
        ctx.lineWidth = 2.5;
        
        // Top-left corner
        ctx.beginPath();
        ctx.moveTo(x1, y1 + 10);
        ctx.lineTo(x1, y1);
        ctx.lineTo(x1 + 10, y1);
        ctx.stroke();
        
        // Top-right corner
        ctx.beginPath();
        ctx.moveTo(x2 - 10, y1);
        ctx.lineTo(x2, y1);
        ctx.lineTo(x2, y1 + 10);
        ctx.stroke();
        
        // Bottom-left corner
        ctx.beginPath();
        ctx.moveTo(x1, y2 - 10);
        ctx.lineTo(x1, y2);
        ctx.lineTo(x1 + 10, y2);
        ctx.stroke();
        
        // Bottom-right corner
        ctx.beginPath();
        ctx.moveTo(x2 - 10, y2);
        ctx.lineTo(x2, y2);
        ctx.lineTo(x2, y2 - 10);
        ctx.stroke();
      });
      
      setShowResult(true);
    };
    img.src = imageSrc;
  };

  // Helper untuk rounded rectangle
  if (!CanvasRenderingContext2D.prototype.roundRect) {
    CanvasRenderingContext2D.prototype.roundRect = function(x, y, w, h, r) {
      if (w < 2 * r) r = w / 2;
      if (h < 2 * r) r = h / 2;
      this.moveTo(x+r, y);
      this.lineTo(x+w-r, y);
      this.quadraticCurveTo(x+w, y, x+w, y+r);
      this.lineTo(x+w, y+h-r);
      this.quadraticCurveTo(x+w, y+h, x+w-r, y+h);
      this.lineTo(x+r, y+h);
      this.quadraticCurveTo(x, y+h, x, y+h-r);
      this.lineTo(x, y+r);
      this.quadraticCurveTo(x, y, x+r, y);
      return this;
    };
  }

  const handleDetect = async () => {
    if (!selectedImage) {
      setError('Please select an image first');
      return;
    }

    setLoading(true);
    setError(null);

    const formData = new FormData();
    formData.append('file', selectedImage);

    try {
      const response = await axios.post('http://localhost:8000/detect', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        timeout: 30000,
      });

      const allDetections = response.data.detections;
      console.log('All Detections:', allDetections);
      
      // Sort by confidence (tertinggi ke terendah) dan ambil top 3
      const sortedDetections = [...allDetections].sort((a, b) => b.confidence - a.confidence);
      const top3Detections = sortedDetections.slice(0, 3);
      
      setDetections(allDetections);
      setTopDetections(top3Detections);
      
      // Draw bounding boxes dengan top 3 detections (paling mencolok)
      setTimeout(() => {
        drawBoundingBoxes(preview, top3Detections);
      }, 100);
      
    } catch (err) {
      setError('Error detecting waste: ' + (err.response?.data?.detail || err.message));
      console.error('Detection error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleClear = () => {
    setSelectedImage(null);
    setPreview(null);
    setDetections([]);
    setTopDetections([]);
    setError(null);
    setShowResult(false);
    setImageDimensions({ width: 0, height: 0 });
    const canvas = canvasRef.current;
    if (canvas) {
      const ctx = canvas.getContext('2d');
      ctx.clearRect(0, 0, canvas.width, canvas.height);
    }
  };

  const toggleTheme = () => {
    setDarkMode(!darkMode);
  };

  // Hitung statistik dari top detections
  const organicCount = topDetections.filter(d => d.class_name === 'Organik').length;
  const inorganicCount = topDetections.filter(d => d.class_name === 'Anorganik').length;
  const avgConfidence = topDetections.length > 0 
    ? (topDetections.reduce((sum, d) => sum + d.confidence, 0) / topDetections.length * 100).toFixed(1)
    : 0;

  return (
    <div className={`app ${darkMode ? 'dark-theme' : 'light-theme'}`}>
      {/* Preloader */}
      <div className={`preloader ${!loading ? 'hidden' : ''}`}>
        <div className="preloader-content">
          <div className="cube-loader">
            <div className="cube">
              <div className="cube-face cube-face-front"></div>
              <div className="cube-face cube-face-back"></div>
              <div className="cube-face cube-face-right"></div>
              <div className="cube-face cube-face-left"></div>
              <div className="cube-face cube-face-top"></div>
              <div className="cube-face cube-face-bottom"></div>
            </div>
          </div>
          <div className="loading-text">
            <span>M</span><span>E</span><span>M</span><span>P</span><span>R</span><span>O</span><span>S</span><span>E</span><span>S</span>
          </div>
          <div className="loading-subtext">
            Mendeteksi sampah...
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="navbar">
        <div className="container nav-container">
          <div className="logo">
            <div className="logo-3d">
              <span className="logo-text">♻️</span>
            </div>
            <span className="logo-name">Waste<span className="gradient">Detector</span></span>
          </div>
          <div className="nav-actions">
            <button className="theme-toggle" onClick={toggleTheme} aria-label="Toggle theme">
              {darkMode ? '☀️' : '🌙'}
            </button>
            <button className="btn btn-primary" onClick={() => document.getElementById('detector').scrollIntoView({ behavior: 'smooth' })}>
              Detect Now
            </button>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section id="home" className="hero">
        <div className="hero-bg">
          <div className="floating-shapes">
            <div className="shape shape-1"></div>
            <div className="shape shape-2"></div>
            <div className="shape shape-3"></div>
            <div className="shape shape-4"></div>
          </div>
        </div>
        <div className="container hero-container">
          <div className="hero-content">
            <div className="hero-badge">
              <span className="badge-icon">🌍</span>
              <span>AI-Powered Waste Detection</span>
            </div>
            <h1 className="hero-title">
              <span className="gradient-text">Detect & Classify</span><br />
              Organic & Inorganic Waste
            </h1>
            <p className="hero-description">
              Upload images to identify and classify waste types using advanced AI.
              Get instant results with bounding boxes and confidence scores.
            </p>
            <div className="hero-buttons">
              <button className="btn btn-primary btn-large" onClick={() => document.getElementById('detector').scrollIntoView({ behavior: 'smooth' })}>
                Start Detecting
                <span className="btn-arrow">→</span>
              </button>
            </div>
          </div>
          <div className="hero-visual">
            <div className="visual-3d">
              <div className="sphere-container">
                <div className="sphere"></div>
                <div className="sphere-ring ring-1"></div>
                <div className="sphere-ring ring-2"></div>
                <div className="sphere-ring ring-3"></div>
              </div>
              <div className="floating-cards">
                <div className="float-card card-1">
                  <div className="card-icon">🌿</div>
                  <p>Organic</p>
                </div>
                <div className="float-card card-2">
                  <div className="card-icon">🗑️</div>
                  <p>Inorganic</p>
                </div>
                <div className="float-card card-3">
                  <div className="card-icon">🤖</div>
                  <p>AI Powered</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Detector Section */}
      <section id="detector" className="detector-section">
        <div className="container">
          <div className="section-header">
            <span className="section-badge">Waste Detector</span>
            <h2 className="section-title">Upload & Detect</h2>
            <p className="section-description">Upload an image to identify organic and inorganic waste</p>
          </div>
          
          <div className="detector-container">
            {/* Upload Area */}
            <div className="upload-card">
              <div 
                {...getRootProps()} 
                className={`dropzone ${isDragActive ? 'active' : ''}`}
              >
                <input {...getInputProps()} />
                <div className="dropzone-content">
                  <div className="dropzone-icon">📸</div>
                  {isDragActive ? (
                    <p>Drop the image here...</p>
                  ) : (
                    <>
                      <p>Drag & drop an image here</p>
                      <small>or click to select</small>
                    </>
                  )}
                  <div className="format-badge">
                    <span>JPG</span>
                    <span>PNG</span>
                    <span>BMP</span>
                    <span>TIFF</span>
                  </div>
                </div>
              </div>
              
              {preview && (
                <div className="button-group">
                  <button 
                    onClick={handleDetect} 
                    disabled={loading}
                    className="btn btn-primary btn-block"
                  >
                    {loading ? '🔄 DETECTING...' : '🔍 DETECT WASTE'}
                  </button>
                  <button onClick={handleClear} className="btn btn-outline btn-block">
                    🗑️ CLEAR
                  </button>
                </div>
              )}
              
              {error && <div className="error-message">⚠️ {error}</div>}
            </div>

            {/* Result Area */}
            <div className="result-card">
              <h3 className="result-title">
                Detection Result 
                {topDetections.length > 0 && (
                  <span className="result-count"> ({topDetections.length} item terdeteksi)</span>
                )}
              </h3>
              <div className="canvas-container">
                {preview ? (
                  <canvas ref={canvasRef} className="detection-canvas" />
                ) : (
                  <div className="placeholder">
                    <div className="placeholder-icon">🖼️</div>
                    <p>No image loaded</p>
                    <small>Upload an image to start detection</small>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Top 3 Detection Summary Card */}
          {showResult && topDetections.length > 0 && (
            <div className="summary-card">
              <h3 className="summary-title">🎯 Ringkasan Deteksi (3 Teratas)</h3>
              <div className="summary-stats">
                <div className="summary-stat">
                  <span className="stat-icon">🌿</span>
                  <div>
                    <div className="stat-label">Organik</div>
                    <div className="stat-value">{organicCount}</div>
                  </div>
                </div>
                <div className="summary-stat">
                  <span className="stat-icon">🗑️</span>
                  <div>
                    <div className="stat-label">Anorganik</div>
                    <div className="stat-value">{inorganicCount}</div>
                  </div>
                </div>
                <div className="summary-stat">
                  <span className="stat-icon">📊</span>
                  <div>
                    <div className="stat-label">Rata-rata Confidence</div>
                    <div className="stat-value">{avgConfidence}%</div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Top 3 Detection Details List */}
          {showResult && topDetections.length > 0 && (
            <div className="details-card">
              <h3 className="details-title">📋 3 Sampah Paling Mencolok</h3>
              <div className="detections-list">
                {topDetections.map((detection, idx) => (
                  <div key={idx} className={`detection-item ${detection.class_name.toLowerCase()} top-${idx + 1}`}>
                    <div className="detection-rank">
                      <span className="rank-badge">#{idx + 1}</span>
                    </div>
                    <div className="detection-info">
                      <span className="detection-icon">
                        {detection.class_name === 'Organik' ? '🌿' : '🗑️'}
                      </span>
                      <span className="detection-class">{detection.class_name}</span>
                    </div>
                    <div className="detection-confidence">
                      Confidence: {(detection.confidence * 100).toFixed(1)}%
                      <div className="confidence-bar">
                        <div 
                          className="confidence-fill" 
                          style={{ width: `${detection.confidence * 100}%` }}
                        />
                      </div>
                    </div>
                    <div className="detection-bbox">
                      Posisi: [{detection.bbox[0]}, {detection.bbox[1]}]
                    </div>
                  </div>
                ))}
              </div>
              {detections.length > 3 && (
                <div className="more-detections-note">
                  <span>ℹ️ Plus {detections.length - 3} deteksi lain dengan confidence lebih rendah</span>
                </div>
              )}
            </div>
          )}

          {/* No Detection Found */}
          {showResult && topDetections.length === 0 && preview && (
            <div className="details-card no-detection">
              <div className="no-detection-content">
                <span className="no-detection-icon">🔍</span>
                <h3>Tidak Ada Sampah Terdeteksi</h3>
                <p>Tidak ada sampah organik atau anorganik yang terdeteksi di gambar ini.</p>
                <small>Coba upload gambar lain dengan objek sampah yang lebih jelas.</small>
              </div>
            </div>
          )}
        </div>
      </section>

      {/* Features Section */}
      <section className="features">
        <div className="container">
          <div className="section-header">
            <span className="section-badge">Features</span>
            <h2 className="section-title">Why Choose Our AI Detector</h2>
            <p className="section-description">Advanced technology for accurate waste classification</p>
          </div>
          <div className="features-grid">
            <div className="feature-card">
              <div className="feature-icon">
                <div className="icon-3d">🧠</div>
              </div>
              <h3 className="feature-title">Smart AI Detection</h3>
              <p className="feature-description">Powered by MobileNetV2 deep learning model for accurate waste classification.</p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">
                <div className="icon-3d">🎯</div>
              </div>
              <h3 className="feature-title">Top 3 Highlight</h3>
              <p className="feature-description">Menampilkan 3 sampah paling mencolok dengan confidence tertinggi.</p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">
                <div className="icon-3d">⚡</div>
              </div>
              <h3 className="feature-title">Real-Time Results</h3>
              <p className="feature-description">Get instant detection results with confidence scores for each item.</p>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="footer">
        <div className="container">
          <div className="footer-content">
            <div className="footer-column">
              <div className="footer-logo">
                <div className="logo-3d">
                  <span className="logo-text">♻️</span>
                </div>
                <span className="logo-name">Waste<span className="gradient">Detector</span></span>
              </div>
              <p className="footer-description">AI-powered waste detection system for a cleaner environment. Identify and classify organic and inorganic waste instantly.</p>
            </div>
            <div className="footer-column">
              <h4 className="footer-title">Quick Links</h4>
              <ul className="footer-links">
                <li><a href="#home">Home</a></li>
                <li><a href="#detector">Detector</a></li>
                <li><a href="#features">Features</a></li>
              </ul>
            </div>
            <div className="footer-column">
              <h4 className="footer-title">Technology</h4>
              <ul className="footer-links">
                <li><a href="#">MobileNetV2</a></li>
                <li><a href="#">PyTorch</a></li>
                <li><a href="#">FastAPI</a></li>
                <li><a href="#">React</a></li>
              </ul>
            </div>
          </div>
          <div className="footer-bottom">
            <p>&copy; 2025 Waste Detector - Clean Environment, Better Future</p>
          </div>
        </div>
      </footer>

      {/* Scroll to Top Button */}
      <button className="scroll-top" id="scrollTop" onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })}>↑</button>
    </div>
  );
}

export default App;