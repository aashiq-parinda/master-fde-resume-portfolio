#!/usr/bin/env python3
"""
Generate ultra-premium burgundy SVG assets for Ashraf Khan's portfolio:
1. Taller, bolder, animated Section Headers (viewBox 0 0 880 70)
2. Flagship Project Cards (viewBox 0 0 880 270)
3. Technical Toolkit Card (viewBox 0 0 880 340)
4. Enterprise Benchmarks Card (viewBox 0 0 880 290)
5. Credentials & Certifications Card (viewBox 0 0 880 220)
6. Research Whitepapers Card (viewBox 0 0 880 230)
"""

import os

COMMON_DEFS = """
    <!-- Background Gradients -->
    <linearGradient id="bgGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#12060E" />
      <stop offset="50%" stop-color="#1B0A15" />
      <stop offset="100%" stop-color="#0E040A" />
    </linearGradient>

    <linearGradient id="cardBgGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#160812" />
      <stop offset="60%" stop-color="#1F0D1A" />
      <stop offset="100%" stop-color="#11050D" />
    </linearGradient>

    <!-- Border Gradients -->
    <linearGradient id="borderGrad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#701A3D" stop-opacity="0.9" />
      <stop offset="50%" stop-color="#A82C5D" stop-opacity="0.6" />
      <stop offset="100%" stop-color="#451126" stop-opacity="0.8" />
    </linearGradient>

    <!-- Animated Shimmer Beam -->
    <linearGradient id="beamGrad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#451126" stop-opacity="0" />
      <stop offset="35%" stop-color="#701A3D" stop-opacity="0.8" />
      <stop offset="50%" stop-color="#F8F0F3" stop-opacity="1" />
      <stop offset="65%" stop-color="#A82C5D" stop-opacity="0.8" />
      <stop offset="100%" stop-color="#451126" stop-opacity="0" />
      <animate attributeName="x1" values="-100%;100%;-100%" dur="8s" repeatCount="indefinite" />
      <animate attributeName="x2" values="0%;200%;0%" dur="8s" repeatCount="indefinite" />
    </linearGradient>

    <!-- Subdued Grid Pattern -->
    <pattern id="cardGrid" width="24" height="24" patternUnits="userSpaceOnUse">
      <path d="M 24 0 L 0 0 0 24" fill="none" stroke="#451126" stroke-width="0.55" stroke-opacity="0.28" />
      <circle cx="24" cy="24" r="0.65" fill="#A82C5D" fill-opacity="0.3" />
    </pattern>

    <!-- Typography Gradient -->
    <linearGradient id="titleGrad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#FFFFFF" />
      <stop offset="60%" stop-color="#F8F0F3" />
      <stop offset="100%" stop-color="#E5B5C7" />
    </linearGradient>

    <linearGradient id="accentGrad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#FF4D6D" />
      <stop offset="100%" stop-color="#C77B9B" />
    </linearGradient>

    <radialGradient id="cornerAura" cx="90%" cy="10%" r="50%">
      <stop offset="0%" stop-color="#701A3D" stop-opacity="0.35" />
      <stop offset="100%" stop-color="#701A3D" stop-opacity="0" />
    </radialGradient>
"""

COMMON_STYLE = """
    .font-mono { font-family: ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, monospace; }
    .font-sans { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif; }
    .text-title { font-weight: 800; letter-spacing: 1.5px; fill: url(#titleGrad); }
    .text-sub { font-weight: 500; letter-spacing: 0.5px; fill: #C77B9B; }
    .text-desc { font-weight: 400; fill: #E5B5C7; line-height: 1.4; }
    .tag-text { font-size: 11px; font-weight: 600; fill: #F8F0F3; letter-spacing: 0.5px; }
    .metric-val { font-weight: 800; fill: #F8F0F3; letter-spacing: 0.5px; }
    .metric-lbl { font-size: 10px; font-weight: 600; text-transform: uppercase; letter-spacing: 1.2px; fill: #A82C5D; }
"""

def generate_header(index_str, title_str, subtitle_str, tag_str, out_path):
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 880 72" width="100%" height="auto" role="img" aria-label="{title_str}">
  <defs>
{COMMON_DEFS}
  </defs>
  <style>
{COMMON_STYLE}
  </style>

  <!-- Container Box -->
  <rect x="1" y="1" width="878" height="70" rx="12" fill="url(#bgGrad)" stroke="url(#borderGrad)" stroke-width="1.2" />
  <rect x="1" y="1" width="878" height="70" rx="12" fill="url(#cardGrid)" />
  <rect x="1" y="1" width="878" height="70" rx="12" fill="url(#cornerAura)" />

  <!-- Left Glowing Indicator -->
  <g transform="translate(26, 36)">
    <circle cx="0" cy="0" r="9" fill="#701A3D" opacity="0.4">
      <animate attributeName="r" values="7;11;7" dur="3s" repeatCount="indefinite" />
      <animate attributeName="opacity" values="0.4;0.15;0.4" dur="3s" repeatCount="indefinite" />
    </circle>
    <circle cx="0" cy="0" r="5" fill="#701A3D" />
    <circle cx="0" cy="0" r="2.5" fill="#FF4D6D" />
  </g>

  <!-- Section Index Badge -->
  <g transform="translate(48, 26)">
    <rect x="0" y="0" width="70" height="20" rx="5" fill="#451126" stroke="#701A3D" stroke-width="0.8" />
    <text x="35" y="14" class="font-mono" font-size="11" font-weight="700" fill="#E5B5C7" text-anchor="middle" letter-spacing="1">[{index_str}]</text>
  </g>

  <!-- Title & Subtitle -->
  <text x="130" y="40" class="font-sans text-title" font-size="16">{title_str}</text>
  <text x="130" y="58" class="font-sans text-sub" font-size="11.5">✦ {subtitle_str}</text>

  <!-- Right Technical Status Badge -->
  <g transform="translate(730, 24)">
    <rect x="0" y="0" width="124" height="24" rx="6" fill="#1C0A15" stroke="#701A3D" stroke-width="1" />
    <circle cx="14" cy="12" r="3.5" fill="#10B981">
      <animate attributeName="opacity" values="1;0.4;1" dur="2s" repeatCount="indefinite" />
    </circle>
    <text x="68" y="16" class="font-mono" font-size="10.5" font-weight="700" fill="#F8F0F3" text-anchor="middle" letter-spacing="1.2">{tag_str}</text>
  </g>

  <!-- Bottom Animated Shimmer Border -->
  <rect x="20" y="69.5" width="840" height="1.5" fill="#451126" />
  <rect x="20" y="69.5" width="840" height="1.5" fill="url(#beamGrad)" />
