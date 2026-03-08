import { useState, useEffect, useRef, useCallback } from "react";
import { analyzeProperty, transformApiResponse } from "./api";

const CSS = `
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Mono:wght@400;500&family=Inter:wght@300;400;500;600&display=swap');

:root {
  --g:#792E29;--g2:#5c2320;--o:#565538;--o2:#6b6a45;
  --gr:#ABA38F;--t:#D9D4C8;--r:#24201D;--r2:#1a1714;
  --gold:#C9A84C;--green:#6A9B5E;--red:#C4614A;
  --bd:rgba(171,163,143,0.09);--bd2:rgba(171,163,143,0.05);
}
*,*::before,*::after{margin:0;padding:0;box-sizing:border-box}
html{scroll-behavior:smooth}
body{background:var(--r2);color:var(--t);font-family:'Inter',sans-serif;overflow-x:hidden;-webkit-font-smoothing:antialiased}
.ll-root{min-height:100vh;background:var(--r2);color:var(--t);font-family:'Inter',sans-serif;overflow-x:hidden;position:relative}
.scene{position:fixed;inset:0;z-index:0;pointer-events:none;overflow:hidden}
.orb{position:absolute;border-radius:50%;filter:blur(120px);animation:breathe ease-in-out infinite}
.o1{width:900px;height:900px;background:rgba(121,46,41,0.13);top:-350px;right:-250px;animation-duration:26s}
.o2{width:700px;height:700px;background:rgba(86,85,56,0.1);bottom:-200px;left:-200px;animation-duration:22s;animation-delay:-11s}
.o3{width:500px;height:500px;background:rgba(171,163,143,0.05);top:40%;left:35%;animation-duration:32s;animation-delay:-20s}
@keyframes breathe{0%,100%{transform:translate(0,0) scale(1)}33%{transform:translate(40px,-50px) scale(1.08)}66%{transform:translate(-28px,35px) scale(0.92)}}
.gridlines{position:fixed;inset:0;z-index:0;pointer-events:none;background-image:linear-gradient(rgba(171,163,143,.022) 1px,transparent 1px),linear-gradient(90deg,rgba(171,163,143,.022) 1px,transparent 1px);background-size:80px 80px}
.pt{position:absolute;border-radius:50%;background:var(--gr);opacity:0;animation:rise linear infinite}
@keyframes rise{0%{opacity:0;transform:translateY(100vh)}8%{opacity:.15}92%{opacity:.15}100%{opacity:0;transform:translateY(-80px)}}
nav{position:fixed;top:0;left:0;right:0;z-index:200;height:60px;padding:0 3rem;display:flex;align-items:center;justify-content:space-between;backdrop-filter:blur(30px) saturate(1.5);border-bottom:1px solid var(--bd2);transition:background .3s}
.nav-logo{font-family:'DM Serif Display',serif;font-size:1.2rem;letter-spacing:.02em}
.nav-logo b{color:var(--g);font-weight:400}
.nav-links{display:flex;align-items:center;gap:2.5rem}
.nav-btn{font-family:'DM Mono',monospace;font-size:.78rem;font-weight:700;letter-spacing:.2em;text-transform:uppercase;color:rgba(171,163,143,.55);text-decoration:none;transition:.2s;cursor:pointer;background:none;border:none}
.nav-btn:hover{color:var(--t)}
.nav-cta{color:var(--t)!important;border:1px solid rgba(121,46,41,.45)!important;padding:.38rem .95rem!important;border-radius:4px!important;transition:.25s!important}
.nav-cta:hover{background:var(--g)!important;border-color:var(--g)!important}
section{position:relative;z-index:1}
#home{min-height:100vh;display:flex;flex-direction:column;justify-content:center;align-items:center;text-align:center;padding:8rem 2rem 5rem;overflow:hidden}
.hero-kicker{display:inline-flex;align-items:center;gap:.7rem;font-family:'DM Mono',monospace;font-size:.55rem;letter-spacing:.3em;text-transform:uppercase;color:rgba(171,163,143,.4);margin-bottom:2rem;animation:fadeUp .8s cubic-bezier(.16,1,.3,1) both}
.hero-kicker::before,.hero-kicker::after{content:'';display:block;width:36px;height:1px;background:rgba(171,163,143,.12)}
.hero-h1{font-family:'DM Serif Display',serif;font-size:clamp(3.5rem,8vw,7rem);font-weight:400;line-height:1.0;letter-spacing:-.03em;margin-bottom:1.8rem;animation:fadeUp .8s cubic-bezier(.16,1,.3,1) .1s both}
.hero-h1 em{color:var(--g);font-style:italic;display:block}
.hero-h1 .sw{font-size:.5em;font-style:italic;color:rgba(217,212,200,.28);letter-spacing:.02em;display:block;margin-top:.2em}
.hero-desc{font-size:.93rem;color:rgba(217,212,200,.82);line-height:1.85;max-width:460px;margin:0 auto 3rem;font-weight:300;animation:fadeUp .8s cubic-bezier(.16,1,.3,1) .2s both}
.hero-actions{display:flex;align-items:center;gap:1.2rem;animation:fadeUp .8s cubic-bezier(.16,1,.3,1) .3s both;margin-bottom:4.5rem}
.btn-p{font-family:'DM Mono',monospace;font-size:.68rem;letter-spacing:.2em;text-transform:uppercase;color:var(--t);background:var(--g);border:1px solid var(--g);padding:.75rem 2rem;border-radius:4px;cursor:pointer;transition:.25s;box-shadow:0 0 40px rgba(121,46,41,.2)}
.btn-p:hover{background:var(--g2);box-shadow:0 0 60px rgba(121,46,41,.38);transform:translateY(-2px)}
.btn-g{font-family:'DM Mono',monospace;font-size:.68rem;letter-spacing:.2em;text-transform:uppercase;color:rgba(171,163,143,.55);background:transparent;border:1px solid var(--bd);padding:.75rem 2rem;border-radius:4px;cursor:pointer;transition:.25s}
.btn-g:hover{color:var(--t);border-color:rgba(171,163,143,.22)}
.stats-row{display:flex;align-items:stretch;border:1px solid var(--bd);border-radius:12px;overflow:hidden;background:rgba(26,23,20,.5);backdrop-filter:blur(20px);animation:fadeUp .8s cubic-bezier(.16,1,.3,1) .4s both;width:100%;max-width:700px}
.stat{padding:1.6rem 2rem;flex:1;text-align:center;border-right:1px solid var(--bd)}
.stat:last-child{border-right:none}
.stat-num{font-family:'DM Serif Display',serif;font-size:2.1rem;color:#fff;letter-spacing:-.02em;line-height:1;margin-bottom:.4rem}
.stat-num .u{font-size:.42em;color:rgba(217,212,200,.6);font-family:'DM Mono',monospace;margin-left:.15em;letter-spacing:.1em}
.stat-lbl{font-family:'DM Mono',monospace;font-size:.48rem;letter-spacing:.2em;text-transform:uppercase;color:rgba(217,212,200,.55)}
.scroll-cue{position:absolute;bottom:2.5rem;left:50%;transform:translateX(-50%);display:flex;flex-direction:column;align-items:center;gap:.6rem;animation:fadeUp 1s ease 1.2s both}
.scl{width:1px;height:48px;background:linear-gradient(to bottom,rgba(171,163,143,.28),transparent);animation:spulse 2s ease infinite}
@keyframes spulse{0%,100%{opacity:.4}50%{opacity:1}}
.sct{font-family:'DM Mono',monospace;font-size:.46rem;letter-spacing:.25em;color:rgba(171,163,143,.22);text-transform:uppercase}
.divider{position:relative;z-index:1;width:100%;height:1px;background:linear-gradient(90deg,transparent,var(--bd),transparent)}
#about{padding:9rem 3rem;max-width:1100px;margin:0 auto}
.about-grid{display:grid;grid-template-columns:1fr 1fr;gap:7rem;align-items:center}
.sec-tag{font-family:'DM Mono',monospace;font-size:.68rem;letter-spacing:.28em;text-transform:uppercase;color:var(--g);margin-bottom:1.4rem;opacity:.9}
.sec-h{font-family:'DM Serif Display',serif;font-size:clamp(1.8rem,3.5vw,2.8rem);font-weight:400;line-height:1.1;letter-spacing:-.02em;margin-bottom:1.4rem}
.sec-h em{color:var(--g);font-style:italic}
.sec-p{font-size:.86rem;color:rgba(217,212,200,.72);line-height:1.9;font-weight:300;margin-bottom:.9rem}
.acards{display:flex;flex-direction:column;gap:.8rem}
.acard{padding:1.3rem 1.5rem;background:rgba(26,23,20,.65);border:1px solid var(--bd2);border-radius:10px;display:grid;grid-template-columns:30px 1fr;gap:0 .9rem;align-items:start;transition:.25s;cursor:default}
.acard:hover{border-color:var(--bd);background:rgba(34,30,27,.75)}
.acard-n{font-family:'DM Mono',monospace;font-size:.58rem;color:rgba(121,46,41,.6);margin-top:3px;letter-spacing:.05em}
.acard-t{font-size:.8rem;font-weight:600;color:var(--t);margin-bottom:.28rem}
.acard-d{font-size:.74rem;color:rgba(171,163,143,.38);line-height:1.6}
/* PROTOTYPE SEED */
.proto-seed{margin-bottom:1.4rem}
.proto-warning{
  display:flex;align-items:flex-start;gap:.65rem;
  font-family:'DM Mono',monospace;font-size:.72rem;letter-spacing:.08em;
  color:rgba(201,168,76,.7);line-height:1.75;margin-bottom:.85rem;
}
.proto-warning-icon{
  flex-shrink:0;width:20px;height:20px;border-radius:50%;
  border:1px solid rgba(201,168,76,.55);
  display:flex;align-items:center;justify-content:center;
  font-size:.7rem;color:rgba(201,168,76,.85);margin-top:2px;
}
.proto-warning em{color:#e8d08a;font-style:normal;font-weight:600}
.proto-inline{display:flex;align-items:center;gap:.85rem;flex-wrap:wrap}
.proto-inline-lbl{
  font-family:'DM Mono',monospace;font-size:.62rem;letter-spacing:.2em;
  text-transform:uppercase;color:rgba(217,212,200,.75);white-space:nowrap;font-weight:500;
}
.proto-num-inp{
  width:100px;background:rgba(22,19,16,.85);
  border:1px solid rgba(171,163,143,.2);border-radius:6px;
  padding:.55rem .85rem;color:#fff;
  font-family:'Inter',sans-serif;font-size:1rem;font-weight:500;
  outline:none;transition:.2s;
}
.proto-num-inp:focus{border-color:rgba(171,163,143,.4);background:rgba(30,26,23,.95)}
.proto-num-inp::placeholder{color:rgba(171,163,143,.3)}
.proto-num-inp::-webkit-inner-spin-button{opacity:.3}
.proto-fill-btn{
  font-family:'DM Mono',monospace;font-size:.6rem;letter-spacing:.18em;text-transform:uppercase;
  color:rgba(217,212,200,.8);background:transparent;
  border:1px solid rgba(171,163,143,.25);border-radius:5px;
  padding:.54rem 1.1rem;cursor:pointer;transition:.22s;white-space:nowrap;
}
.proto-fill-btn:hover{color:#fff;border-color:rgba(217,212,200,.5);background:rgba(171,163,143,.06)}
.proto-hint-inline{
  font-family:'DM Mono',monospace;font-size:.58rem;letter-spacing:.08em;
  transition:color .25s;font-weight:500;
}

/* GET STARTED */
#get-started{padding:4rem 3rem 9rem;max-width:1000px;margin:0 auto}
.gs-hdr{text-align:center;margin-bottom:3rem}
.gs-h{font-family:'DM Serif Display',serif;font-size:clamp(1.8rem,3.5vw,2.6rem);font-weight:400;letter-spacing:-.02em;margin-bottom:.7rem}
.gs-s{font-size:.84rem;color:rgba(171,163,143,.45);font-weight:300;line-height:1.7}
.presets{display:flex;align-items:center;gap:.6rem;margin-bottom:1.1rem;flex-wrap:wrap}
.preset-lbl{font-family:'DM Mono',monospace;font-size:.56rem;letter-spacing:.2em;text-transform:uppercase;color:rgba(217,212,200,.55);margin-right:.2rem}
.preset-btn{font-family:'DM Mono',monospace;font-size:.58rem;letter-spacing:.1em;color:rgba(217,212,200,.7);background:rgba(26,23,20,.7);border:1px solid rgba(171,163,143,.18);padding:.38rem .95rem;border-radius:3px;cursor:pointer;transition:.22s;white-space:nowrap}
.preset-btn:hover{color:#fff;border-color:rgba(121,46,41,.45);background:rgba(121,46,41,.1)}
.search-block{border:1px solid var(--bd);border-radius:16px;overflow:hidden;background:rgba(20,17,15,.55);backdrop-filter:blur(30px);box-shadow:0 50px 100px rgba(0,0,0,.35),inset 0 1px 0 rgba(217,212,200,.025);position:relative}
.search-block::before{content:'';position:absolute;top:0;left:0;right:0;height:1px;background:linear-gradient(90deg,transparent,rgba(121,46,41,.38) 40%,rgba(86,85,56,.25) 70%,transparent);z-index:1}
.fields-grid{display:grid;grid-template-columns:1fr 1fr 1fr;gap:1px;background:var(--bd2)}
.fcell{padding:1.6rem 1.8rem;background:rgba(22,19,16,.72);transition:.25s;position:relative}
.fcell:hover{background:rgba(30,26,23,.85)}
.fcell.focused{background:rgba(34,30,27,.92)}
.fcell.focused::after{content:'';position:absolute;top:0;left:0;right:0;height:1px;background:rgba(121,46,41,.55)}
.fcell.error{background:rgba(196,97,74,0.06)}
.flbl{font-family:'DM Mono',monospace;font-size:.54rem;letter-spacing:.22em;text-transform:uppercase;color:rgba(171,163,143,.52);margin-bottom:.7rem;display:flex;align-items:center;gap:.4rem;flex-wrap:wrap}
.flbl .req{color:rgba(196,97,74,.8);font-size:.6rem}
.flbl .opt{opacity:.5}
.flbl .soft{color:rgba(201,168,76,.6);font-size:.48rem;letter-spacing:.08em;text-transform:none;font-family:'Inter',sans-serif;font-style:italic;font-weight:300}
.finp{width:100%;background:transparent;border:none;color:rgba(217,212,200,.92);font-size:1rem;font-family:'Inter',sans-serif;outline:none;padding:0;font-weight:400}
.finp.error-text{color:rgba(196,97,74,0.75)}
.finp::placeholder{color:rgba(171,163,143,.28)}
.finp option{background:#1a1714}
.search-action{padding:1.1rem 1.8rem;background:rgba(18,15,12,.82);border-top:1px solid var(--bd2);display:flex;align-items:center;justify-content:space-between;gap:1rem}
.sa-l{display:flex;align-items:center;gap:1.8rem}
.sa-hint{font-family:'DM Mono',monospace;font-size:.5rem;letter-spacing:.16em;text-transform:uppercase;color:rgba(171,163,143,.18)}
.sa-hint kbd{color:rgba(171,163,143,.35);font-style:normal}
.req-note{font-family:'DM Mono',monospace;font-size:.48rem;letter-spacing:.14em;color:rgba(121,46,41,.4)}
.sa-btn{font-family:'DM Mono',monospace;font-size:.62rem;letter-spacing:.2em;text-transform:uppercase;color:var(--t);background:var(--g);border:none;border-radius:5px;padding:.65rem 1.8rem;cursor:pointer;transition:.25s;box-shadow:0 0 28px rgba(121,46,41,.18);white-space:nowrap;flex-shrink:0}
.sa-btn:hover{background:var(--g2);box-shadow:0 0 50px rgba(121,46,41,.38);transform:translateY(-1px)}
/* LOADER */
.loader-overlay{position:fixed;inset:0;z-index:500;background:rgba(16,13,11,.97);backdrop-filter:blur(30px);display:flex;flex-direction:column;align-items:center;justify-content:center;gap:2rem}
.l-cross{width:52px;height:52px;position:relative;animation:rcross 3s linear infinite}
.l-cross::before,.l-cross::after{content:'';position:absolute;background:rgba(121,46,41,.75)}
.l-cross::before{width:1px;height:100%;top:0;left:50%;transform:translateX(-50%)}
.l-cross::after{width:100%;height:1px;left:0;top:50%;transform:translateY(-50%)}
.l-ring{position:absolute;inset:-14px;border:1px solid transparent;border-top-color:rgba(121,46,41,.5);border-right-color:rgba(121,46,41,.18);border-radius:50%;animation:spin 1.4s linear infinite}
@keyframes rcross{to{transform:rotate(90deg)}}
@keyframes spin{to{transform:rotate(360deg)}}
.l-text{font-family:'DM Serif Display',serif;font-size:.95rem;color:var(--gr);letter-spacing:.1em}
.l-step{font-family:'DM Mono',monospace;font-size:.55rem;color:rgba(171,163,143,.28);letter-spacing:.18em;text-transform:uppercase;animation:blink 1.8s ease infinite}
@keyframes blink{0%,100%{opacity:.3}50%{opacity:1}}
/* RESULTS */
.results-wrap{position:relative;z-index:1;padding:5.5rem 2rem 4rem;min-height:100vh}
.rc{width:100%;max-width:700px;margin:0 auto}
.rhead{display:flex;align-items:center;justify-content:space-between;margin-bottom:2.2rem}
.bbtn{font-family:'DM Mono',monospace;font-size:.57rem;letter-spacing:.18em;text-transform:uppercase;color:var(--gr);background:rgba(36,32,29,.7);border:1px solid var(--bd);padding:.38rem .9rem;border-radius:6px;cursor:pointer;transition:.2s}
.bbtn:hover{color:var(--t);border-color:rgba(171,163,143,.22)}
.propid{font-family:'DM Mono',monospace;font-size:.52rem;letter-spacing:.2em;color:rgba(171,163,143,.28);text-transform:uppercase}
.sh{text-align:center;padding:3.5rem 2rem 2.8rem;background:rgba(20,17,14,.65);border:1px solid var(--bd);border-radius:22px;margin-bottom:1.2rem;position:relative;overflow:hidden;animation:fadeUp .7s cubic-bezier(.16,1,.3,1) both}
.sh::before{content:'';position:absolute;inset:0;background:radial-gradient(ellipse 80% 50% at 50% -5%,rgba(121,46,41,.1),transparent 58%)}
.sh::after{content:'';position:absolute;top:0;left:0;right:0;height:1px;background:linear-gradient(90deg,transparent,rgba(121,46,41,.3),transparent)}
.cc{position:absolute;width:14px;height:14px}
.cc.tl{top:14px;left:14px;border-top:1px solid rgba(121,46,41,.28);border-left:1px solid rgba(121,46,41,.28)}
.cc.tr{top:14px;right:14px;border-top:1px solid rgba(121,46,41,.28);border-right:1px solid rgba(121,46,41,.28)}
.cc.bl{bottom:14px;left:14px;border-bottom:1px solid rgba(121,46,41,.28);border-left:1px solid rgba(121,46,41,.28)}
.cc.br{bottom:14px;right:14px;border-bottom:1px solid rgba(121,46,41,.28);border-right:1px solid rgba(121,46,41,.28)}
.slbl{font-family:'DM Mono',monospace;font-size:.72rem;font-weight:700;letter-spacing:.35em;text-transform:uppercase;color:rgba(171,163,143,.5);margin-bottom:1.2rem;position:relative;z-index:1}
.snum{font-family:'DM Serif Display',serif;font-size:clamp(6rem,16vw,9rem);font-weight:400;line-height:.9;color:var(--t);position:relative;z-index:1;margin-bottom:1.4rem;letter-spacing:-.03em;text-shadow:0 0 80px rgba(121,46,41,.18)}
.srisk{display:inline-flex;align-items:center;gap:.5rem;font-family:'DM Mono',monospace;font-size:.62rem;font-weight:500;letter-spacing:.25em;text-transform:uppercase;padding:.38rem 1.4rem;border-radius:3px;position:relative;z-index:1;margin-bottom:1.8rem}
.srisk::before{content:'';width:5px;height:5px;border-radius:50%;background:currentColor;flex-shrink:0}
.risk-med{color:var(--gold);background:rgba(201,168,76,.06);border:1px solid rgba(201,168,76,.2)}
.risk-low{color:var(--green);background:rgba(106,155,94,.06);border:1px solid rgba(106,155,94,.2)}
.risk-high{color:var(--red);background:rgba(196,97,74,.06);border:1px solid rgba(196,97,74,.2)}
.smtr{width:200px;height:1px;margin:0 auto;background:rgba(171,163,143,.07);position:relative;z-index:1;overflow:hidden}
.smtrf{height:100%;background:linear-gradient(90deg,var(--green),var(--gold),var(--red));transform:scaleX(0);transform-origin:left}
.smtrf.animate{animation:barf 1.8s cubic-bezier(.16,1,.3,1) .5s forwards}
@keyframes barf{to{transform:scaleX(1)}}
.smeta{font-family:'DM Mono',monospace;font-size:.62rem;font-weight:600;color:rgba(171,163,143,.35);letter-spacing:.15em;margin-top:1.2rem;position:relative;z-index:1}
.prop-meta-pills{display:flex;align-items:center;justify-content:center;gap:.55rem;margin-top:.9rem;position:relative;z-index:1;flex-wrap:wrap}
.pmp{font-family:'DM Mono',monospace;font-size:.58rem;font-weight:600;letter-spacing:.14em;text-transform:uppercase;color:rgba(171,163,143,.45);background:rgba(26,23,20,.6);border:1px solid var(--bd2);padding:.32rem .8rem;border-radius:3px}
.rb{background:rgba(20,17,14,.6);border:1px solid var(--bd2);border-radius:16px;padding:1.8rem 2rem;margin-bottom:1.2rem;position:relative;overflow:hidden;animation:fadeUp .6s cubic-bezier(.16,1,.3,1) both;transition:border-color .3s}
.rb:hover{border-color:var(--bd)}
.stripe{position:absolute;left:0;top:1.5rem;bottom:1.5rem;width:2px;border-radius:0 1px 1px 0}
.sg{background:linear-gradient(to bottom,var(--g),transparent)}.so{background:linear-gradient(to bottom,var(--o),transparent)}.sgr{background:linear-gradient(to bottom,var(--gr),transparent)}
.blbl{font-family:'DM Mono',monospace;font-size:.72rem;font-weight:700;letter-spacing:.28em;text-transform:uppercase;color:rgba(171,163,143,.5);margin-bottom:1.6rem;display:flex;align-items:center;gap:.8rem}
.blbl::after{content:'';flex:1;height:1px;background:var(--bd2)}
.tlw{padding-left:.2rem}
.ti{display:grid;grid-template-columns:10px 52px 1fr;gap:0 1rem;align-items:start}
.tsp{display:flex;flex-direction:column;align-items:center}
.tn{width:10px;height:10px;border-radius:50%;flex-shrink:0;margin-top:4px;border:1.5px solid;position:relative;z-index:1}
.tln{width:1px;flex:1;min-height:34px;margin-top:3px;opacity:.22}
.tn1{background:var(--g);border-color:rgba(121,46,41,.8);box-shadow:0 0 10px rgba(121,46,41,.35)}
.tn2{background:var(--o);border-color:rgba(86,85,56,.8);box-shadow:0 0 10px rgba(86,85,56,.35)}
.tn3{background:var(--gr);border-color:rgba(171,163,143,.55)}
.tn4{background:var(--red);border-color:rgba(196,97,74,.6);box-shadow:0 0 10px rgba(196,97,74,.35)}
.tyr{font-family:'DM Mono',monospace;font-size:.6rem;color:rgba(171,163,143,.32);padding-top:4px}
.tnm{font-family:'DM Serif Display',serif;font-size:1.05rem;line-height:1.2;margin-bottom:.18rem;color:var(--t)}
.tty{font-family:'DM Mono',monospace;font-size:.55rem;letter-spacing:.14em;text-transform:uppercase;color:rgba(171,163,143,.28);margin-bottom:1.3rem}
.ti-last .tty{margin-bottom:0;color:rgba(196,97,74,.42)}.ti-last .tnm{color:var(--red)}
.ftr{border:1px solid rgba(171,163,143,.07);border-radius:10px;padding:1.4rem 1.6rem;margin-top:1.2rem;background:rgba(14,11,9,.4);position:relative}
.ftr::before{content:'INHERITANCE TREE';position:absolute;top:-.42rem;left:1rem;font-family:'DM Mono',monospace;font-size:.43rem;letter-spacing:.22em;color:var(--gr);background:var(--r2);padding:0 .5rem;opacity:.38}
.ftr-r{display:flex;align-items:baseline;gap:.8rem;font-size:.8rem;margin-bottom:.55rem}
.ftr-k{font-family:'DM Mono',monospace;font-size:.64rem;font-weight:700;letter-spacing:.14em;text-transform:uppercase;color:rgba(171,163,143,.4);white-space:nowrap;min-width:95px}
.ftr-v{color:var(--t);font-size:.92rem;font-weight:600}
.ftr-hs{border-left:1px solid rgba(86,85,56,.25);margin-left:95px;padding-left:.9rem;margin-top:-.1rem;margin-bottom:.8rem}
.ftr-h{font-size:.88rem;font-weight:600;color:rgba(217,212,200,.6);padding:.22rem 0;display:flex;align-items:center;gap:.5rem}
.ftr-h::before{content:'';width:12px;height:1px;background:rgba(86,85,56,.3);flex-shrink:0}
.ftr-w{font-family:'DM Mono',monospace;display:inline-flex;align-items:center;gap:.5rem;font-size:.66rem;font-weight:700;letter-spacing:.14em;text-transform:uppercase;color:var(--red);border:1px solid rgba(196,97,74,.18);padding:.36rem .85rem;border-radius:2px;background:rgba(196,97,74,.04)}
.ftr-w::before{content:'!';width:13px;height:13px;border-radius:50%;border:1px solid var(--red);display:flex;align-items:center;justify-content:center;font-size:.5rem;flex-shrink:0}
.flags{display:flex;flex-direction:column;gap:.55rem}
.flag{display:grid;grid-template-columns:20px 1fr;gap:0 .85rem;align-items:start;padding:.72rem .95rem;background:rgba(196,97,74,.04);border:1px solid rgba(196,97,74,.1);border-radius:7px;transition:.22s;cursor:default}
.flag:hover{background:rgba(196,97,74,.07);border-color:rgba(196,97,74,.18);transform:translateX(4px)}
.fi{width:18px;height:18px;border:1px solid rgba(196,97,74,.32);border-radius:2px;display:flex;align-items:center;justify-content:center;font-family:'DM Mono',monospace;font-size:.58rem;color:var(--red);flex-shrink:0;margin-top:2px}
.ftxt{font-size:.81rem;color:rgba(217,212,200,.58);line-height:1.55}
.ftxt strong{color:var(--red);font-weight:600}
.aip{font-size:.86rem;line-height:1.88;color:rgba(217,212,200,.55);font-weight:300;padding:1.2rem 1.4rem;border-left:1.5px solid rgba(121,46,41,.22);background:rgba(14,11,9,.3);border-radius:0 7px 7px 0}
.recs{display:flex;flex-direction:column}
.rec{display:grid;grid-template-columns:22px 1fr;gap:0 .9rem;align-items:start;padding:.62rem .4rem;border-bottom:1px solid var(--bd2);transition:.2s;cursor:default}
.rec:last-child{border-bottom:none}
.rec:hover{padding-left:.75rem}
.rec:hover .rt{color:var(--t)}
.ri{width:19px;height:19px;border-radius:50%;border:1px solid rgba(86,85,56,.38);display:flex;align-items:center;justify-content:center;flex-shrink:0;margin-top:2px}
.ri::after{content:'';width:5px;height:5px;border-bottom:1.5px solid var(--green);border-right:1.5px solid var(--green);transform:rotate(45deg) translate(-1px,-1px)}
.rt{font-size:.81rem;color:rgba(217,212,200,.5);line-height:1.55}
.foot{text-align:center;padding:2.5rem 0 2rem;font-family:'DM Mono',monospace;font-size:.48rem;letter-spacing:.2em;text-transform:uppercase;color:rgba(171,163,143,.12)}
.foot span{margin:0 .6rem;opacity:.5}
@keyframes fadeUp{from{opacity:0;transform:translateY(22px)}to{opacity:1;transform:translateY(0)}}

@media(max-width:760px){
  .about-grid,.fields-grid{grid-template-columns:1fr}
  .hero-h1{font-size:3.2rem}.snum{font-size:5.5rem}
  nav{padding:0 1.4rem}
  .nav-btn:not(.nav-cta){display:none}
  #about,#get-started{padding:5rem 1.5rem}
  #home{padding:7rem 1.5rem 5rem}
  .stats-row{flex-direction:column}
  .stat{border-right:none;border-bottom:1px solid var(--bd)}
  .stat:last-child{border-bottom:none}
  .presets{gap:.4rem}
}
`;

