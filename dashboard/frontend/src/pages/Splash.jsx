import React, { useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import '../styles/splash.css';

/* -----------------------------------------------------------------------
   Hurricane particle system — spiraling particles emanating from center
   with arms + ambient drift particles.  Pure canvas, zero external assets.
   ----------------------------------------------------------------------- */

class HurricaneSystem {
  constructor(canvas) {
    this.canvas = canvas;
    this.ctx = canvas.getContext('2d');
    this.spiralParticles = [];
    this.SPIRAL_COUNT = 500;
    this.animId = null;
    this.time = 0;
    this._resize();
    this._init();
  }

  _resize() {
    this.w = this.canvas.width = window.innerWidth;
    this.h = this.canvas.height = window.innerHeight;
    this.cx = this.w / 2;
    this.cy = this.h * 0.55; // slightly below center so text stays clear
  }

  _init() {
    this.spiralParticles = [];
    for (let i = 0; i < this.SPIRAL_COUNT; i++) {
      this.spiralParticles.push(this._spawnSpiral());
    }
  }

  _spawnSpiral() {
    const arm = Math.floor(Math.random() * 6);
    const maxR = Math.max(this.w, this.h) * 0.7;
    const r = 30 + Math.random() * maxR;
    const angleOffset = (arm / 6) * Math.PI * 2;
    const spiralTightness = 0.06; // looser spiral = wider spread
    const theta = angleOffset + r * spiralTightness + (Math.random() - 0.5) * 1.2;

    return {
      r,
      theta,
      angularSpeed: (0.001 + 0.004 / (1 + r * 0.003)) * (0.7 + Math.random() * 0.6),
      drift: (Math.random() - 0.5) * 0.08,
      size: 0.4 + Math.random() * 1.2,
      alpha: 0.04 + Math.random() * 0.18,
      life: Math.random() * 400,
      maxLife: 300 + Math.random() * 300,
    };
  }

  start() {
    const tick = () => {
      this.time++;
      const { ctx, w, h, cx, cy } = this;

      // Fade trail
      ctx.fillStyle = 'rgba(0, 0, 0, 0.04)';
      ctx.fillRect(0, 0, w, h);

      const maxR = Math.max(w, h) * 0.75;

      // Draw spiral particles
      for (const p of this.spiralParticles) {
        p.theta += p.angularSpeed;
        p.r += p.drift;
        p.life++;

        if (p.life > p.maxLife || p.r < 15 || p.r > maxR) {
          Object.assign(p, this._spawnSpiral());
          p.life = 0;
          continue;
        }

        const fade = p.life < 40 ? p.life / 40
          : p.life > p.maxLife - 50 ? (p.maxLife - p.life) / 50
          : 1;
        const a = p.alpha * fade;

        const x = cx + Math.cos(p.theta) * p.r;
        const y = cy + Math.sin(p.theta) * p.r;

        // Dim blue tint — avoids pure white that obscures text
        const colorBlend = Math.min(p.r / (maxR * 0.6), 1);
        const rr = Math.floor(100 + (1 - colorBlend) * 80);
        const gg = Math.floor(140 + (1 - colorBlend) * 60);
        const bb = Math.floor(200 + (1 - colorBlend) * 55);

        ctx.fillStyle = `rgba(${rr},${gg},${bb},${a})`;
        ctx.beginPath();
        ctx.arc(x, y, p.size, 0, Math.PI * 2);
        ctx.fill();
      }

      // Subtle eye glow
      const eyeGrad = ctx.createRadialGradient(cx, cy, 0, cx, cy, 60);
      eyeGrad.addColorStop(0, 'rgba(100, 160, 255, 0.03)');
      eyeGrad.addColorStop(1, 'rgba(100, 160, 255, 0)');
      ctx.fillStyle = eyeGrad;
      ctx.beginPath();
      ctx.arc(cx, cy, 60, 0, Math.PI * 2);
      ctx.fill();

      this.animId = requestAnimationFrame(tick);
    };
    tick();
  }

  stop() {
    if (this.animId) cancelAnimationFrame(this.animId);
  }

  resize() {
    this._resize();
    this._init();
  }
}


export default function Splash() {
  const canvasRef = useRef(null);
  const systemRef = useRef(null);
  const navigate = useNavigate();

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const system = new HurricaneSystem(canvas);
    systemRef.current = system;
    system.start();
    const onResize = () => system.resize();
    window.addEventListener('resize', onResize);
    return () => {
      system.stop();
      window.removeEventListener('resize', onResize);
    };
  }, []);

  return (
    <div className="splash">
      <canvas ref={canvasRef} className="splash-canvas" />

      <div className="splash-overlay">
        <div className="splash-badge">QM 2026 CAPSTONE</div>
        <h1 className="splash-title">Hurricane Impact</h1>
        <h2 className="splash-subtitle-line">on Florida Real Estate</h2>
        <p className="splash-subtitle">
          Quantitative analysis of hurricane events against Zillow housing
          metrics across Florida metropolitan statistical areas, 1995 &ndash; 2025
        </p>
        <div className="splash-stats">
          <div className="splash-stat">
            <div className="stat-value">13+</div>
            <div className="stat-label">Data Sources</div>
          </div>
          <div className="splash-divider" />
          <div className="splash-stat">
            <div className="stat-value">1995 &ndash; 2025</div>
            <div className="stat-label">Date Range</div>
          </div>
          <div className="splash-divider" />
          <div className="splash-stat">
            <div className="stat-value">FL</div>
            <div className="stat-label">Focus Region</div>
          </div>
        </div>
        <button className="splash-enter" onClick={() => navigate('/overview')}>
          Launch Dashboard
          <span className="splash-enter-arrow">&rarr;</span>
        </button>
      </div>
    </div>
  );
}