</svg>"""
    with open(out_path, "w") as f:
        f.write(svg)
    print(f"Generated header: {out_path}")

def generate_project_arbitrator():
    out_path = "assets/card-project-arbitrator.svg"
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 880 270" width="100%" height="auto" role="img" aria-label="Multi-Agent Dispute Arbitrator">
  <defs>
{COMMON_DEFS}
  </defs>
  <style>
{COMMON_STYLE}
  </style>

  <!-- Outer Card -->
  <rect x="1" y="1" width="878" height="268" rx="16" fill="url(#cardBgGrad)" stroke="url(#borderGrad)" stroke-width="1.4" />
  <rect x="1" y="1" width="878" height="268" rx="16" fill="url(#cardGrid)" />
  <rect x="1" y="1" width="878" height="268" rx="16" fill="url(#cornerAura)" />

  <!-- Top Status Bar -->
  <g transform="translate(24, 20)">
    <!-- Category Pill -->
    <rect x="0" y="0" width="168" height="22" rx="5" fill="#451126" stroke="#701A3D" stroke-width="0.8" />
    <text x="84" y="15" class="font-mono" font-size="10" font-weight="700" fill="#E5B5C7" text-anchor="middle" letter-spacing="1">ARCH-01 // AUTONOMOUS AGENTS</text>

    <!-- Live Status Pill -->
    <rect x="178" y="0" width="144" height="22" rx="5" fill="#1C0A15" stroke="#10B981" stroke-width="0.8" />
    <circle cx="190" cy="11" r="3.5" fill="#10B981">
      <animate attributeName="opacity" values="1;0.4;1" dur="2s" repeatCount="indefinite" />
    </circle>
    <text x="256" y="15" class="font-mono" font-size="10" font-weight="700" fill="#10B981" text-anchor="middle" letter-spacing="1">PRODUCTION STACK</text>
  </g>

  <!-- Project Title -->
  <text x="24" y="74" class="font-sans text-title" font-size="22">Multi-Agent Financial Dispute Arbitrator</text>
  <text x="24" y="96" class="font-sans text-sub" font-size="13">Autonomous Transaction Settlement, Ledger Reconciliation &amp; Fraud Arbitration Engine</text>

  <!-- Tech Stack Pills Row -->
  <g transform="translate(24, 114)">
    <!-- Pill 1 -->
    <rect x="0" y="0" width="104" height="22" rx="4" fill="#2E101E" stroke="#701A3D" stroke-width="0.8" />
    <text x="52" y="15" class="font-sans tag-text" font-size="11" text-anchor="middle">LangGraph</text>
    <!-- Pill 2 -->
    <rect x="112" y="0" width="118" height="22" rx="4" fill="#2E101E" stroke="#701A3D" stroke-width="0.8" />
    <text x="171" y="15" class="font-sans tag-text" font-size="11" text-anchor="middle">DeepSeek-R1</text>
    <!-- Pill 3 -->
    <rect x="238" y="0" width="94" height="22" rx="4" fill="#2E101E" stroke="#701A3D" stroke-width="0.8" />
    <text x="285" y="15" class="font-sans tag-text" font-size="11" text-anchor="middle">FastAPI</text>
    <!-- Pill 4 -->
    <rect x="340" y="0" width="116" height="22" rx="4" fill="#2E101E" stroke="#701A3D" stroke-width="0.8" />
    <text x="398" y="15" class="font-sans tag-text" font-size="11" text-anchor="middle">Apache Kafka</text>
    <!-- Pill 5 -->
    <rect x="464" y="0" width="104" height="22" rx="4" fill="#2E101E" stroke="#701A3D" stroke-width="0.8" />
    <text x="516" y="15" class="font-sans tag-text" font-size="11" text-anchor="middle">PostgreSQL</text>
    <!-- Pill 6 -->
    <rect x="576" y="0" width="100" height="22" rx="4" fill="#2E101E" stroke="#701A3D" stroke-width="0.8" />
    <text x="626" y="15" class="font-sans tag-text" font-size="11" text-anchor="middle">Docker K8s</text>
  </g>

  <!-- Metrics Grid (3 Key Metric Panels) -->
  <!-- Metric Box 1 -->
  <g transform="translate(24, 150)">
    <rect x="0" y="0" width="260" height="76" rx="8" fill="#170712" stroke="#451126" stroke-width="1" />
    <text x="16" y="24" class="font-sans metric-lbl">SIMULATED ARR RECOVERY</text>
    <text x="16" y="52" class="font-sans metric-val" font-size="24">$1.8M ARR</text>
    <text x="16" y="68" class="font-sans" font-size="10.5" fill="#C77B9B">Recovered via automated chargeback auditing</text>
  </g>

  <!-- Metric Box 2 -->
  <g transform="translate(298, 150)">
    <rect x="0" y="0" width="260" height="76" rx="8" fill="#170712" stroke="#451126" stroke-width="1" />
    <text x="16" y="24" class="font-sans metric-lbl">AUTONOMOUS RESOLUTION</text>
    <text x="16" y="52" class="font-sans metric-val" font-size="24">94.2% Rate</text>
    <text x="16" y="68" class="font-sans" font-size="10.5" fill="#C77B9B">Zero human touchpoints across test suites</text>
  </g>

  <!-- Metric Box 3 -->
  <g transform="translate(572, 150)">
    <rect x="0" y="0" width="284" height="76" rx="8" fill="#170712" stroke="#451126" stroke-width="1" />
    <text x="16" y="24" class="font-sans metric-lbl">DECISION LATENCY &amp; SCALE</text>
    <text x="16" y="52" class="font-sans metric-val" font-size="24">&lt; 1.8s P99</text>
    <text x="16" y="68" class="font-sans" font-size="10.5" fill="#C77B9B">Full audit trail generated per dispute</text>
  </g>

  <!-- Bottom Interactive CTA Link Row -->
  <g transform="translate(24, 240)">
    <text x="0" y="14" class="font-mono" font-size="11" font-weight="600" fill="#FF4D6D">➔ SYSTEM DESIGN: SYSTEM_DESIGNS/dispute-arbitrator.md</text>
    <text x="580" y="14" class="font-mono" font-size="11" font-weight="600" fill="#E5B5C7">SOURCE: apps/dispute-arbitrator [CLI / API]</text>
  </g>

  <!-- Bottom Shimmer Accent -->
  <rect x="24" y="267" width="832" height="1.5" fill="url(#beamGrad)" />
</svg>"""
    with open(out_path, "w") as f:
        f.write(svg)
    print(f"Generated project card: {out_path}")