const STEPS = [
  'Querying land registry databases',
  'Reconstructing ownership lineage',
  'Cross-referencing encumbrance records',
  'Parsing mutation history',
  'Running AI risk assessment',
  'Computing title confidence score'
];

const PRESETS = [
  { label: 'Whitefield, Bengaluru', data: { survey: '84/3B', district: 'Bengaluru Urban', taluk: 'Mahadevapura', state: 'Karnataka', village: 'Whitefield', owner: '', propType: 'Residential', area: '2400 sq ft' } },
  { label: 'Agricultural, Mysuru', data: { survey: '221/1A', district: 'Mysuru', taluk: 'Nanjangud', state: 'Karnataka', village: 'Bilikere', owner: '', propType: 'Agricultural', area: '3.5 acres' } },
  { label: 'Commercial, Pune', data: { survey: '47/12', district: 'Pune', taluk: 'Haveli', state: 'Maharashtra', village: 'Kharadi', owner: '', propType: 'Commercial', area: '1800 sq ft' } },
];

// eslint-disable-next-line no-unused-vars
const QUICK_PILLS = [
  'What does this score mean?',
  'How do I fix the mutation gap?',
  'Steps to clear the loan encumbrance',
  'Is this safe to buy?',
  'What is a partition deed?',
  'How long will resolution take?',
];

