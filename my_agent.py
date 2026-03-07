"""
PROMETHEUS AGENT v12.0 — Groq Edition
Single API key (Groq, free). No Gemini, no Pollinations.
Get your free key: https://console.groq.com/keys
"""
import os, sys, re, json, ast, time, subprocess, warnings
from pathlib import Path
from typing import Optional, List, Dict, Tuple
from datetime import datetime

warnings.filterwarnings("ignore")
import matplotlib; matplotlib.use("Agg")

try:
    from dotenv import load_dotenv; load_dotenv()
except ImportError: pass

try:
    from groq import Groq as _GroqSDK; _GROQ_OK = True
except ImportError:
    _GROQ_OK = False; print("[ERROR] pip install groq")

DDGS = None
try:
    from duckduckgo_search import DDGS
except ImportError: pass

try: import numpy as np
except ImportError: np = None
try:
    import matplotlib.pyplot as plt
    from matplotlib.gridspec import GridSpec
except ImportError: plt = None

for _d in ["outputs","built_agents","prometheus_memory","core_versions"]:
    Path(_d).mkdir(exist_ok=True)

_CODE_SYS = """You are PROMETHEUS, an elite Python coding AI.
Output COMPLETE RUNNABLE Python ONLY.
STRICT RULES:
- First line: a real import (e.g. import numpy as np)
- Matplotlib: import matplotlib; matplotlib.use('Agg')
- Save charts: plt.savefig('outputs/name.png',dpi=150,bbox_inches='tight'); plt.close()
- NEVER call plt.show()
- Print all key numbers and results
- NO markdown fences, NO explanations — pure Python
- Dark theme: facecolor='#0d1117', set_facecolor('#161b22'), tick colors '#9CA3AF'
"""
_PROSE_SYS = "You are PROMETHEUS AI. Give clear, factual, well-structured answers using markdown."


class ASCII:
    _MAP = {"θ":"theta","π":"pi","μ":"mu","σ":"sigma","Σ":"Sigma","Δ":"Delta",
        "α":"alpha","β":"beta","γ":"gamma","λ":"lambda","ω":"omega","φ":"phi",
        "∞":"inf","√":"sqrt","∫":"integral","≤":"<=","≥":">=","≠":"!=","≈":"~=",
        "×":"*","÷":"/","−":"-","±":"+/-","°":"deg","²":"^2","³":"^3",
        "'":"'","'":"'",'"':'"','"':'"',"–":"-","—":"--","…":"...",
        "\u00a0":" ","\u200b":""}
    @classmethod
    def clean(cls, t):
        if not t: return t
        for u,a in cls._MAP.items(): t=t.replace(u,a)
        return "".join(c if ord(c)<128 else "?" for c in t)
    @classmethod
    def clean_code(cls, code):
        code = cls.clean(code)
        code = re.sub(r"```(?:python)?\s*","",code)
        code = re.sub(r"```\s*$","",code,flags=re.MULTILINE)
        lines=code.split("\n")
        for i,line in enumerate(lines):
            s=line.strip()
            if any(re.match(p,s) for p in [r"^import ",r"^from ",r"^#",r"^def ",r"^class ",r"^if __name__"]):
                code="\n".join(lines[i:]); break
        if "import matplotlib" in code and "matplotlib.use" not in code:
            code=code.replace("import matplotlib","import matplotlib\nmatplotlib.use('Agg')")
        code=re.sub(r"plt\.show\s*\(\s*\)",
            "plt.savefig('outputs/plot_output.png',dpi=150,bbox_inches='tight'); plt.close()",code)
        return code.strip()