def generate_project_regulatory():
    out_path = "assets/card-project-regulatory.svg"
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 880 270" width="100%" height="auto" role="img" aria-label="Regulatory Risk Intelligence Engine">
  <defs>
{COMMON_DEFS}
  </defs>
  <style>
{COMMON_STYLE}
  </style>

  <!-- Outer Card -->
  <rect x="1" y="1" width="878" height="268" rx="16" fill="url(#cardBgGrad)" stroke="url(#borderGrad)" stroke-width="1.4" />
  <rect x="1" y="1" width="878" height="268" rx="16" fill="url(#cardGrid)" />
  <rect x="1" y="1" width="878" height="268" rx="16" fill="url(#cornerAura)" />

  <!-- Top Status Bar -->
  <g transform="translate(24, 20)">
    <!-- Category Pill -->
    <rect x="0" y="0" width="168" height="22" rx="5" fill="#451126" stroke="#701A3D" stroke-width="0.8" />
    <text x="84" y="15" class="font-mono" font-size="10" font-weight="700" fill="#E5B5C7" text-anchor="middle" letter-spacing="1">ARCH-02 // ENTERPRISE RAG</text>

    <!-- Live Status Pill -->
    <rect x="178" y="0" width="170" height="22" rx="5" fill="#1C0A15" stroke="#A82C5D" stroke-width="0.8" />
    <circle cx="190" cy="11" r="3.5" fill="#FF4D6D">
      <animate attributeName="opacity" values="1;0.4;1" dur="2s" repeatCount="indefinite" />
    </circle>
    <text x="270" y="15" class="font-mono" font-size="10" font-weight="700" fill="#FF4D6D" text-anchor="middle" letter-spacing="1">🤗 HUGGING FACE LIVE SPACE</text>
  </g>

  <!-- Project Title -->
  <text x="24" y="74" class="font-sans text-title" font-size="22">Regulatory Risk Intelligence Engine</text>
  <text x="24" y="96" class="font-sans text-sub" font-size="13">High-Throughput Contract Clause Analysis, Ambiguity Classification &amp; Hybrid Vector Retrieval</text>

  <!-- Tech Stack Pills Row -->
  <g transform="translate(24, 114)">
    <rect x="0" y="0" width="160" height="22" rx="4" fill="#2E101E" stroke="#701A3D" stroke-width="0.8" />
    <text x="80" y="15" class="font-sans tag-text" font-size="11" text-anchor="middle">Qdrant Hybrid Search</text>

    <rect x="168" y="0" width="118" height="22" rx="4" fill="#2E101E" stroke="#701A3D" stroke-width="0.8" />
    <text x="227" y="15" class="font-sans tag-text" font-size="11" text-anchor="middle">Llama-3.3-70B</text>

    <rect x="294" y="0" width="110" height="22" rx="4" fill="#2E101E" stroke="#701A3D" stroke-width="0.8" />
    <text x="349" y="15" class="font-sans tag-text" font-size="11" text-anchor="middle">BM25 + Dense</text>

    <rect x="412" y="0" width="116" height="22" rx="4" fill="#2E101E" stroke="#701A3D" stroke-width="0.8" />
    <text x="470" y="15" class="font-sans tag-text" font-size="11" text-anchor="middle">Cross-Encoders</text>

    <rect x="536" y="0" width="108" height="22" rx="4" fill="#2E101E" stroke="#701A3D" stroke-width="0.8" />
    <text x="590" y="15" class="font-sans tag-text" font-size="11" text-anchor="middle">Gradio Space</text>

    <rect x="652" y="0" width="94" height="22" rx="4" fill="#2E101E" stroke="#701A3D" stroke-width="0.8" />
    <text x="699" y="15" class="font-sans tag-text" font-size="11" text-anchor="middle">FastAPI</text>
  </g>

  <!-- Metrics Grid (3 Key Metric Panels) -->
  <g transform="translate(24, 150)">
    <rect x="0" y="0" width="260" height="76" rx="8" fill="#170712" stroke="#451126" stroke-width="1" />
    <text x="16" y="24" class="font-sans metric-lbl">RETRIEVAL LATENCY (P99)</text>
    <text x="16" y="52" class="font-sans metric-val" font-size="24">420 ms P99</text>
    <text x="16" y="68" class="font-sans" font-size="10.5" fill="#C77B9B">Sub-second dense + sparse lexical re-ranking</text>
  </g>

  <g transform="translate(298, 150)">
    <rect x="0" y="0" width="260" height="76" rx="8" fill="#170712" stroke="#451126" stroke-width="1" />
    <text x="16" y="24" class="font-sans metric-lbl">CLAUSE EXTRACTION ACCURACY</text>
    <text x="16" y="52" class="font-sans metric-val" font-size="24">99.4% Precision</text>
    <text x="16" y="68" class="font-sans" font-size="10.5" fill="#C77B9B">Zero hallucination on CUAD benchmark test set</text>
  </g>

  <g transform="translate(572, 150)">
    <rect x="0" y="0" width="284" height="76" rx="8" fill="#170712" stroke="#451126" stroke-width="1" />
    <text x="16" y="24" class="font-sans metric-lbl">CORPUS THROUGHPUT</text>
    <text x="16" y="52" class="font-sans metric-val" font-size="24">100K+ Pages</text>
    <text x="16" y="68" class="font-sans" font-size="10.5" fill="#C77B9B">Sub-second risk matrices generated per NDA/MSA</text>
  </g>

  <!-- Bottom Interactive CTA Link Row -->
  <g transform="translate(24, 240)">
    <text x="0" y="14" class="font-mono" font-size="11" font-weight="600" fill="#FF4D6D">➔ LIVE SPACE: huggingface.co/spaces/ashrafksalim/contract-clause-risk-review</text>
    <text x="630" y="14" class="font-mono" font-size="11" font-weight="600" fill="#E5B5C7">SOURCE: apps/rag-engine</text>
  </g>

  <!-- Bottom Shimmer Accent -->
  <rect x="24" y="267" width="832" height="1.5" fill="url(#beamGrad)" />