function Particles() {
  const particles = Array.from({ length: 20 }, () => ({
    left: `${Math.random() * 100}%`,
    size: `${1 + Math.random() * 2}px`,
    duration: `${14 + Math.random() * 18}s`,
    delay: `${-Math.random() * 25}s`,
  }));
  return (
    <div style={{ position:'fixed', inset:0, zIndex:0, pointerEvents:'none', overflow:'hidden' }}>
      {particles.map((p, i) => (
        <div key={i} className="pt" style={{ left:p.left, width:p.size, height:p.size, animationDuration:p.duration, animationDelay:p.delay }}/>
      ))}
    </div>
  );
}

function useCountUp(target, duration, active) {
  const [val, setVal] = useState(0);
  useEffect(() => {
    if (!active) return;
    const t0 = performance.now();
    let raf;
    const tick = (now) => {
      const p = Math.min((now - t0) / duration, 1);
      const e = 1 - Math.pow(1 - p, 3);
      setVal(Math.round(e * target));
      if (p < 1) raf = requestAnimationFrame(tick);
    };
    raf = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(raf);
  }, [target, duration, active]);
  return val;
}

function StatItem({ target, suffix, label, active }) {
  const val = useCountUp(target, 2200, active);
  return (
    <div className="stat">
      <div className="stat-num">{val.toLocaleString()}<span className="u">{suffix}</span></div>
      <div className="stat-lbl">{label}</div>
    </div>
  );
}