class GroqBrain:
    MODELS = {"code":"llama-3.3-70b-versatile","prose":"llama-3.1-8b-instant"}
    def __init__(self):
        self.client=None
        key=os.getenv("GROQ_KEY") or os.getenv("GROQ_API_KEY")
        if not key: print("[!] GROQ_KEY not set. Get it free at console.groq.com/keys"); return
        if not _GROQ_OK: print("[!] pip install groq"); return
        self.client=_GroqSDK(api_key=key)
        print(f"[OK] Groq → {self.MODELS['code']}")
    @property
    def available(self): return self.client is not None
    def think(self, prompt, temp=0.2, mode="code"):
        if not self.client: return None
        model=self.MODELS.get(mode,self.MODELS["code"])
        system=_PROSE_SYS if mode=="prose" else _CODE_SYS
        try:
            print(f"[GROQ] {'Thinking' if mode=='prose' else 'Coding'} ({model})")
            r=self.client.chat.completions.create(
                model=model,
                messages=[{"role":"system","content":system},{"role":"user","content":ASCII.clean(prompt)}],
                temperature=float(min(temp,1.0)),max_tokens=6000)
            raw=r.choices[0].message.content
            return raw if mode=="prose" else ASCII.clean_code(raw)
        except Exception as e:
            print(f"[GROQ] Error: {e}")
            if "rate" in str(e).lower() and mode=="code":
                time.sleep(4)
                try:
                    r2=self.client.chat.completions.create(
                        model=self.MODELS["prose"],
                        messages=[{"role":"system","content":system},{"role":"user","content":ASCII.clean(prompt)}],
                        temperature=float(min(temp,1.0)),max_tokens=4000)
                    return ASCII.clean_code(r2.choices[0].message.content)
                except: pass
            return None


class WebResearch:
    def search(self, query, n=5):
        if not DDGS: return "[pip install duckduckgo-search for web search]"
        try:
            results=[]
            with DDGS() as d:
                for r in d.text(ASCII.clean(query),max_results=n):
                    results.append(f"- {r.get('title','')}: {r.get('body','')[:200]}")
            return "\n".join(results) or "No results."
        except Exception as e: return f"Search error: {e}"
    def deep_research(self, question, brain):
        print(f"[RESEARCH] {question}")
        ctx=self.search(question,4)+"\n\n"+self.search(f"{question} 2024 2025",3)
        prompt=(f"QUESTION: {question}\n\nSEARCH RESULTS:\n{ctx}\n\n"
                "Give a comprehensive, well-structured answer with key facts and confidence level.")
        return brain.think(prompt,temp=0.3,mode="prose") or f"Could not research: {question}"


class Executor:
    TIMEOUT=90
    def run(self, code):
        tmp=Path("outputs/_tmp.py")
        try:
            tmp.write_text(code,encoding="utf-8",errors="replace")
            r=subprocess.run([sys.executable,str(tmp)],capture_output=True,text=True,
                timeout=self.TIMEOUT,cwd=str(Path.cwd()),env={**os.environ,"MPLBACKEND":"Agg"})
            return r.returncode==0,(r.stdout+r.stderr).strip()
        except subprocess.TimeoutExpired: return False,f"[TIMEOUT] {self.TIMEOUT}s"
        except Exception as e: return False,f"[EXEC ERROR] {e}"
        finally:
            try: tmp.unlink()
            except: pass


class Memory:
    FILE=Path("prometheus_memory/solutions.json")
    def __init__(self):
        self.data={}
        if self.FILE.exists():
            try: self.data=json.loads(self.FILE.read_text(encoding="utf-8")); print(f"[MEM] {len(self.data)} cached")
            except: pass
    def _key(self,g): return re.sub(r"\W+","_",g.lower())[:60]
    def get(self,g):
        k=self._key(g)
        if k in self.data: print(f"[MEM] Hit: {k}"); return self.data[k]["code"]
        return None
    def store(self,g,code,out):
        self.data[self._key(g)]={"goal":g,"code":code,"output":out[:400],"ts":str(datetime.now())}
        try: self.FILE.write_text(json.dumps(self.data,indent=2),encoding="utf-8")
        except: pass
    def stats(self): return f"{len(self.data)} cached"