</svg>"""
    with open(out_path, "w") as f:
        f.write(svg)
    print(f"Generated project card: {out_path}")

def generate_project_copilot():
    out_path = "assets/card-project-copilot.svg"
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 880 270" width="100%" height="auto" role="img" aria-label="Self-Healing Infra SRE Copilot">
  <defs>
{COMMON_DEFS}
  </defs>
  <style>
{COMMON_STYLE}
  </style>

  <!-- Outer Card -->
  <rect x="1" y="1" width="878" height="268" rx="16" fill="url(#cardBgGrad)" stroke="url(#borderGrad)" stroke-width="1.4" />
  <rect x="1" y="1" width="878" height="268" rx="16" fill="url(#cardGrid)" />
  <rect x="1" y="1" width="878" height="268" rx="16" fill="url(#cornerAura)" />

  <!-- Top Status Bar -->
  <g transform="translate(24, 20)">
    <!-- Category Pill -->
    <rect x="0" y="0" width="168" height="22" rx="5" fill="#451126" stroke="#701A3D" stroke-width="0.8" />
    <text x="84" y="15" class="font-mono" font-size="10" font-weight="700" fill="#E5B5C7" text-anchor="middle" letter-spacing="1">ARCH-03 // SRE &amp; OBSERVABILITY</text>

    <!-- Live Status Pill -->
    <rect x="178" y="0" width="150" height="22" rx="5" fill="#1C0A15" stroke="#10B981" stroke-width="0.8" />
    <circle cx="190" cy="11" r="3.5" fill="#10B981">
      <animate attributeName="opacity" values="1;0.4;1" dur="2s" repeatCount="indefinite" />
    </circle>
    <text x="259" y="15" class="font-mono" font-size="10" font-weight="700" fill="#10B981" text-anchor="middle" letter-spacing="1">ENTERPRISE AGENT</text>
  </g>

  <!-- Project Title -->
  <text x="24" y="74" class="font-sans text-title" font-size="22">Self-Healing Infra SRE Copilot</text>
  <text x="24" y="96" class="font-sans text-sub" font-size="13">Autonomous Kubernetes Incident Remediation, eBPF Kernel Telemetry &amp; Root Cause Analysis</text>

  <!-- Tech Stack Pills Row -->
  <g transform="translate(24, 114)">
    <rect x="0" y="0" width="96" height="22" rx="4" fill="#2E101E" stroke="#701A3D" stroke-width="0.8" />
    <text x="48" y="15" class="font-sans tag-text" font-size="11" text-anchor="middle">LangSmith</text>

    <rect x="104" y="0" width="124" height="22" rx="4" fill="#2E101E" stroke="#701A3D" stroke-width="0.8" />
    <text x="166" y="15" class="font-sans tag-text" font-size="11" text-anchor="middle">eBPF Telemetry</text>

    <rect x="236" y="0" width="112" height="22" rx="4" fill="#2E101E" stroke="#701A3D" stroke-width="0.8" />
    <text x="292" y="15" class="font-sans tag-text" font-size="11" text-anchor="middle">Prometheus</text>

    <rect x="356" y="0" width="140" height="22" rx="4" fill="#2E101E" stroke="#701A3D" stroke-width="0.8" />
    <text x="426" y="15" class="font-sans tag-text" font-size="11" text-anchor="middle">Kubernetes Operator</text>

    <rect x="504" y="0" width="90" height="22" rx="4" fill="#2E101E" stroke="#701A3D" stroke-width="0.8" />
    <text x="549" y="15" class="font-sans tag-text" font-size="11" text-anchor="middle">Golang</text>

    <rect x="602" y="0" width="94" height="22" rx="4" fill="#2E101E" stroke="#701A3D" stroke-width="0.8" />
    <text x="649" y="15" class="font-sans tag-text" font-size="11" text-anchor="middle">OpenTelemetry</text>
  </g>

  <!-- Metrics Grid (3 Key Metric Panels) -->
  <g transform="translate(24, 150)">
    <rect x="0" y="0" width="260" height="76" rx="8" fill="#170712" stroke="#451126" stroke-width="1" />
    <text x="16" y="24" class="font-sans metric-lbl">MEAN TIME TO RESOLVE (MTTR)</text>
    <text x="16" y="52" class="font-sans metric-val" font-size="24">68% Reduction</text>
    <text x="16" y="68" class="font-sans" font-size="10.5" fill="#C77B9B">Cut incident duration from 45m to &lt; 14m</text>
  </g>

  <g transform="translate(298, 150)">
    <rect x="0" y="0" width="260" height="76" rx="8" fill="#170712" stroke="#451126" stroke-width="1" />
    <text x="16" y="24" class="font-sans metric-lbl">TELEMETRY TRACE LATENCY</text>
    <text x="16" y="52" class="font-sans metric-val" font-size="24">Zero Drift</text>
    <text x="16" y="68" class="font-sans" font-size="10.5" fill="#C77B9B">Sub-10ms eBPF packet probe capture overhead</text>
  </g>

  <g transform="translate(572, 150)">
    <rect x="0" y="0" width="284" height="76" rx="8" fill="#170712" stroke="#451126" stroke-width="1" />
    <text x="16" y="24" class="font-sans metric-lbl">UPTIME AVAILABILITY GUARD</text>
    <text x="16" y="52" class="font-sans metric-val" font-size="24">99.99% Guard</text>
    <text x="16" y="68" class="font-sans" font-size="10.5" fill="#C77B9B">Proactive pod memory drain &amp; circuit breaking</text>
  </g>

  <!-- Bottom Interactive CTA Link Row -->
  <g transform="translate(24, 240)">
    <text x="0" y="14" class="font-mono" font-size="11" font-weight="600" fill="#FF4D6D">➔ SYSTEM DESIGN: SYSTEM_DESIGNS/sre-copilot.md</text>
    <text x="610" y="14" class="font-mono" font-size="11" font-weight="600" fill="#E5B5C7">SOURCE: apps/sre-copilot</text>
  </g>

  <!-- Bottom Shimmer Accent -->
  <rect x="24" y="267" width="832" height="1.5" fill="url(#beamGrad)" />
</svg>"""
    with open(out_path, "w") as f:
        f.write(svg)
    print(f"Generated project card: {out_path}")