function ScoreCount({ target, active }) {
  const val = useCountUp(target, 1600, active);
  return <div className="snum">{val}</div>;
}

const EMPTY_FORM = { survey:'', district:'', taluk:'', state:'Karnataka', village:'', owner:'', propType:'', area:'', seed: null };

// ── Prototype seed helpers ─────────────────────────────────────────────────
const SEED_DISTRICTS = [
  {district:'Bengaluru Urban',taluk:'Mahadevapura',village:'Whitefield',state:'Karnataka',propType:'Residential'},
  {district:'Mysuru',taluk:'Nanjangud',village:'Bilikere',state:'Karnataka',propType:'Agricultural'},
  {district:'Pune',taluk:'Haveli',village:'Kharadi',state:'Maharashtra',propType:'Commercial'},
  {district:'Chennai',taluk:'Tambaram',village:'Pallavaram',state:'Tamil Nadu',propType:'Residential'},
  {district:'Hyderabad',taluk:'Serilingampally',village:'Gachibowli',state:'Telangana',propType:'Commercial'},
  {district:'Thiruvananthapuram',taluk:'Neyyattinkara',village:'Balaramapuram',state:'Kerala',propType:'Agricultural'},
  {district:'Ahmedabad',taluk:'Daskroi',village:'Bopal',state:'Gujarat',propType:'Industrial'},
  {district:'Jaipur',taluk:'Sanganer',village:'Mansarovar',state:'Rajasthan',propType:'Residential'},
];
const SEED_OWNERS = ['Ramesh Iyer','Suresh Nair','Kavitha Reddy','Mohan Das','Priya Sharma','Arun Patel','Lakshmi Devi','Vijay Kumar'];
const SEED_AREAS  = ['1200 sq ft','2400 sq ft','3.5 acres','0.75 acres','1800 sq ft','4200 sq ft','1.2 acres','800 sq ft'];