class Templates:
    @staticmethod
    def monte_carlo(goal):
        return r'''
import numpy as np
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from pathlib import Path
Path("outputs").mkdir(exist_ok=True)
np.random.seed(42)
N=50000;initial=10000;mu=0.08;sigma=0.20;years=10
results=np.array([initial*np.prod(1+np.random.normal(mu,sigma,years)) for _ in range(N)])
p5,p50,p95=np.percentile(results,[5,50,95])
print(f"Monte Carlo Simulation — {N:,} paths | {years} years")
print(f"  5th  pct (bad):    ${p5:>12,.0f}")
print(f"  50th pct (median): ${p50:>12,.0f}")
print(f"  95th pct (good):   ${p95:>12,.0f}")
print(f"  P(double money):   {(results>initial*2).mean()*100:.1f}%")
print(f"  P(loss):           {(results<initial).mean()*100:.1f}%")
fig=plt.figure(figsize=(14,6),facecolor="#0d1117");gs=GridSpec(1,2,figure=fig,wspace=0.35)
ax1=fig.add_subplot(gs[0]);ax1.set_facecolor("#161b22")
ax1.hist(results/1000,bins=90,color="#0085FF",alpha=0.85,edgecolor="none")
for v,c,l in [(p5,"#EF4444","5th"),(p50,"#10B981","Median"),(p95,"#F59E0B","95th")]:
    ax1.axvline(v/1000,color=c,lw=2.5,linestyle="--",label=f"{l}: ${v/1000:.0f}k")
ax1.set_xlabel("Final Value ($k)",color="#9CA3AF");ax1.set_ylabel("Frequency",color="#9CA3AF")
ax1.set_title("Distribution of Outcomes",color="white",fontweight="bold")
ax1.tick_params(colors="#9CA3AF");ax1.spines[:].set_color("#21262d")
ax1.legend(facecolor="#21262d",labelcolor="white")
ax2=fig.add_subplot(gs[1]);ax2.set_facecolor("#161b22")
yr=np.arange(years+1)
for _ in range(200):
    path=[initial];[path.append(path[-1]*(1+np.random.normal(mu,sigma))) for _ in range(years)]
    ax2.plot(yr,np.array(path)/1000,color="#0085FF",alpha=0.035,lw=0.8)
ax2.plot(yr,[initial*(1+mu)**y/1000 for y in yr],color="#10B981",lw=2.5,label="Expected")
ax2.set_xlabel("Year",color="#9CA3AF");ax2.set_ylabel("Value ($k)",color="#9CA3AF")
ax2.set_title("Simulation Paths",color="white",fontweight="bold")
ax2.tick_params(colors="#9CA3AF");ax2.spines[:].set_color("#21262d")
ax2.legend(facecolor="#21262d",labelcolor="white")
fig.suptitle("PROMETHEUS — Monte Carlo Portfolio Simulation",color="white",fontsize=13,fontweight="bold")
plt.savefig("outputs/monte_carlo.png",dpi=150,bbox_inches="tight",facecolor="#0d1117");plt.close()
print("\n[OK] outputs/monte_carlo.png")
'''

    @staticmethod
    def fibonacci(goal):
        return r'''
import numpy as np
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from pathlib import Path
Path("outputs").mkdir(exist_ok=True)
fibs=[0,1]
for _ in range(18): fibs.append(fibs[-1]+fibs[-2])
ratios=[fibs[i+1]/fibs[i] for i in range(1,len(fibs)-1)]
phi=(1+5**0.5)/2
print("Fibonacci Sequence");print("-"*30)
for i,f in enumerate(fibs): print(f"  F({i:2d}) = {f:>10,}")
print(f"\nGolden Ratio phi = {phi:.10f}")
print(f"F(19)/F(18)      = {fibs[-1]/fibs[-2]:.10f}")
print(f"Convergence err  = {abs(ratios[-1]-phi):.2e}")
fig,(ax1,ax2)=plt.subplots(1,2,figsize=(13,5),facecolor="#0d1117")
for ax in [ax1,ax2]: ax.set_facecolor("#161b22");ax.tick_params(colors="#9CA3AF");ax.spines[:].set_color("#21262d")
ax1.bar(range(len(fibs)),fibs,color="#009EFF",alpha=0.85,width=0.7,edgecolor="none")
ax1.set_title("Fibonacci Numbers",color="white",fontweight="bold")
ax1.set_xlabel("n",color="#9CA3AF");ax1.set_ylabel("F(n)",color="#9CA3AF")
ax2.plot(range(1,len(ratios)+1),ratios,"o-",color="#009EFF",lw=2,ms=6,markerfacecolor="white")
ax2.axhline(phi,color="#9360FF",lw=2.5,linestyle="--",label=f"phi={phi:.5f}")
ax2.set_title("Convergence to Golden Ratio",color="white",fontweight="bold")
ax2.set_xlabel("n",color="#9CA3AF");ax2.set_ylabel("F(n+1)/F(n)",color="#9CA3AF")
ax2.legend(facecolor="#21262d",labelcolor="white")
fig.suptitle("PROMETHEUS — Fibonacci & Golden Ratio",color="white",fontsize=13,fontweight="bold")
plt.tight_layout()
plt.savefig("outputs/fibonacci.png",dpi=150,bbox_inches="tight",facecolor="#0d1117");plt.close()
print("\n[OK] outputs/fibonacci.png")
'''

    @staticmethod
    def physics(goal):
        return r'''
import numpy as np
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from pathlib import Path
Path("outputs").mkdir(exist_ok=True)
g=9.81;v0=50.0;ang=np.radians(45);h0=10.0
vx=v0*np.cos(ang);vy0=v0*np.sin(ang)
t_land=(vy0+np.sqrt(vy0**2+2*g*h0))/g
t=np.linspace(0,t_land,600)
x=vx*t;y=h0+vy0*t-0.5*g*t**2
speed=np.sqrt(vx**2+(vy0-g*t)**2)
t_peak=vy0/g;h_peak=h0+vy0**2/(2*g)
print(f"Projectile Motion | v0=50m/s @ 45deg | h0=10m")
print(f"  Peak height: {h_peak:.3f} m at t={t_peak:.3f} s")
print(f"  Range:       {x[-1]:.3f} m")
print(f"  Flight time: {t_land:.3f} s")
print(f"  Impact speed:{speed[-1]:.3f} m/s")
fig,(ax1,ax2)=plt.subplots(1,2,figsize=(13,5),facecolor="#0d1117")
for ax in [ax1,ax2]: ax.set_facecolor("#161b22");ax.tick_params(colors="#9CA3AF");ax.spines[:].set_color("#21262d")
ax1.plot(x,y,color="#009EFF",lw=2.5)
ax1.fill_between(x,0,np.clip(y,0,None),alpha=0.08,color="#009EFF")
ax1.plot(x[np.argmax(y)],np.max(y),"o",color="#F59E0B",ms=10,label=f"Peak {h_peak:.1f}m",zorder=5)
ax1.plot(x[-1],0,"o",color="#EF4444",ms=10,label=f"Land {x[-1]:.1f}m",zorder=5)
ax1.axhline(0,color="#30363d",lw=0.8);ax1.set_ylim(bottom=-2)
ax1.set_xlabel("Distance (m)",color="#9CA3AF");ax1.set_ylabel("Height (m)",color="#9CA3AF")
ax1.set_title("Projectile Trajectory",color="white",fontweight="bold")
ax1.legend(facecolor="#21262d",labelcolor="white")
ax2.plot(t,speed,color="#9360FF",lw=2.5,label="Speed")
ax2.plot(t,np.abs(vy0-g*t),color="#10B981",lw=1.8,linestyle="--",label="|vy|")
ax2.set_xlabel("Time (s)",color="#9CA3AF");ax2.set_ylabel("Speed (m/s)",color="#9CA3AF")
ax2.set_title("Speed over Time",color="white",fontweight="bold")
ax2.legend(facecolor="#21262d",labelcolor="white")
fig.suptitle("PROMETHEUS — Projectile Motion",color="white",fontsize=13,fontweight="bold")
plt.tight_layout()
plt.savefig("outputs/physics.png",dpi=150,bbox_inches="tight",facecolor="#0d1117");plt.close()
print("\n[OK] outputs/physics.png")
'''

    @staticmethod
    def compound(goal):
        return r'''
import numpy as np
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from pathlib import Path
Path("outputs").mkdir(exist_ok=True)
p=10000;r=0.07;yrs=30;m=200
months=np.arange(yrs*12+1);bal=np.zeros(len(months));bal[0]=p
for i in range(1,len(months)): bal[i]=bal[i-1]*(1+r/12)+m
tc=p+m*(len(months)-1);final=bal[-1]
print(f"Compound Interest | ${p:,} + ${m}/mo | {r*100:.0f}% | {yrs}yr")
print(f"  Total contributed: ${tc:>12,.2f}")
print(f"  Final balance:     ${final:>12,.2f}")
print(f"  Interest earned:   ${final-tc:>12,.2f}")
print(f"  Return multiple:   {final/tc:.2f}x")
yr_idx=np.arange(0,yrs+1)*12;yr_bal=bal[yr_idx];contrib=p+m*yr_idx
fig,ax=plt.subplots(figsize=(12,6),facecolor="#0d1117");ax.set_facecolor("#161b22")
ax.fill_between(range(yrs+1),0,contrib/1000,alpha=0.5,color="#9360FF",label="Contributions")
ax.fill_between(range(yrs+1),contrib/1000,yr_bal/1000,alpha=0.4,color="#009EFF",label="Interest")
ax.plot(range(yrs+1),yr_bal/1000,color="#009EFF",lw=2.5,label=f"Balance (${final/1000:.0f}k)")
ax.set_xlabel("Year",color="#9CA3AF");ax.set_ylabel("Balance ($k)",color="#9CA3AF")
ax.set_title("PROMETHEUS — Compound Interest Growth",color="white",fontweight="bold")
ax.tick_params(colors="#9CA3AF");ax.spines[:].set_color("#21262d")
ax.legend(facecolor="#21262d",labelcolor="white");ax.grid(True,color="#21262d",alpha=0.5)
plt.savefig("outputs/compound.png",dpi=150,bbox_inches="tight",facecolor="#0d1117");plt.close()
print("\n[OK] outputs/compound.png")
'''