def generate_toolkit_card():
    out_path = "assets/card-toolkit.svg"
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 880 340" width="100%" height="auto" role="img" aria-label="Technical Toolkit Matrix">
  <defs>
{COMMON_DEFS}
  </defs>
  <style>
{COMMON_STYLE}
  </style>

  <!-- Outer Card -->
  <rect x="1" y="1" width="878" height="338" rx="16" fill="url(#cardBgGrad)" stroke="url(#borderGrad)" stroke-width="1.4" />
  <rect x="1" y="1" width="878" height="338" rx="16" fill="url(#cardGrid)" />
  <rect x="1" y="1" width="878" height="338" rx="16" fill="url(#cornerAura)" />

  <!-- 4 Column Domains -->
  <!-- Column 1: Autonomous Agents -->
  <g transform="translate(24, 24)">
    <rect x="0" y="0" width="198" height="288" rx="10" fill="#170712" stroke="#451126" stroke-width="1" />
    <rect x="12" y="12" width="174" height="28" rx="5" fill="#2E101E" stroke="#701A3D" stroke-width="0.8" />
    <text x="99" y="30" class="font-sans" font-size="11" font-weight="700" fill="#F8F0F3" text-anchor="middle" letter-spacing="0.8">⚡ AUTONOMOUS AGENTS</text>

    <!-- Skills list -->
    <text x="20" y="70" class="font-mono" font-size="11" font-weight="600" fill="#E5B5C7">▸ LangGraph (StateGraph)</text>
    <text x="20" y="96" class="font-mono" font-size="11" font-weight="600" fill="#E5B5C7">▸ CrewAI &amp; AutoGen</text>
    <text x="20" y="122" class="font-mono" font-size="11" font-weight="600" fill="#E5B5C7">▸ DeepSeek-R1 Distill</text>
    <text x="20" y="148" class="font-mono" font-size="11" font-weight="600" fill="#E5B5C7">▸ Function Calling / MCP</text>
    <text x="20" y="174" class="font-mono" font-size="11" font-weight="600" fill="#E5B5C7">▸ Human-in-the-Loop</text>
    <text x="20" y="200" class="font-mono" font-size="11" font-weight="600" fill="#E5B5C7">▸ Memory &amp; Checkpoints</text>
    <text x="20" y="226" class="font-mono" font-size="11" font-weight="600" fill="#E5B5C7">▸ Dynamic Replanning</text>

    <rect x="12" y="248" width="174" height="24" rx="4" fill="#260C1A" />
    <text x="99" y="264" class="font-sans metric-lbl" text-anchor="middle">MULTI-AGENT ORCHESTRATION</text>
  </g>

  <!-- Column 2: Enterprise RAG -->
  <g transform="translate(236, 24)">
    <rect x="0" y="0" width="198" height="288" rx="10" fill="#170712" stroke="#451126" stroke-width="1" />
    <rect x="12" y="12" width="174" height="28" rx="5" fill="#2E101E" stroke="#701A3D" stroke-width="0.8" />
    <text x="99" y="30" class="font-sans" font-size="11" font-weight="700" fill="#F8F0F3" text-anchor="middle" letter-spacing="0.8">🎯 ENTERPRISE RAG</text>

    <text x="20" y="70" class="font-mono" font-size="11" font-weight="600" fill="#E5B5C7">▸ Qdrant Hybrid Vector</text>
    <text x="20" y="96" class="font-mono" font-size="11" font-weight="600" fill="#E5B5C7">▸ BM25 Sparse Search</text>
    <text x="20" y="122" class="font-mono" font-size="11" font-weight="600" fill="#E5B5C7">▸ Cross-Encoder Rerank</text>
    <text x="20" y="148" class="font-mono" font-size="11" font-weight="600" fill="#E5B5C7">▸ Semantic Caching</text>
    <text x="20" y="174" class="font-mono" font-size="11" font-weight="600" fill="#E5B5C7">▸ Context Compression</text>
    <text x="20" y="200" class="font-mono" font-size="11" font-weight="600" fill="#E5B5C7">▸ Document Chunking</text>
    <text x="20" y="226" class="font-mono" font-size="11" font-weight="600" fill="#E5B5C7">▸ RAG Triad Evaluation</text>

    <rect x="12" y="248" width="174" height="24" rx="4" fill="#260C1A" />
    <text x="99" y="264" class="font-sans metric-lbl" text-anchor="middle">SUB-SECOND HIGH PRECISION</text>
  </g>

  <!-- Column 3: Infra & Observability -->
  <g transform="translate(448, 24)">
    <rect x="0" y="0" width="198" height="288" rx="10" fill="#170712" stroke="#451126" stroke-width="1" />
    <rect x="12" y="12" width="174" height="28" rx="5" fill="#2E101E" stroke="#701A3D" stroke-width="0.8" />
    <text x="99" y="30" class="font-sans" font-size="11" font-weight="700" fill="#F8F0F3" text-anchor="middle" letter-spacing="0.8">☁️ INFRA &amp; OPS</text>

    <text x="20" y="70" class="font-mono" font-size="11" font-weight="600" fill="#E5B5C7">▸ Kubernetes &amp; Docker</text>
    <text x="20" y="96" class="font-mono" font-size="11" font-weight="600" fill="#E5B5C7">▸ LangSmith Tracing</text>
    <text x="20" y="122" class="font-mono" font-size="11" font-weight="600" fill="#E5B5C7">▸ Prometheus &amp; Grafana</text>
    <text x="20" y="148" class="font-mono" font-size="11" font-weight="600" fill="#E5B5C7">▸ eBPF Observability</text>
    <text x="20" y="174" class="font-mono" font-size="11" font-weight="600" fill="#E5B5C7">▸ Terraform / AWS / GCP</text>
    <text x="20" y="200" class="font-mono" font-size="11" font-weight="600" fill="#E5B5C7">▸ GitHub Actions CI/CD</text>
    <text x="20" y="226" class="font-mono" font-size="11" font-weight="600" fill="#E5B5C7">▸ Zero-Trust Envoy</text>

    <rect x="12" y="248" width="174" height="24" rx="4" fill="#260C1A" />
    <text x="99" y="264" class="font-sans metric-lbl" text-anchor="middle">DISTRIBUTED &amp; RESILIENT</text>
  </g>

  <!-- Column 4: Quantum & Data Core -->
  <g transform="translate(660, 24)">
    <rect x="0" y="0" width="196" height="288" rx="10" fill="#170712" stroke="#451126" stroke-width="1" />
    <rect x="12" y="12" width="172" height="28" rx="5" fill="#2E101E" stroke="#701A3D" stroke-width="0.8" />
    <text x="98" y="30" class="font-sans" font-size="11" font-weight="700" fill="#F8F0F3" text-anchor="middle" letter-spacing="0.8">⚛️ QUANTUM &amp; DATA</text>

    <text x="20" y="70" class="font-mono" font-size="11" font-weight="600" fill="#E5B5C7">▸ IBM Qiskit Quantum</text>
    <text x="20" y="96" class="font-mono" font-size="11" font-weight="600" fill="#E5B5C7">▸ VQE &amp; QAOA Algorithms</text>
    <text x="20" y="122" class="font-mono" font-size="11" font-weight="600" fill="#E5B5C7">▸ Apache Kafka Streams</text>
    <text x="20" y="148" class="font-mono" font-size="11" font-weight="600" fill="#E5B5C7">▸ PostgreSQL &amp; pgvector</text>
    <text x="20" y="174" class="font-mono" font-size="11" font-weight="600" fill="#E5B5C7">▸ Redis Streams &amp; Cache</text>
    <text x="20" y="200" class="font-mono" font-size="11" font-weight="600" fill="#E5B5C7">▸ DuckDB Analytical Engine</text>
    <text x="20" y="226" class="font-mono" font-size="11" font-weight="600" fill="#E5B5C7">▸ Python · Go · C++</text>

    <rect x="12" y="248" width="172" height="24" rx="4" fill="#260C1A" />
    <text x="98" y="264" class="font-sans metric-lbl" text-anchor="middle">HIGH-THROUGHPUT COMPUTE</text>
  </g>

  <!-- Bottom Shimmer Accent -->
  <rect x="24" y="337" width="832" height="1.5" fill="url(#beamGrad)" />