function generateFormFromSeed(n) {
  const v = Math.max(1, Math.min(1000, Number(n)));
  const idx = Math.floor(((v - 1) / 999) * (SEED_DISTRICTS.length - 1));
  const loc = SEED_DISTRICTS[idx];
  const oIdx = Math.floor(((v - 1) / 999) * (SEED_OWNERS.length - 1));
  const aIdx = Math.floor(((v - 1) / 999) * (SEED_AREAS.length - 1));
  const surveyBase = Math.floor(1 + ((v - 1) / 999) * 498);
  const surveyFrag = v % 4 === 0 ? `${surveyBase}/2A` : v % 3 === 0 ? `${surveyBase}/1B` : v % 2 === 0 ? `${surveyBase}/3` : `${surveyBase}`;
  return {
    survey: surveyFrag,
    district: loc.district,
    taluk: loc.taluk,
    village: loc.village,
    state: loc.state,
    propType: loc.propType,
    owner: SEED_OWNERS[oIdx],
    area: SEED_AREAS[aIdx],
    seed: v, // Store seed for dynamic risk calculation
  };
}

function getRiskHint(n) {
  const v = Number(n);
  if (!v) return { text: '', color: 'rgba(171,163,143,.35)' };
  // Calculate approximate score to show user
  const approxScore = Math.round(950 - ((v - 1) / 999) * 800);
  if (v <= 200)  return { text: `Score ~${approxScore} — Clean title, safe to proceed.`, color: 'var(--green)' };
  if (v <= 500)  return { text: `Score ~${approxScore} — Moderate risk, some gaps to resolve.`, color: 'var(--gold)' };
  if (v <= 800)  return { text: `Score ~${approxScore} — High risk, disputes detected.`, color: 'var(--red)' };
  return { text: `Score ~${approxScore} — Severe risk, do not transact.`, color: 'var(--red)' };
}

function PrototypeSeed({ onFill }) {
  const [seed, setSeed] = useState('');
  const hint = getRiskHint(seed);
  const handleFill = () => {
    const v = parseInt(seed, 10);
    if (!v || v < 1 || v > 1000) return;
    const formData = generateFormFromSeed(v);
    onFill(formData);
  };
  return (
    <div className="proto-seed">
  
      <div className="proto-inline">
        <span className="proto-inline-lbl">Seed number</span>
        <input
          className="proto-num-inp"
          type="number" min="1" max="1000"
          placeholder="1 – 1000"
          value={seed}
          onChange={e => setSeed(e.target.value)}
          onKeyDown={e => { if (e.key === 'Enter') handleFill(); }}
        />
        <button className="proto-fill-btn" onClick={handleFill}>Autofill →</button>
        {hint.text && <span className="proto-hint-inline" style={{color: hint.color, marginLeft: '1rem'}}>{hint.text}</span>}
      </div>
    </div>
  );
}