_DOMAINS = {
    "monte_carlo":["monte carlo","simulation","stochastic","random walk","portfolio sim"],
    "fibonacci":  ["fibonacci","golden ratio","fib"],
    "physics":    ["projectile","trajectory","gravity","force","pendulum","orbit","mechanics"],
    "compound":   ["compound interest","compounding","investment growth","savings"],
    "research":   ["what is","explain","latest","history of","how does"],
}

def classify(goal):
    g=goal.lower()
    for d,kw in _DOMAINS.items():
        if any(k in g for k in kw): return d
    return "general"


class PrometheusAgent:
    def __init__(self):
        self.brain=GroqBrain();self.web=WebResearch()
        self.executor=Executor();self.memory=Memory()
        if not self.brain.available:
            print("\n[!] Groq not available.\n  1. Get FREE key: console.groq.com/keys\n  2. Add to .env: GROQ_KEY=gsk_xxx\n")

    def _generate(self, goal, task, errors=None, temp=0.2):
        tmap={"monte_carlo":Templates.monte_carlo,"fibonacci":Templates.fibonacci,
              "physics":Templates.physics,"compound":Templates.compound}
        if task in tmap: print(f"[TEMPLATE] {task}"); return tmap[task](goal)
        err_ctx=("Errors to avoid:\n"+"\n".join(errors[-2:])+"\n\n") if errors else ""
        return self.brain.think(
            f"Task: {goal}\n\n{err_ctx}Write complete Python. numpy+matplotlib dark theme. "
            "Save chart to outputs/. Print results. No markdown.",temp=temp,mode="code")

    def execute(self, goal, max_retries=3):
        print(f"\n[TASK] {goal}\n"+"─"*60)
        task=classify(goal); print(f"[TYPE] {task}")
        code=self.memory.get(goal) or self._generate(goal,task)
        if not code: print("[ERROR] Generation failed"); return False
        errors=[]
        for attempt in range(max_retries):
            print(f"\n[EXEC] Attempt {attempt+1}/{max_retries}")
            code=_clean_code(code)
            ok,output=self.executor.run(code)
            if ok:
                print(f"[SUCCESS]\n{output[:2000]}")
                imgs=sorted(Path("outputs").glob("*.png"))
                if imgs: print(f"[IMAGES] {[i.name for i in imgs[-4:]]}")
                self.memory.store(goal,code,output); return True
            print(f"[FAILED] {output[:400]}"); errors.append(output[:200])
            if attempt<max_retries-1:
                print("[REPAIR] Asking Groq...")
                fix=self.brain.think(
                    f"Fix Python error:\n{output[:500]}\nGoal:{goal}\nCode:\n{code[:2000]}\n"
                    "Return ONLY complete fixed Python. No markdown.",temp=0.1,mode="code")
                if fix: code=fix
                else: code=self._generate(goal,task,errors,temp=0.4) or code
        print(f"[FAILED] {max_retries} attempts"); return False

    def research_mode(self, question):
        print(f"\n[RESEARCH] {question}\n"+"─"*60)
        answer=self.web.deep_research(question,self.brain)
        ts=datetime.now().strftime("%Y%m%d_%H%M%S")
        try: (Path("outputs")/f"research_{ts}.txt").write_text(f"Q: {question}\n\n{answer}",encoding="utf-8")
        except: pass
        print(f"\n{answer}"); return answer

    def build(self, purpose):
        print(f"\n[BUILDER] {purpose}")
        code=self.brain.think(
            f"Write complete standalone Python agent for: {purpose}\n"
            "All imports inside. Save output to outputs/agent_output.png. "
            "Print results. Has main() function. NO markdown.",temp=0.4,mode="code")
        if not code: return None
        try: ast.parse(code)
        except SyntaxError as e:
            fixed=self.brain.think(f"Fix syntax error: {e}\n\n{code}",temp=0.1,mode="code")
            if fixed:
                try: ast.parse(fixed); code=fixed
                except: return None
            else: return None
        safe=re.sub(r"[^a-z0-9_]","_",purpose.lower())[:40]
        ts=datetime.now().strftime("%Y%m%d_%H%M%S")
        path=Path("built_agents")/f"agent_{safe}_{ts}.py"
        path.write_text(code,encoding="utf-8",errors="replace")
        print(f"[BUILDER] Saved: {path}"); return path

    def interactive(self):
        print("\n"+"="*55+"\n  PROMETHEUS AI — Interactive (Groq Llama 3.3 70B)\n"
              "  Commands: /research <q>  /build <p>  /stats  /quit\n"+"="*55+"\n")
        while True:
            try:
                u=input(">>> ").strip()
                if not u: continue
                if u.lower() in ("/quit","quit","exit","q"): break
                elif u.startswith("/research "): self.research_mode(u[10:])
                elif u.startswith("/build "): self.build(u[7:])
                elif u=="/stats": print(f"[STATS] {self.memory.stats()}")
                else: self.execute(u)
            except KeyboardInterrupt: print("\nGoodbye!"); break
            except Exception as e: print(f"[ERROR] {e}")


def _clean_code(code):
    """Alias for ASCII.clean_code for backward compat"""
    return ASCII.clean_code(code)


if __name__=="__main__":
    import argparse
    ap=argparse.ArgumentParser(description="PROMETHEUS AI v12.0")
    ap.add_argument("--goal",type=str); ap.add_argument("--research",type=str)
    ap.add_argument("--build",type=str); ap.add_argument("-i","--interactive",action="store_true")
    args=ap.parse_args()
    agent=PrometheusAgent()
    if args.interactive: agent.interactive()
    elif args.goal: agent.execute(args.goal)
    elif args.research: agent.research_mode(args.research)
    elif args.build: agent.build(args.build)
    else:
        print("[DEMO] Running default task...")
        agent.execute("Monte Carlo simulation of $10,000 portfolio over 10 years")