</svg>"""
    with open(out_path, "w") as f:
        f.write(svg)
    print(f"Generated toolkit card: {out_path}")

def generate_benchmarks_card():
    out_path = "assets/card-benchmarks.svg"
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 880 290" width="100%" height="auto" role="img" aria-label="Enterprise Benchmarks Dashboard">
  <defs>
{COMMON_DEFS}
  </defs>
  <style>
{COMMON_STYLE}
  </style>

  <!-- Outer Card -->
  <rect x="1" y="1" width="878" height="288" rx="16" fill="url(#cardBgGrad)" stroke="url(#borderGrad)" stroke-width="1.4" />
  <rect x="1" y="1" width="878" height="288" rx="16" fill="url(#cardGrid)" />
  <rect x="1" y="1" width="878" height="288" rx="16" fill="url(#cornerAura)" />

  <!-- Top Banner Info -->
  <g transform="translate(24, 20)">
    <text x="0" y="18" class="font-sans text-title" font-size="18">Simulated Enterprise Benchmark Telemetry</text>
    <text x="0" y="36" class="font-sans text-sub" font-size="11.5">Rigorous validation results across synthetic financial transaction &amp; contract datasets</text>
  </g>

  <!-- 4 Metrics Gauges / Progress Cards -->
  <!-- Box 1 -->
  <g transform="translate(24, 76)">
    <rect x="0" y="0" width="198" height="130" rx="8" fill="#170712" stroke="#451126" stroke-width="1" />
    <text x="16" y="24" class="font-sans metric-lbl">ARBITRATION RESOLUTION</text>
    <text x="16" y="58" class="font-sans metric-val" font-size="28">94.2%</text>
    <text x="16" y="76" class="font-sans" font-size="11" fill="#C77B9B">Benchmark: 80%</text>
    <!-- Progress bar -->
    <rect x="16" y="94" width="166" height="8" rx="4" fill="#2E101E" />
    <rect x="16" y="94" width="156" height="8" rx="4" fill="#10B981" />
    <text x="16" y="118" class="font-mono" font-size="10" fill="#10B981">✓ +14.2% Over Target</text>
  </g>

  <!-- Box 2 -->
  <g transform="translate(236, 76)">
    <rect x="0" y="0" width="198" height="130" rx="8" fill="#170712" stroke="#451126" stroke-width="1" />
    <text x="16" y="24" class="font-sans metric-lbl">HYBRID RETRIEVAL P99</text>
    <text x="16" y="58" class="font-sans metric-val" font-size="28">420 ms</text>
    <text x="16" y="76" class="font-sans" font-size="11" fill="#C77B9B">SLA Target: &lt; 1,000ms</text>
    <rect x="16" y="94" width="166" height="8" rx="4" fill="#2E101E" />
    <rect x="16" y="94" width="140" height="8" rx="4" fill="#FF4D6D" />
    <text x="16" y="118" class="font-mono" font-size="10" fill="#FF4D6D">⚡ 2.38x Latency Advantage</text>
  </g>

  <!-- Box 3 -->
  <g transform="translate(448, 76)">
    <rect x="0" y="0" width="198" height="130" rx="8" fill="#170712" stroke="#451126" stroke-width="1" />
    <text x="16" y="24" class="font-sans metric-lbl">INCIDENT MTTR REDUCTION</text>
    <text x="16" y="58" class="font-sans metric-val" font-size="28">68.0%</text>
    <text x="16" y="76" class="font-sans" font-size="11" fill="#C77B9B">From 45m to &lt; 14m</text>
    <rect x="16" y="94" width="166" height="8" rx="4" fill="#2E101E" />
    <rect x="16" y="94" width="112" height="8" rx="4" fill="#10B981" />
    <text x="16" y="118" class="font-mono" font-size="10" fill="#10B981">🛡️ Automated Self-Heal</text>
  </g>

  <!-- Box 4 -->
  <g transform="translate(660, 76)">
    <rect x="0" y="0" width="196" height="130" rx="8" fill="#170712" stroke="#451126" stroke-width="1" />
    <text x="16" y="24" class="font-sans metric-lbl">TOKEN INFERENCE COST</text>
    <text x="16" y="58" class="font-sans metric-val" font-size="28">$0.14</text>
    <text x="16" y="76" class="font-sans" font-size="11" fill="#C77B9B">Per 1M Output Tokens</text>
    <rect x="16" y="94" width="164" height="8" rx="4" fill="#2E101E" />
    <rect x="16" y="94" width="145" height="8" rx="4" fill="#A82C5D" />
    <text x="16" y="118" class="font-mono" font-size="10" fill="#E5B5C7">📉 -89% vs Proprietary</text>
  </g>

  <!-- Bottom Verification Callout Box -->
  <g transform="translate(24, 222)">
    <rect x="0" y="0" width="832" height="44" rx="8" fill="#1B0A15" stroke="#701A3D" stroke-width="0.8" />
    <circle cx="20" cy="22" r="4" fill="#FF4D6D" />
    <text x="36" y="26" class="font-sans" font-size="11" fill="#E5B5C7">
      <tspan font-weight="700" fill="#FFFFFF">SIMULATION &amp; BENCHMARK METHODOLOGY:</tspan> All reported metrics are verified runs on reproducible synthetic enterprise corpora (CUAD, synthetically generated financial dispute ledgers &amp; K8s chaos tests). Detailed scripts located in /benchmarks.
    </text>
  </g>

  <!-- Bottom Shimmer Accent -->
  <rect x="24" y="287" width="832" height="1.5" fill="url(#beamGrad)" />
</svg>"""
    with open(out_path, "w") as f:
        f.write(svg)
    print(f"Generated benchmarks card: {out_path}")