// ── Landing ────────────────────────────────────────────────────────────────
function LandingView({ onAnalyze }) {
  const statsRef = useRef(null);
  const [statsActive, setStatsActive] = useState(false);
  const [form, setForm] = useState(EMPTY_FORM);
  const [errors, setErrors] = useState({});
  const [focused, setFocused] = useState({});

  useEffect(() => {
    const obs = new IntersectionObserver(([e]) => { if (e.isIntersecting) setStatsActive(true); }, { threshold: 0.3 });
    if (statsRef.current) obs.observe(statsRef.current);
    return () => obs.disconnect();
  }, []);

  const handleAnalyze = () => {
    const newErrors = {};
    if (!form.survey.trim()) newErrors.survey = true;
    if (!form.district.trim()) newErrors.district = true;
    if (!form.taluk.trim()) newErrors.taluk = true;
    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      setTimeout(() => setErrors({}), 2200);
      return;
    }
    onAnalyze(form);
  };

  const applyPreset = (data) => {
    setForm({ ...EMPTY_FORM, ...data });
    setTimeout(() => document.getElementById('get-started')?.scrollIntoView({ behavior:'smooth' }), 50);
  };

  const applySeeed = (data) => {
    setForm({ ...EMPTY_FORM, ...data });
  };

  const scrollTo = (id) => document.getElementById(id)?.scrollIntoView({ behavior:'smooth' });

  const bind = (id) => ({
    value: form[id],
    onChange: e => setForm(f => ({ ...f, [id]: e.target.value })),
    onFocus: () => setFocused(f => ({ ...f, [id]: true })),
    onBlur: () => setFocused(f => ({ ...f, [id]: false })),
    onKeyDown: e => { if (e.key === 'Enter') handleAnalyze(); },
    className: `finp${errors[id] ? ' error-text' : ''}`,
    autoComplete: 'off',
  });

  const cell = (id) => `fcell${errors[id] ? ' error' : ''}${focused[id] ? ' focused' : ''}`;

  return (
    <div id="landing">
      <section id="home">
        <h1 className="hero-h1">Every Land Title<em>Has a Story.</em><span className="sw">We decode it.</span></h1>
        <p className="hero-desc">Reconstruct ownership lineage, detect legal risks, and generate a Title Confidence Score for any property, built to simplify India's complex land records.</p>
        <div className="hero-actions">
          <button className="btn-p" onClick={() => scrollTo('get-started')}>Analyze a Property →</button>
          <button className="btn-g" onClick={() => scrollTo('about')}>How it works</button>
        </div>
        <div className="stats-row" ref={statsRef}>
          <StatItem target={1000} suffix="" label="Synthetic Properties Analyzed" active={statsActive}/>
          <StatItem target={30} suffix="+" label="Legal Risk Indicators Modeled" active={statsActive}/>
          <StatItem target={3} suffix="-gen" label="Ownership Lineage Simulation" active={statsActive}/>
          <StatItem target={10} suffix="s" label="Avg. Analysis Time" active={statsActive}/>
        </div>
        <div className="scroll-cue"><div className="sct">Scroll</div><div className="scl"/></div>
      </section>

      <div className="divider"/>

      <section id="about">
        <div className="about-grid">
          <div>
            <div className="sec-tag">What we do</div>
            <h2 className="sec-h">Land ownership in India is <em>complicated.</em></h2>
            <p className="sec-p">Decades of undocumented transfers, missing mutation records, and fragmented state registries make verifying a title a legal minefield. One unclear chain of custody can block a sale for years.</p>
            <p className="sec-p">Lineage reconstructs ownership history, detects legal gaps, and calculates a Title Confidence Score using structured land record data.</p>
          </div>
          <div className="acards">
            {[
              ['01','Lineage Reconstruction','Traces every owner back to original allotment. Sale deeds, inheritance, court orders — all mapped.'],
              ['02','Encumbrance Detection',"Surfaces active loans, liens, and disputed claims that don't appear in standard registry searches."],
              ['03','Title Confidence Score','A single 0–1000 score summarising legal risk, with plain-language AI explanation and action steps.'],
              ['04','Mutation Gap Analysis','Identifies periods where ownership transferred but mutation records were never updated in time.'],
            ].map(([n,t,d]) => (
              <div className="acard" key={n}>
                <div className="acard-n">{n}</div>
                <div><div className="acard-t">{t}</div><div className="acard-d">{d}</div></div>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section id="get-started">
        <div className="gs-hdr">
          <div className="sec-tag">Get Started</div>
          <h2 className="gs-h">Enter property details</h2>
          <p className="gs-s">Survey number + village + district + taluk uniquely identifies any parcel in India.</p>
        </div>

        <PrototypeSeed onFill={applySeeed}/>

        <div className="presets">
          <span className="preset-lbl">Try an example →</span>
          {PRESETS.map(p => (
            <button key={p.label} className="preset-btn" onClick={() => applyPreset(p.data)}>{p.label}</button>
          ))}
        </div>

        <div className="search-block">
          <div className="fields-grid">
            <div className={cell('survey')}>
              <div className="flbl"><span className="req">*</span>Survey Number</div>
              <input {...bind('survey')} type="text" placeholder="84/3B"/>
            </div>
            <div className={cell('district')}>
              <div className="flbl"><span className="req">*</span>District</div>
              <input {...bind('district')} type="text" placeholder="Bengaluru Urban"/>
            </div>
            <div className={cell('taluk')}>
              <div className="flbl"><span className="req">*</span>Taluk</div>
              <input {...bind('taluk')} type="text" placeholder="Mahadevapura"/>
            </div>
            <div className={`fcell${focused.village ? ' focused' : ''}`}>
              <div className="flbl">Village <span className="soft">— recommended</span></div>
              <input {...bind('village')} type="text" placeholder="Whitefield"/>
            </div>
            <div className={`fcell${focused.propType ? ' focused' : ''}`}>
              <div className="flbl">Property Type<span className="opt">&nbsp;—&nbsp;optional</span></div>
              <select value={form.propType} onChange={e => setForm(f=>({...f,propType:e.target.value}))}
                onFocus={()=>setFocused(f=>({...f,propType:true}))} onBlur={()=>setFocused(f=>({...f,propType:false}))}
                className="finp">
                <option value="">— Select —</option>
                <option>Residential</option>
                <option>Agricultural</option>
                <option>Commercial</option>
                <option>Industrial</option>
              </select>
            </div>
            <div className={`fcell${focused.area ? ' focused' : ''}`}>
              <div className="flbl">Area / Extent<span className="opt">&nbsp;—&nbsp;optional</span></div>
              <input {...bind('area')} type="text" placeholder="2400 sq ft  /  1.2 acres"/>
            </div>
            <div className={`fcell${focused.state ? ' focused' : ''}`}>
              <div className="flbl">State<span className="opt">&nbsp;—&nbsp;optional</span></div>
              <select value={form.state} onChange={e=>setForm(f=>({...f,state:e.target.value}))}
                onFocus={()=>setFocused(f=>({...f,state:true}))} onBlur={()=>setFocused(f=>({...f,state:false}))}
                className="finp">
                <option value="">— Select —</option>
                {['Karnataka','Maharashtra','Tamil Nadu','Andhra Pradesh','Telangana','Kerala','Gujarat','Rajasthan','Uttar Pradesh','West Bengal'].map(s=><option key={s}>{s}</option>)}
              </select>
            </div>
            <div className={`fcell${focused.owner ? ' focused' : ''}`} style={{gridColumn:'span 2'}}>
              <div className="flbl">Owner Name<span className="opt">&nbsp;—&nbsp;optional</span></div>
              <input {...bind('owner')} type="text" placeholder="Mahesh Kumar"/>
            </div>
          </div>
          <div className="search-action">
            <div className="sa-l">
              <div className="sa-hint">Press <kbd>↵ Enter</kbd> to analyze</div>
              <div className="req-note">* required fields</div>
            </div>
            <button className="sa-btn" onClick={handleAnalyze}>Analyze Ownership →</button>
          </div>
        </div>
      </section>
    </div>
  );
}

// ── Loader ─────────────────────────────────────────────────────────────────
function Loader({ step }) {
  return (
    <div className="loader-overlay">
      <div className="l-cross"><div className="l-ring"/></div>
      <div className="l-text">Analyzing Property Records</div>
      <div className="l-step">{step}</div>
    </div>
  );
}

function getRisk(score) {
  if (score >= 850) return { cls:'risk-low', label:'Low Risk' };
  if (score >= 650) return { cls:'risk-med', label:'Medium Risk' };
  return { cls:'risk-high', label:'High Risk' };
}

// ── Dynamic data generation based on seed ──────────────────────────────────
function generateScoreFromSeed(seed) {
  if (!seed) return 742; // Default fallback
  const v = Number(seed);
  // Lower seed = higher score (safer), higher seed = lower score (riskier)
  // Seed 1 = ~950 score, Seed 1000 = ~150 score
  const baseScore = Math.round(950 - ((v - 1) / 999) * 800);
  // Add some variation based on seed
  const variation = (v * 7) % 50 - 25;
  return Math.max(50, Math.min(980, baseScore + variation));
}

function generateLineageFromSeed(seed, score) {
  const v = Number(seed) || 500;
  const isHighRisk = score < 400;
  const isMediumRisk = score >= 400 && score < 700;
  
  const owners = [
    ['Rajendra Singh', 'Suresh Kumar', 'Mahesh Gupta', 'Ramesh Iyer', 'Krishna Rao'],
    ['Venkatesh Reddy', 'Anand Sharma', 'Vijay Patel', 'Mohan Das', 'Prakash Nair'],
    ['Arun Kumar', 'Sanjay Verma', 'Deepak Joshi', 'Amit Singh', 'Rahul Menon'],
    ['Disputed Party', 'Under Legal Review', 'Contested Ownership', 'Multiple Claimants', 'Pending Resolution'],
  ];
  
  const ownerIdx = v % 5;
  const baseYear = 1970 + (v % 30);
  
  const lineage = [
    {cls:'tn1', lnClr:'var(--g)', yr: String(baseYear), nm: owners[0][ownerIdx], ty:'Original Govt. Allotment'},
    {cls:'tn2', lnClr:'var(--o)', yr: String(baseYear + 12 + (v % 8)), nm: owners[1][ownerIdx], ty:'Sale Deed · Registered'},
  ];
  
  if (isMediumRisk || isHighRisk) {
    lineage.push({cls:'tn3', lnClr:'var(--gr)', yr: String(baseYear + 25 + (v % 10)), nm: owners[2][ownerIdx], ty:'Inheritance · Probate Filed'});
  }
  
  if (isHighRisk) {
    lineage.push({cls:'tn4', lnClr:null, yr:'2024', nm: owners[3][v % 5], ty:`Mutation gap — ${2018 + (v % 6)}`, last:true});
  } else if (isMediumRisk) {
    lineage[lineage.length - 1].last = true;
    lineage[lineage.length - 1].lnClr = null;
  } else {
    lineage[lineage.length - 1].last = true;
    lineage[lineage.length - 1].lnClr = null;
  }
  
  return lineage;
}

function generateFlagsFromSeed(seed, score, isAgri) {
  const v = Number(seed) || 500;
  const flags = [];
  
  // High risk (score < 400) - many flags
  if (score < 400) {
    flags.push(['Pending litigation', `— Case No. ${v}/${2020 + (v % 4)} in Civil Court`]);
    flags.push(['Multiple ownership claims', '— 3+ parties claiming title rights']);
    flags.push(['Missing mutation record', `— not updated since ${2015 + (v % 8)}`]);
    const loanAmount = 20 + (v % 80);
    flags.push(['Active loan encumbrance', `— Bank Loan, ₹${loanAmount} Lakhs outstanding`]);
    flags.push(['Boundary dispute', '— neighboring property overlap detected']);
  }
  // Medium risk (score 400-700) - some flags
  else if (score < 700) {
    flags.push(['Missing mutation record', `— not updated since ${2018 + (v % 5)}`]);
    const loanAmount = 15 + (v % 50);
    flags.push(['Active loan encumbrance', `— Home Loan, ₹${loanAmount} Lakhs outstanding`]);
    if (v % 3 === 0) {
      flags.push(['Partition record absent', '— legal heirs identified, no deed filed']);
    }
  }
  // Low risk (score >= 700) - minimal or no flags
  else {
    if (v % 4 === 0) {
      flags.push(['Minor documentation gap', '— easily rectifiable at sub-registrar']);
    }
  }
  
  if (isAgri && score < 800) {
    flags.push(['Agricultural land ceiling', '— verify compliance with Land Reforms Act']);
  }
  
  return flags;
}

function generateRecommendationsFromSeed(score, isAgri) {
  const recs = [];
  
  if (score < 400) {
    recs.push('URGENT: Do not proceed with transaction until litigation is resolved');
    recs.push('Engage a property lawyer to review all disputed claims');
    recs.push('Obtain court clearance certificate before any payment');
    recs.push('Verify all claimant identities with original documents');
    recs.push('Consider title insurance if proceeding after resolution');
  } else if (score < 700) {
    recs.push('Verify and update mutation records at the sub-registrar office');
    recs.push('Obtain official loan closure certificate and register release deed');
    recs.push('File formal partition deed co-signed by all legal heirs');
    recs.push('Cross-verify Khata extract for current ownership status');
  } else {
    recs.push('Standard due diligence recommended before transaction');
    recs.push('Verify latest property tax receipts are cleared');
    recs.push('Confirm seller identity with Aadhaar/PAN verification');
  }
  
  recs.push('Commission a licensed surveyor to confirm plot boundaries');
  
  if (isAgri) {
    recs.push('Verify land ceiling compliance and obtain NOC under Land Reforms Act');
    recs.push('Check for any pending land acquisition notifications');
  }
  
  return recs;
}

function generateAIAnalysisFromSeed(seed, score, isAgri, form) {
  const v = Number(seed) || 500;
  
  if (score >= 700) {
    return `This ${isAgri ? 'agricultural ' : ''}property in ${form.district}, ${form.state} demonstrates a clear ownership chain with minimal legal concerns. The title confidence score of ${score}/1000 indicates low risk. All critical documentation appears to be in order, with properly registered transfers and updated mutation records. Standard due diligence is recommended before proceeding with any transaction, including verification of the latest property tax receipts and seller identity confirmation. ${isAgri ? 'As agricultural land, ensure compliance with state-specific land ceiling regulations.' : ''} This property is generally safe for transaction with routine precautions.`;
  } else if (score >= 400) {
    return `This ${isAgri ? 'agricultural ' : ''}property in ${form.district}, ${form.state} carries moderate legal risk with a confidence score of ${score}/1000. The mutation record has not been updated since ${2018 + (v % 5)}, leaving current ownership status potentially ambiguous in official land registers. An active bank loan creates a financial encumbrance that must be formally discharged prior to any transfer. ${v % 3 === 0 ? 'Additionally, legal heirs from a previous inheritance have not filed a partition deed — this gap elevates dispute risk. ' : ''}No transaction should proceed without resolving the identified flags. ${isAgri ? 'Agricultural land transfers require additional regulatory scrutiny under state Land Reforms Acts.' : ''}`;
  } else {
    return `CRITICAL ALERT: This ${isAgri ? 'agricultural ' : ''}property in ${form.district}, ${form.state} presents severe legal risk with a confidence score of only ${score}/1000. Active litigation (Case No. ${v}/${2020 + (v % 4)}) is pending in Civil Court with multiple parties claiming title rights. The ownership chain shows significant gaps, and boundary disputes with neighboring properties have been detected. A substantial bank encumbrance of ₹${20 + (v % 80)} Lakhs remains outstanding. DO NOT PROCEED with any transaction until all legal matters are fully resolved. Immediate consultation with a property litigation specialist is strongly advised. ${isAgri ? 'Additional complications arise from agricultural land ceiling regulations.' : ''}`;
  }
}

function generateFamilyTreeFromSeed(seed, score) {
  const v = Number(seed) || 500;
  const families = [
    { surname: 'Patel', heirs: ['Mahesh', 'Anita', 'Kavya'] },
    { surname: 'Sharma', heirs: ['Rajiv', 'Priya', 'Neha'] },
    { surname: 'Reddy', heirs: ['Venkat', 'Lakshmi'] },
    { surname: 'Kumar', heirs: ['Arun', 'Sunita', 'Deepa', 'Ravi'] },
    { surname: 'Singh', heirs: ['Amit', 'Rekha'] },
  ];
  
  const family = families[v % 5];
  const originalOwners = ['Suresh', 'Mohan', 'Ramesh', 'Prakash', 'Vijay'];
  
  return {
    originalOwner: `${originalOwners[v % 5]} ${family.surname}`,
    heirs: family.heirs.map((name, i) => ({
      name: `${name} ${family.surname}`,
      relation: i === 0 ? 'Son' : 'Daughter'
    })),
    partitionStatus: score < 700 ? 'Partition Record Missing' : 'Partition Complete'
  };
}

// ── Results ────────────────────────────────────────────────────────────────
function ResultsView({ form, apiData, onBack }) {
  const [scoreActive, setScoreActive] = useState(false);
  
  // Calculate score dynamically from seed if no API data
  const seed = form.seed;
  const score = apiData?.score || generateScoreFromSeed(seed);
  const risk = getRisk(score);
  const propId = `${form.survey} · ${form.district} · ${form.taluk}`.toUpperCase();
  const isAgri = form.propType === 'Agricultural';

  // Generate all data dynamically based on seed and score
  const lineageData = apiData?.lineage || generateLineageFromSeed(seed, score);
  const flags = apiData?.flags?.length > 0 ? apiData.flags : generateFlagsFromSeed(seed, score, isAgri);
  const recommendations = apiData?.recommendations?.length > 0 ? apiData.recommendations : generateRecommendationsFromSeed(score, isAgri);
  const aiAnalysis = apiData?.aiAnalysis || generateAIAnalysisFromSeed(seed, score, isAgri, form);
  const familyTree = apiData?.familyTree || generateFamilyTreeFromSeed(seed, score);

  useEffect(() => { const t = setTimeout(()=>setScoreActive(true), 350); return ()=>clearTimeout(t); }, []);

  return (
    <div className="results-wrap">
      <div className="rc">
        <div className="rhead">
          <button className="bbtn" onClick={onBack}>← Back</button>
          <div className="propid">{propId}</div>
        </div>

        {/* Score card */}
        <div className="sh">
          <div className="cc tl"/><div className="cc tr"/><div className="cc bl"/><div className="cc br"/>
          <div className="slbl">Title Confidence Score</div>
          <ScoreCount target={score} active={scoreActive}/>
          <div className={`srisk ${risk.cls}`}>{risk.label}</div>
          <div className="smtr"><div className={`smtrf${scoreActive?' animate':''}`}/></div>
          <div className="smeta">Score / 1000 &nbsp;·&nbsp; Analyzed just now &nbsp;·&nbsp; {form.state || 'Karnataka'} Land Records</div>
          <div className="prop-meta-pills">
            {form.propType && <span className="pmp">{form.propType}</span>}
            {form.area && <span className="pmp">{form.area}</span>}
            {form.village && <span className="pmp">{form.village}</span>}
            {form.state && <span className="pmp">{form.state}</span>}
          </div>
        </div>

        {/* Ownership lineage */}
        <div className="rb">
          <div className="stripe sg"/>
          <div className="blbl">Ownership Lineage Reconstruction</div>
          <div className="tlw">
            {lineageData.map(({cls,lnClr,yr,nm,ty,last}, idx)=>(
              <div className={`ti${last?' ti-last':''}`} key={`${yr}-${idx}`}>
                <div className="tsp">
                  <div className={`tn ${cls}`}/>
                  {!last && <div className="tln" style={{background:lnClr}}/>}
                </div>
                <div className="tyr" style={last?{color:'rgba(196,97,74,.38)'}:{}}>{yr}</div>
                <div><div className="tnm">{nm}</div><div className="tty">{ty}</div></div>
              </div>
            ))}
          </div>
          <div className="ftr">
            <div className="ftr-r"><span className="ftr-k">Original Owner</span><span className="ftr-v">{familyTree.originalOwner}</span></div>
            <div className="ftr-r" style={{marginBottom:'.3rem'}}><span className="ftr-k">Legal Heirs</span></div>
            <div className="ftr-hs">
              {familyTree.heirs.map(({name,relation})=>(
                <div className="ftr-h" key={name}>{name}<span style={{opacity:.28,fontSize:'.7rem',marginLeft:'.4rem'}}>{relation}</span></div>
              ))}
            </div>
            <div className="ftr-w">{familyTree.partitionStatus}</div>
          </div>
        </div>

        {/* Risk flags */}
        <div className="rb" style={{animationDelay:'.05s'}}>
          <div className="stripe sg"/>
          <div className="blbl">Risk Flags Detected</div>
          <div className="flags">
            {flags.map(([k,v], idx)=>(
              <div className="flag" key={`${k}-${idx}`}>
                <div className="fi">!</div>
                <div className="ftxt"><strong>{k}</strong> {v}</div>
              </div>
            ))}
          </div>
        </div>

        {/* AI Legal Analysis */}
        <div className="rb" style={{animationDelay:'.1s'}}>
          <div className="stripe so"/>
          <div className="blbl">AI Legal Analysis</div>
          <div className="aip">
            {aiAnalysis}
          </div>
        </div>

        {/* Recommendations */}
        <div className="rb" style={{animationDelay:'.15s'}}>
          <div className="stripe sgr"/>
          <div className="blbl">Recommended Actions</div>
          <div className="recs">
            {recommendations.map((t, idx)=>(
              <div className="rec" key={`rec-${idx}`}>
                <div className="ri"/>
                <div className="rt">{t}</div>
              </div>
            ))}
          </div>
        </div>

        <div className="foot">Lineage <span>·</span> AI Title Intelligence <span>·</span> For Informational Use Only</div>
      </div>
    </div>
  );
}

// ── Root ───────────────────────────────────────────────────────────────────
export default function Lineage() {
  const [view, setView] = useState('landing');
  const [form, setForm] = useState(null);
  const [apiData, setApiData] = useState(null);
  const [loaderStep, setLoaderStep] = useState(STEPS[0]);
  const [navBg, setNavBg] = useState('rgba(20,17,14,0.6)');
  // eslint-disable-next-line no-unused-vars
  const [error, setError] = useState(null);

  useEffect(() => {
    const onScroll = () => setNavBg(window.scrollY > 50 ? 'rgba(14,11,9,0.92)' : 'rgba(20,17,14,0.6)');
    window.addEventListener('scroll', onScroll);
    return () => window.removeEventListener('scroll', onScroll);
  }, []);

  const handleAnalyze = useCallback(async (formData) => {
    setForm(formData);
    setView('loading');
    setError(null);
    setApiData(null);
    
    let si = 0;
    const iv = setInterval(() => { si=(si+1)%STEPS.length; setLoaderStep(STEPS[si]); }, 540);
    
    try {
      // Call the backend API
      const response = await analyzeProperty(formData);
      const transformedData = transformApiResponse(response);
      setApiData(transformedData);
      clearInterval(iv);
      window.scrollTo({top:0,behavior:'instant'});
      setView('results');
    } catch (err) {
      console.warn('API call failed, using fallback data:', err.message);
      // On error, still show results with default/synthetic data
      setApiData(null); // Will use default values in ResultsView
      clearInterval(iv);
      window.scrollTo({top:0,behavior:'instant'});
      setView('results');
    }
  }, []);

  const handleBack = useCallback(() => { 
    window.scrollTo({top:0,behavior:'instant'}); 
    setView('landing'); 
    setApiData(null);
    setError(null);
  }, []);
  
  const scrollTo = (id) => document.getElementById(id)?.scrollIntoView({behavior:'smooth'});

  const goHome = useCallback(() => {
    if (view !== 'landing') {
      window.scrollTo({top:0,behavior:'instant'});
      setView('landing');
      setApiData(null);
      setError(null);
    } else {
      document.getElementById('home')?.scrollIntoView({behavior:'smooth'});
    }
  }, [view]);

  return (
    <>
      <style>{CSS}</style>
      <div className="ll-root">
        <div className="scene"><div className="orb o1"/><div className="orb o2"/><div className="orb o3"/></div>
        <div className="gridlines"/>
        <Particles/>
        {view === 'loading' && <Loader step={loaderStep}/>}
        <nav style={{background:navBg}}>
          <div className="nav-logo">LandLedger<b>.</b></div>
          <div className="nav-links">
            <button className="nav-btn" onClick={goHome}>Home</button>
            <button className="nav-btn" onClick={()=>scrollTo('about')}>About</button>
            <button className="nav-btn nav-cta" onClick={()=>scrollTo('get-started')}>Get Started</button>
          </div>
        </nav>
        {view !== 'results' && <LandingView onAnalyze={handleAnalyze}/>}
        {view === 'results' && <ResultsView form={form} apiData={apiData} onBack={handleBack}/>}
      </div>
    </>
  );
}