def generate_credentials_card():
    out_path = "assets/card-credentials.svg"
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 880 220" width="100%" height="auto" role="img" aria-label="Credentials &amp; Certifications">
  <defs>
{COMMON_DEFS}
  </defs>
  <style>
{COMMON_STYLE}
  </style>

  <!-- Outer Card -->
  <rect x="1" y="1" width="878" height="218" rx="16" fill="url(#cardBgGrad)" stroke="url(#borderGrad)" stroke-width="1.4" />
  <rect x="1" y="1" width="878" height="218" rx="16" fill="url(#cardGrid)" />
  <rect x="1" y="1" width="878" height="218" rx="16" fill="url(#cornerAura)" />

  <!-- 3 Credential Badges / Cards -->
  <!-- Cred 1: IBM Quantum -->
  <g transform="translate(24, 24)">
    <rect x="0" y="0" width="260" height="168" rx="10" fill="#170712" stroke="#451126" stroke-width="1" />
    <rect x="16" y="16" width="94" height="20" rx="4" fill="#2E101E" stroke="#701A3D" stroke-width="0.8" />
    <text x="63" y="30" class="font-mono" font-size="9.5" font-weight="700" fill="#E5B5C7" text-anchor="middle">IBM QUANTUM</text>
    <text x="16" y="66" class="font-sans text-title" font-size="15">Quantum Computation</text>
    <text x="16" y="86" class="font-sans text-sub" font-size="12">IBM Quantum Spring Challenge &amp; Credly Badges</text>
    <text x="16" y="112" class="font-sans" font-size="11" fill="#E5B5C7">VQE, Circuit Optimization, Error Mitigation</text>
    <text x="16" y="148" class="font-mono" font-size="10.5" font-weight="600" fill="#FF4D6D">➔ credly.com/users/ashraf-khan</text>
  </g>

  <!-- Cred 2: LangGraph Certified -->
  <g transform="translate(310, 24)">
    <rect x="0" y="0" width="260" height="168" rx="10" fill="#170712" stroke="#451126" stroke-width="1" />
    <rect x="16" y="16" width="118" height="20" rx="4" fill="#2E101E" stroke="#701A3D" stroke-width="0.8" />
    <text x="75" y="30" class="font-mono" font-size="9.5" font-weight="700" fill="#E5B5C7" text-anchor="middle">LANGCHAIN ACADEMY</text>
    <text x="16" y="66" class="font-sans text-title" font-size="15">LangGraph Certified</text>
    <text x="16" y="86" class="font-sans text-sub" font-size="12">StateGraph &amp; Multi-Agent Orchestration</text>
    <text x="16" y="112" class="font-sans" font-size="11" fill="#E5B5C7">ID: 1hhanf8ox7 · Verified Accreditation</text>
    <text x="16" y="148" class="font-mono" font-size="10.5" font-weight="600" fill="#FF4D6D">➔ academy.langchain.com</text>
  </g>

  <!-- Cred 3: LangSmith Certified -->
  <g transform="translate(596, 24)">
    <rect x="0" y="0" width="260" height="168" rx="10" fill="#170712" stroke="#451126" stroke-width="1" />
    <rect x="16" y="16" width="118" height="20" rx="4" fill="#2E101E" stroke="#701A3D" stroke-width="0.8" />
    <text x="75" y="30" class="font-mono" font-size="9.5" font-weight="700" fill="#E5B5C7" text-anchor="middle">LANGCHAIN ACADEMY</text>
    <text x="16" y="66" class="font-sans text-title" font-size="15">LangSmith Observability</text>
    <text x="16" y="86" class="font-sans text-sub" font-size="12">Production Tracing &amp; Agent Evaluation</text>
    <text x="16" y="112" class="font-sans" font-size="11" fill="#E5B5C7">ID: rlwlwmnqzc · Verified Accreditation</text>
    <text x="16" y="148" class="font-mono" font-size="10.5" font-weight="600" fill="#FF4D6D">➔ academy.langchain.com</text>
  </g>

  <!-- Bottom Shimmer Accent -->
  <rect x="24" y="217" width="832" height="1.5" fill="url(#beamGrad)" />
</svg>"""
    with open(out_path, "w") as f:
        f.write(svg)
    print(f"Generated credentials card: {out_path}")

def generate_research_card():
    out_path = "assets/card-research.svg"
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 880 230" width="100%" height="auto" role="img" aria-label="Research Whitepapers &amp; Architectural Blueprints">
  <defs>
{COMMON_DEFS}
  </defs>
  <style>
{COMMON_STYLE}
  </style>

  <!-- Outer Card -->
  <rect x="1" y="1" width="878" height="228" rx="16" fill="url(#cardBgGrad)" stroke="url(#borderGrad)" stroke-width="1.4" />
  <rect x="1" y="1" width="878" height="228" rx="16" fill="url(#cardGrid)" />
  <rect x="1" y="1" width="878" height="228" rx="16" fill="url(#cornerAura)" />

  <!-- Paper 1 -->
  <g transform="translate(24, 24)">
    <rect x="0" y="0" width="400" height="178" rx="10" fill="#170712" stroke="#451126" stroke-width="1" />
    <rect x="16" y="16" width="124" height="20" rx="4" fill="#2E101E" stroke="#701A3D" stroke-width="0.8" />
    <text x="78" y="30" class="font-mono" font-size="9.5" font-weight="700" fill="#E5B5C7" text-anchor="middle">WHITEPAPER 01</text>
    <text x="16" y="66" class="font-sans text-title" font-size="14.5">Multi-Agent StateGraph Fault Tolerance</text>
    <text x="16" y="86" class="font-sans text-sub" font-size="11.5">Formal Verification of Cyclic Agent Swarms &amp; Deadlock Prevention</text>
    <text x="16" y="112" class="font-sans" font-size="11" fill="#E5B5C7">Analysis of bounded state recursion, human intervention failover &amp; checkpoint consistency.</text>
    <text x="16" y="156" class="font-mono" font-size="10.5" font-weight="600" fill="#FF4D6D">➔ READ DOCS: docs/whitepapers/fault-tolerance.md</text>
  </g>

  <!-- Paper 2 -->
  <g transform="translate(456, 24)">
    <rect x="0" y="0" width="400" height="178" rx="10" fill="#170712" stroke="#451126" stroke-width="1" />
    <rect x="16" y="16" width="124" height="20" rx="4" fill="#2E101E" stroke="#701A3D" stroke-width="0.8" />
    <text x="78" y="30" class="font-mono" font-size="9.5" font-weight="700" fill="#E5B5C7" text-anchor="middle">WHITEPAPER 02</text>
    <text x="16" y="66" class="font-sans text-title" font-size="14.5">Hybrid Sparse-Dense Vector Precision</text>
    <text x="16" y="86" class="font-sans text-sub" font-size="11.5">CUAD Benchmark Optimization via Cross-Encoder Re-Ranking</text>
    <text x="16" y="112" class="font-sans" font-size="11" fill="#E5B5C7">Empirical comparison of lexical BM25 vs dense embeddings across complex legal clauses.</text>
    <text x="16" y="156" class="font-mono" font-size="10.5" font-weight="600" fill="#FF4D6D">➔ READ DOCS: docs/whitepapers/hybrid-rag.md</text>
  </g>

  <!-- Bottom Shimmer Accent -->
  <rect x="24" y="227" width="832" height="1.5" fill="url(#beamGrad)" />
</svg>"""
    with open(out_path, "w") as f:
        f.write(svg)
    print(f"Generated research card: {out_path}")

def generate_commercial_card():
    out_path = "assets/card-commercial.svg"
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 880 230" width="100%" height="auto" role="img" aria-label="Commercial Case Studies">
  <defs>
{COMMON_DEFS}
  </defs>
  <style>
{COMMON_STYLE}
  </style>

  <!-- Outer Card -->
  <rect x="1" y="1" width="878" height="228" rx="16" fill="url(#cardBgGrad)" stroke="url(#borderGrad)" stroke-width="1.4" />
  <rect x="1" y="1" width="878" height="228" rx="16" fill="url(#cardGrid)" />
  <rect x="1" y="1" width="878" height="228" rx="16" fill="url(#cornerAura)" />

  <!-- 3 Case Study Panels -->
  <!-- Case 1 -->
  <g transform="translate(24, 24)">
    <rect x="0" y="0" width="260" height="178" rx="10" fill="#170712" stroke="#451126" stroke-width="1" />
    <rect x="16" y="16" width="104" height="20" rx="4" fill="#2E101E" stroke="#701A3D" stroke-width="0.8" />
    <text x="68" y="30" class="font-mono" font-size="9.5" font-weight="700" fill="#E5B5C7" text-anchor="middle">FINTECH CASE</text>
    <text x="16" y="66" class="font-sans text-title" font-size="14.5">Autonomous Dispute Mesh</text>
    <text x="16" y="86" class="font-sans text-sub" font-size="11.5">Tier-1 Payment Gateway Audit</text>
    <text x="16" y="112" class="font-sans" font-size="11" fill="#E5B5C7">Replaced manual compliance triaging with LangGraph cyclic graph.</text>
    <text x="16" y="156" class="font-mono" font-size="10.5" font-weight="600" fill="#FF4D6D">➔ CASE_STUDIES/01_FINTECH.md</text>
  </g>

  <!-- Case 2 -->
  <g transform="translate(310, 24)">
    <rect x="0" y="0" width="260" height="178" rx="10" fill="#170712" stroke="#451126" stroke-width="1" />
    <rect x="16" y="16" width="118" height="20" rx="4" fill="#2E101E" stroke="#701A3D" stroke-width="0.8" />
    <text x="75" y="30" class="font-mono" font-size="9.5" font-weight="700" fill="#E5B5C7" text-anchor="middle">LEGAL / COMPLIANCE</text>
    <text x="16" y="66" class="font-sans text-title" font-size="14.5">Contract Intelligence Grid</text>
    <text x="16" y="86" class="font-sans text-sub" font-size="11.5">Healthcare Provider NDA Engine</text>
    <text x="16" y="112" class="font-sans" font-size="11" fill="#E5B5C7">Sub-second extraction of indemnification liability and risk clauses.</text>
    <text x="16" y="156" class="font-mono" font-size="10.5" font-weight="600" fill="#FF4D6D">➔ CASE_STUDIES/02_HEALTHCARE.md</text>
  </g>

  <!-- Case 3 -->
  <g transform="translate(596, 24)">
    <rect x="0" y="0" width="260" height="178" rx="10" fill="#170712" stroke="#451126" stroke-width="1" />
    <rect x="16" y="16" width="118" height="20" rx="4" fill="#2E101E" stroke="#701A3D" stroke-width="0.8" />
    <text x="75" y="30" class="font-mono" font-size="9.5" font-weight="700" fill="#E5B5C7" text-anchor="middle">CLOUD SRE &amp; CHAOS</text>
    <text x="16" y="66" class="font-sans text-title" font-size="14.5">Zero-Drift K8s Copilot</text>
    <text x="16" y="86" class="font-sans text-sub" font-size="11.5">Chaos Engineering Validation</text>
    <text x="16" y="112" class="font-sans" font-size="11" fill="#E5B5C7">Real-time eBPF socket tracing with automated operator failovers.</text>
    <text x="16" y="156" class="font-mono" font-size="10.5" font-weight="600" fill="#FF4D6D">➔ CASE_STUDIES/03_INFRA.md</text>
  </g>

  <!-- Bottom Shimmer Accent -->
  <rect x="24" y="227" width="832" height="1.5" fill="url(#beamGrad)" />
</svg>"""
    with open(out_path, "w") as f:
        f.write(svg)
    print(f"Generated commercial card: {out_path}")

def main():
    os.makedirs("assets", exist_ok=True)

    # 1. Generate 7 Taller, Bolder Section Headers (viewBox 0 0 880 72)
    headers = [
        ("01", "FLAGSHIP PRODUCTION SYSTEMS", "Self-Built Autonomous Architectures & Production Engines", "PRODUCTION", "assets/hdr-architectures.svg"),
        ("02", "TECHNICAL TOOLKIT & COMPETENCIES", "Production Stacks, Autonomous Frameworks & Distributed Compute", "VERIFIED", "assets/hdr-toolkit.svg"),
        ("03", "ENTERPRISE BENCHMARKS & TELEMETRY", "Simulated Performance Metrics & Throughput Verification", "BENCHMARKS", "assets/hdr-benchmarks.svg"),
        ("04", "CASE STUDIES & COMMERCIAL BLUEPRINTS", "Enterprise Architecture Case Studies & Mission Impact", "BLUEPRINTS", "assets/hdr-commercial.svg"),
        ("05", "CREDENTIALS & ACCREDITATIONS", "IBM Quantum Credentials & LangChain Academy Certifications", "ACCREDITED", "assets/hdr-credentials.svg"),
        ("06", "RESEARCH & ARCHITECTURAL WHITEPAPERS", "Systems Design Publications, Formal Proofs & Analysis", "WHITEPAPERS", "assets/hdr-research.svg"),
        ("07", "GITHUB TELEMETRY & SYSTEM ACTIVITY", "Live Repository Statistics, Codebase Uptime & Commit Stream", "ACTIVE", "assets/hdr-analytics.svg"),
    ]

    for idx, title, sub, tag, path in headers:
        generate_header(idx, title, sub, tag, path)

    # 2. Generate All-In-One Graphical Project Cards
    generate_project_arbitrator()
    generate_project_regulatory()
    generate_project_copilot()

    # 3. Generate Overview Cards
    generate_toolkit_card()
    generate_benchmarks_card()
    generate_commercial_card()
    generate_credentials_card()
    generate_research_card()

    print("All SVG assets successfully generated!")

if __name__ == "__main__":
    main()

